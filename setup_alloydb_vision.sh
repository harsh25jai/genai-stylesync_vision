#!/bin/bash
# StyleSync Vision - Submission 3: Persistent Wardrobe Setup

PROJECT_ID=$1
REGION=$2
PASSWORD=$3
CLUSTER_ID="stylesync-cluster"
INSTANCE_ID="stylesync-primary"
VPC_NAME="stylesync-vpc"
PSA_RANGE_NAME="stylesync-psa-range"

# Check if arguments are missing
if [ -z "$PROJECT_ID" ] || [ -z "$REGION" ] || [ -z "$PASSWORD" ]; then
    echo "❌ ERROR: Missing arguments."
    echo "Usage: bash cleanup_alloydb.sh [PROJECT_ID] [REGION]"
    exit 1
fi

echo "🚀 Starting StyleSync AlloyDB Deployment..."

# 1. Enable Required AI & DB APIs
gcloud services enable \
    alloydb.googleapis.com \
    servicenetworking.googleapis.com \
    aiplatform.googleapis.com \
    compute.googleapis.com

# 2. Networking (Simplified check)
if ! gcloud compute networks describe $VPC_NAME --global > /dev/null 2>&1; then
    gcloud compute networks create $VPC_NAME --subnet-mode=custom
    gcloud compute addresses create $PSA_RANGE_NAME --global --purpose=VPC_PEERING --prefix-length=16 --network=$VPC_NAME
    gcloud services vpc-peerings connect --service=servicenetworking.googleapis.com --ranges=$PSA_RANGE_NAME --network=$VPC_NAME
fi

# 3. Create Cluster with Continuous Backup (Important for "Persistence")
if ! gcloud alloydb clusters describe $CLUSTER_ID --region=$REGION > /dev/null 2>&1; then
    echo "🏗️ Creating AlloyDB Cluster..."
    gcloud alloydb clusters create $CLUSTER_ID \
        --region=$REGION \
        --network=$VPC_NAME \
        --password=$PASSWORD
fi

# 4. Create Instance with AI Enabled
if ! gcloud alloydb instances describe $INSTANCE_ID --cluster=$CLUSTER_ID --region=$REGION > /dev/null 2>&1; then
    echo "💎 Creating AlloyDB Primary Instance..."
    gcloud alloydb instances create $INSTANCE_ID \
        --cluster=$CLUSTER_ID \
        --region=$REGION \
        --cpu-count=2 \
        --instance-type=PRIMARY \
        --database-flags=google_columnar_engine.enabled=on
fi

# 5. Create Cluster
if ! gcloud alloydb clusters describe $CLUSTER_ID --region=$REGION > /dev/null 2>&1; then
    echo "🏗️ Creating AlloyDB Cluster $CLUSTER_ID in region $REGION..."
    # Explicitly using the --region flag is mandatory
    gcloud alloydb clusters create $CLUSTER_ID \
        --region=$REGION \
        --network=$VPC_NAME \
        --password=$PASSWORD \
else
    echo "AlloyDB Cluster $CLUSTER_ID already exists. Skipping."
fi

sleep 10

# 6. Create Instance
if ! gcloud alloydb instances describe $INSTANCE_ID --cluster=$CLUSTER_ID --region=$REGION > /dev/null 2>&1; then
    echo "💎 Creating AlloyDB Primary Instance $INSTANCE_ID..."
    # Note: --cluster and --region are both required for instances
    gcloud alloydb instances create $INSTANCE_ID \
        --cluster=$CLUSTER_ID \
        --region=$REGION \
        --cpu-count=2 \
        --instance-type=PRIMARY
else
    echo "AlloyDB Instance $INSTANCE_ID already exists. Skipping."
fi

echo "✅ Infrastructure Ready. Please run the SQL initialization next."