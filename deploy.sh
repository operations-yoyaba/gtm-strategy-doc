#!/bin/bash

# GTM Strategy Doc Generator - Cloud Run Deployment Script

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
SERVICE_NAME="gtm-doc"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying GTM Strategy Doc Generator to Cloud Run${NC}"

# Check if PROJECT_ID is set
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${RED}❌ Please set PROJECT_ID environment variable${NC}"
    echo "export PROJECT_ID=your-actual-project-id"
    exit 1
fi

# Build and push Docker image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:latest .

echo -e "${YELLOW}📤 Pushing image to Google Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --timeout 900s \
    --min-instances 0 \
    --max-instances 10 \
    --memory 1Gi \
    --cpu 1 \
    --concurrency 80 \
    --service-account gtm-doc@${PROJECT_ID}.iam.gserviceaccount.com \
    --set-env-vars "LOG_LEVEL=INFO" \
    --allow-unauthenticated

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID} --format="value(status.url)")

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}📋 Health check: ${SERVICE_URL}/healthz${NC}"
echo -e "${GREEN}📝 Generate endpoint: ${SERVICE_URL}/generate${NC}"

# Display next steps
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Set up environment variables in Cloud Run:"
echo "   - OPENAI_API_KEY"
echo "   - HUBSPOT_ACCESS_TOKEN"
echo "   - GS_TEMPLATE_DOC_ID"
echo "   - GS_DRIVE_FOLDER_ID"
echo "   - GOOGLE_APPLICATION_CREDENTIALS"
echo "   - CLAY_API_KEY"
echo ""
echo "2. Configure the service account permissions"
echo "3. Set up the n8n webhook to call ${SERVICE_URL}/generate"
echo "4. Test with a sample request"

echo -e "${GREEN}🎉 Ready to generate GTM strategy documents!${NC}" 