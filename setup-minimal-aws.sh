#!/bin/bash

# Minimal AWS Setup for World Immigration Consultant
# This script creates basic AWS resources with minimal permissions required

set -e

REGION="us-east-1"
CLUSTER_NAME="worldimmigration-cluster"
ECR_REPO="worldimmigration-backend"

echo "🏗️ Setting up minimal AWS infrastructure..."

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "Unknown")
echo "AWS Account ID: $ACCOUNT_ID"

echo "📦 Creating ECR repository..."
aws ecr create-repository \
    --repository-name $ECR_REPO \
    --region $REGION \
    --image-scanning-configuration scanOnPush=true \
    2>/dev/null || echo "✅ ECR repository already exists"

echo "📝 Creating CloudWatch log group..."
aws logs create-log-group \
    --log-group-name "/ecs/worldimmigration-backend" \
    --region $REGION \
    2>/dev/null || echo "✅ Log group already exists"

echo "🏢 Creating ECS cluster..."
aws ecs create-cluster \
    --cluster-name $CLUSTER_NAME \
    --capacity-providers FARGATE \
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
    2>/dev/null || echo "✅ ECS cluster already exists"

echo "📄 Creating minimal task definition (without VPC specifics)..."

# Create a minimal task definition
cat > aws-task-definition-minimal.json << EOF
{
  "family": "worldimmigration-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "worldimmigration-backend",
      "image": "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/worldimmigration-backend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/worldimmigration-backend",
          "awslogs-region": "$REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "ENV",
          "value": "production"
        }
      ]
    }
  ]
}
EOF

echo "✅ Minimal AWS infrastructure setup complete!"
echo ""
echo "📋 Summary:"
echo "- AWS Account: $ACCOUNT_ID"
echo "- ECS Cluster: $CLUSTER_NAME"
echo "- ECR Repository: $ECR_REPO"
echo "- Task Definition: aws-task-definition-minimal.json"
echo ""
echo "⚠️ Note: This setup uses minimal permissions and doesn't include load balancer."
echo "🚀 Ready for deployment! Run ./deploy-minimal-aws.sh to deploy your backend." 