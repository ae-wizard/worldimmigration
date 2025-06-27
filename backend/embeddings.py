# embeddings.py
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import os
from scraper import load_scraped_content, scrape_immigration_content, save_scraped_content

# Initialize embedding model and Qdrant client
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_qdrant_client(url: str = None) -> QdrantClient:
    """Get Qdrant client with environment-based URL"""
    if url is None:
        url = os.getenv("QDRANT_URL", "http://localhost:6333")
    return QdrantClient(url=url)

def ensure_collection(collection_name: str = "immigration_docs", vector_dim: int = 384):
    """Ensure the collection exists, creating it if necessary"""
    qdrant = get_qdrant_client()
    
    try:
        # Try to get collection info
        collection_info = qdrant.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists with {collection_info.points_count} points")
    except Exception:
        # Collection doesn't exist, create it
        print(f"Creating collection '{collection_name}'...")
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
        )
        print(f"Collection '{collection_name}' created successfully")

def index_documents(chunks: List[Dict[str, str]], collection_name: str = "immigration_docs", batch_size: int = 100):
    """Embed a list of text chunks and upsert into Qdrant."""
    if not chunks:
        print("No chunks to index")
        return
    
    qdrant = get_qdrant_client()
    
    # Ensure collection exists
    ensure_collection(collection_name)
    
    print(f"Indexing {len(chunks)} chunks into Qdrant...")
    
    # Process in batches to avoid memory issues
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_texts = [chunk["text"] for chunk in batch]
        
        print(f"Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
        
        # Generate embeddings for the batch
        try:
            vectors = embed_model.encode(batch_texts, show_progress_bar=True)
        except Exception as e:
            print(f"Error generating embeddings for batch: {e}")
            continue
        
        # Prepare points for Qdrant
        points = []
        for idx, (chunk, vector) in enumerate(zip(batch, vectors)):
            point_id = i + idx  # Global point ID
            payload = {
                "text": chunk["text"],
                "source_url": chunk.get("source_url", ""),
                "chunk_id": chunk.get("chunk_id", f"chunk_{point_id}"),
                "source_type": chunk.get("source_type", "unknown")
            }
            
            points.append(PointStruct(
                id=point_id, 
                vector=vector.tolist(), 
                payload=payload
            ))
        
        # Upsert points in Qdrant
        try:
            qdrant.upsert(collection_name=collection_name, points=points)
            print(f"  -> Indexed {len(points)} points")
        except Exception as e:
            print(f"Error upserting batch to Qdrant: {e}")
            continue
    
    # Get final collection stats
    try:
        collection_info = qdrant.get_collection(collection_name)
        print(f"Indexing complete! Collection now has {collection_info.points_count} total points")
    except Exception as e:
        print(f"Error getting collection info: {e}")

def search_similar(query: str, collection_name: str = "immigration_docs", limit: int = 5) -> List[Dict]:
    """Search for similar documents given a query"""
    qdrant = get_qdrant_client()
    
    try:
        # Embed the query
        query_vector = embed_model.encode(query).tolist()
        
        # Search in Qdrant
        results = qdrant.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result.payload.get("text", ""),
                "score": result.score,
                "source_url": result.payload.get("source_url", ""),
                "chunk_id": result.payload.get("chunk_id", ""),
                "source_type": result.payload.get("source_type", "")
            })
        
        return formatted_results
        
    except Exception as e:
        print(f"Error searching: {e}")
        return []

def get_collection_stats(collection_name: str = "immigration_docs") -> Dict:
    """Get statistics about the collection"""
    qdrant = get_qdrant_client()
    
    try:
        collection_info = qdrant.get_collection(collection_name)
        return {
            "points_count": collection_info.points_count,
            "status": collection_info.status,
            "optimizer_status": collection_info.optimizer_status,
            "vectors_count": collection_info.vectors_count
        }
    except Exception as e:
        print(f"Error getting collection stats: {e}")
        return {"error": str(e)}

def reset_collection(collection_name: str = "immigration_docs"):
    """Delete and recreate the collection (warning: removes all data!)"""
    qdrant = get_qdrant_client()
    
    try:
        print(f"Deleting collection '{collection_name}'...")
        qdrant.delete_collection(collection_name)
        print(f"Recreating collection '{collection_name}'...")
        ensure_collection(collection_name)
        print("Collection reset complete")
    except Exception as e:
        print(f"Error resetting collection: {e}")

def main():
    """Main function to scrape content and index it"""
    print("Immigration Content Indexing Pipeline")
    print("=====================================")
    
    # Check if we have existing content
    existing_content = load_scraped_content()
    
    if not existing_content:
        print("No existing scraped content found. Starting scraping...")
        content = scrape_immigration_content()
        save_scraped_content(content)
    else:
        print(f"Found {len(existing_content)} existing content pieces")
        choice = input("Re-scrape content? (y/N): ").lower().strip()
        if choice == 'y':
            content = scrape_immigration_content()
            save_scraped_content(content)
        else:
            content = existing_content
    
    if not content:
        print("No content to index. Exiting.")
        return
    
    # Check collection status
    stats = get_collection_stats()
    if "points_count" in stats and stats["points_count"] > 0:
        print(f"Collection already has {stats['points_count']} points")
        choice = input("Reset and re-index? (y/N): ").lower().strip()
        if choice == 'y':
            reset_collection()
        else:
            print("Using existing index")
            return
    
    # Index the content
    index_documents(content)
    
    # Test search
    print("\nTesting search functionality...")
    test_query = "How to apply for naturalization?"
    results = search_similar(test_query, limit=3)
    
    print(f"\nTest query: '{test_query}'")
    print("Top results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   Source: {result['source_url']}")
        print(f"   Text: {result['text'][:150]}...")
        print()

if __name__ == "__main__":
    main() 