#!/bin/bash
# StyleSync Vision - Submission 3: AlloyDB & Networking Cleanup Script

# Capture arguments
PROJECT_ID=$1
REGION=$2

# Check if arguments are missing
if [ -z "$PROJECT_ID" ] || [ -z "$REGION" ]; then
    echo "❌ ERROR: Missing arguments."
    echo "Usage: bash cleanup_alloydb.sh [PROJECT_ID] [REGION]"
    exit 1
fi

CLUSTER_ID="stylesync-cluster"
INSTANCE_ID="stylesync-primary"
VPC_NAME="stylesync-vpc"
PSA_RANGE_NAME="stylesync-psa-range"

echo "⚠️ WARNING: This will permanently delete the AlloyDB Cluster, Instance, and VPC Networking."
read -p "Are you sure you want to proceed? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

echo "🗑️ Starting Cleanup in Project: $PROJECT_ID ($REGION)..."

# 1. Delete AlloyDB Instance (Must be deleted before the cluster)
if gcloud alloydb instances describe $INSTANCE_ID --cluster=$CLUSTER_ID --region=$REGION --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "Deleting AlloyDB Instance: $INSTANCE_ID..."
    gcloud alloydb instances delete $INSTANCE_ID --cluster=$CLUSTER_ID --region=$REGION --project=$PROJECT_ID --quiet
else
    echo "✅ Instance $INSTANCE_ID not found."
fi

# 2. Delete AlloyDB Cluster
if gcloud alloydb clusters describe $CLUSTER_ID --region=$REGION --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "Deleting AlloyDB Cluster: $CLUSTER_ID..."
    gcloud alloydb clusters delete $CLUSTER_ID --region=$REGION --project=$PROJECT_ID --quiet
else
    echo "✅ Cluster $CLUSTER_ID not found."
fi

# 3. Delete VPC Peering (Service Networking)
echo "Removing VPC Peering..."
gcloud services vpc-peerings delete \
    --service=servicenetworking.googleapis.com \
    --network=$VPC_NAME \
    --project=$PROJECT_ID --quiet 2>/dev/null

# 4. Delete Reserved IP Range
if gcloud compute addresses describe $PSA_RANGE_NAME --global --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "Deleting PSA IP Range: $PSA_RANGE_NAME..."
    gcloud compute addresses delete $PSA_RANGE_NAME --global --project=$PROJECT_ID --quiet
else
    echo "✅ IP Range not found."
fi

# 5. Delete VPC Network
if gcloud compute networks describe $VPC_NAME --project=$PROJECT_ID --global > /dev/null 2>&1; then
    echo "Deleting VPC Network: $VPC_NAME..."
    # We wait a few seconds to ensure peering deletion has propagated
    sleep 10
    gcloud compute networks delete $VPC_NAME --project=$PROJECT_ID --quiet
else
    echo "✅ VPC $VPC_NAME not found."
fi

echo "✨ Cleanup Complete. All StyleSync AlloyDB resources have been removed."