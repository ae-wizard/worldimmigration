#!/bin/bash

# Minimal AWS Deployment Script for World Immigration Consultant
# This script deploys using minimal AWS permissions

set -e

# Configuration
REGION="us-east-1"
CLUSTER_NAME="worldimmigration-cluster"
TASK_DEFINITION="worldimmigration-backend"
ECR_REPO="worldimmigration-backend"

echo "🚀 Starting minimal deployment to AWS ECS..."

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $ACCOUNT_ID"

echo "📦 Building and pushing Docker image..."

# Build Docker image
cd backend
docker build -t $ECR_REPO .

# Tag for ECR
docker tag $ECR_REPO:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Push to ECR
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

cd ..

echo "🏗️ Registering task definition..."

# Register new task definition using minimal version
TASK_DEFINITION_ARN=$(aws ecs register-task-definition \
    --cli-input-json file://aws-task-definition-minimal.json \
    --query taskDefinition.taskDefinitionArn --output text)

echo "New task definition: $TASK_DEFINITION_ARN"

echo "🚀 Running task on ECS..."

# Run a task instead of creating a service (requires fewer permissions)
TASK_ARN=$(aws ecs run-task \
    --cluster $CLUSTER_NAME \
    --task-definition $TASK_DEFINITION \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={assignPublicIp=ENABLED}" \
    --query 'tasks[0].taskArn' --output text)

echo "Task started: $TASK_ARN"

echo "⏳ Waiting for task to start..."
sleep 30

# Get task status
TASK_STATUS=$(aws ecs describe-tasks \
    --cluster $CLUSTER_NAME \
    --tasks $TASK_ARN \
    --query 'tasks[0].lastStatus' --output text)

echo "Task status: $TASK_STATUS"

if [ "$TASK_STATUS" = "RUNNING" ]; then
    # Get task IP
    TASK_IP=$(aws ecs describe-tasks \
        --cluster $CLUSTER_NAME \
        --tasks $TASK_ARN \
        --query 'tasks[0].attachments[0].details[?name==`privateIPv4Address`].value' \
        --output text)
    
    echo "🎉 Task is running!"
    echo "📍 Private IP: $TASK_IP"
    echo "⚠️ Note: Since this uses private IP only, you'll need to set up networking for external access."
    echo "🔍 Check logs: aws logs tail /ecs/worldimmigration-backend --follow"
else
    echo "❌ Task failed to start. Check CloudWatch logs for details:"
    echo "aws logs tail /ecs/worldimmigration-backend --follow"
fi

echo "✅ Minimal deployment complete!"

# Show next steps
echo ""
echo "📋 Next Steps:"
echo "1. Check logs: aws logs tail /ecs/worldimmigration-backend --follow"
echo "2. For external access, you'll need to set up AWS networking (VPC, security groups, load balancer)"
echo "3. Consider upgrading AWS IAM permissions for full functionality" 