# db.py
import sqlite3
import threading
from datetime import datetime

DB_PATH = "conversation_logs.db"

# Thread lock for database operations
db_lock = threading.Lock()

def get_connection():
    """Get a database connection with thread safety"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn

def init_db():
    """Initialize database tables"""
    with db_lock:
        conn = get_connection()
        try:
            # Create conversations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_question TEXT NOT NULL,
                    assistant_answer TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create leads table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    country TEXT,
                    intent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            conn.close()

def log_conversation(user_question: str, assistant_answer: str):
    """Log a completed QA pair to the database"""
    with db_lock:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO conversations (user_question, assistant_answer) VALUES (?, ?)",
                (user_question, assistant_answer)
            )
            conn.commit()
            print(f"Logged conversation: {user_question[:50]}...")
        except Exception as e:
            print(f"Error logging conversation: {e}")
        finally:
            conn.close()

def create_lead(email: str, country: str, intent: str):
    """Store lead information in the database"""
    with db_lock:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO leads (email, country, intent) VALUES (?, ?, ?)",
                (email, country, intent)
            )
            conn.commit()
            print(f"Created lead: {email}")
        except Exception as e:
            print(f"Error creating lead: {e}")
            raise e
        finally:
            conn.close()

def save_lead(email: str, phone: str = None, country: str = None, goal: str = None, timeline: str = None, additional_info: str = None):
    """Store comprehensive lead information in the database"""
    with db_lock:
        conn = get_connection()
        try:
            # First, let's update the leads table schema if needed
            try:
                conn.execute("ALTER TABLE leads ADD COLUMN phone TEXT")
                conn.execute("ALTER TABLE leads ADD COLUMN goal TEXT") 
                conn.execute("ALTER TABLE leads ADD COLUMN timeline TEXT")
                conn.execute("ALTER TABLE leads ADD COLUMN additional_info TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                # Columns already exist
                pass
            
            # Insert the lead
            cursor = conn.execute(
                """INSERT INTO leads (email, country, intent, phone, goal, timeline, additional_info) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (email, country, goal, phone, goal, timeline, additional_info)
            )
            conn.commit()
            lead_id = cursor.lastrowid
            print(f"Saved lead: {email} (ID: {lead_id})")
            return lead_id
        except Exception as e:
            print(f"Error saving lead: {e}")
            raise e
        finally:
            conn.close()

def get_conversations(limit: int = 100):
    """Retrieve recent conversations"""
    with db_lock:
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            conversations = [dict(row) for row in cursor.fetchall()]
            return conversations
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            return []
        finally:
            conn.close()

def get_leads(limit: int = 100):
    """Retrieve recent leads"""
    with db_lock:
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM leads ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            leads = [dict(row) for row in cursor.fetchall()]
            return leads
        except Exception as e:
            print(f"Error retrieving leads: {e}")
            return []
        finally:
            conn.close() 