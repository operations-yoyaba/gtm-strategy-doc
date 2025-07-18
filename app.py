#!/usr/bin/env python3
"""
GTM Strategy Document Generator - Main Application
Combines job submission and webhook handling in a single FastAPI app
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import Response
import openai
from openai import InvalidWebhookSignatureError

# Google Cloud Secret Manager
try:
    from google.cloud import secretmanager
    secret_manager_available = True
except ImportError:
    secret_manager_available = False

from services.openai_service import OpenAIService
from services.google_docs_service import GoogleDocsService
from models.gtm_context import GenerateRequest

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_secret(secret_name: str, fallback_env_var: str = None) -> str:
    """
    Get secret from Google Secret Manager or fallback to environment variable
    """
    if secret_manager_available:
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/yoyaba-db/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.warning(f"Failed to get secret {secret_name} from Secret Manager: {e}")
    
    # Fallback to environment variable
    if fallback_env_var:
        return os.getenv(fallback_env_var)
    
    return None

# Initialize FastAPI app
app = FastAPI(
    title="GTM Strategy Document Generator",
    description="Webhook-based GTM strategy document generation system",
    version="1.0.0"
)

# Initialize services
openai_service = OpenAIService()

# Initialize Google Docs service only if credentials are available
try:
    google_docs_service = GoogleDocsService()
    google_docs_available = True
    logger.info("Google Docs service initialized successfully")
except Exception as e:
    logger.warning(f"Google Docs service not available: {e}")
    google_docs_service = None
    google_docs_available = False

# In-memory job tracking (in production, use a proper database)
job_tracker = {}

@app.post("/generate")
async def generate_gtm_doc(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Submit a background deep research job for GTM strategy document generation
    
    This endpoint submits a background job to OpenAI and returns immediately.
    The actual document generation happens when OpenAI calls our webhook.
    """
    try:
        logger.info(f"Received GTM document generation request for company: {request.company.get('name', 'Unknown')}")
        
        # Get secrets
        openai_api_key = get_secret("OPENAI_API_KEY", "OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not available")
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Prepare raw data
        raw_data = {
            "company": request.get_company_data(),
            "enriched_data": request.enriched_data
        }
        
        # Build the research input
        research_input = openai_service._build_deep_research_input(raw_data)
        
        # Count input tokens
        input_tokens = openai_service.count_tokens(research_input)
        logger.info(f"Input tokens: {input_tokens:,}")
        
        # Submit background job to OpenAI
        response = client.responses.create(
            model="o3-deep-research",
            input=research_input,
            tools=[
                {"type": "web_search_preview"},
                {"type": "code_interpreter", "container": {"type": "auto"}}
            ],
            background=True,
            timeout=3600
        )
        
        response_id = response.id
        logger.info(f"Submitted background job: {response_id}")
        
        # Store job metadata for webhook correlation
        job_tracker[response_id] = {
            "company_name": request.company.get('name', 'Unknown'),
            "company_id": request.companyId,
            "input_tokens": input_tokens,
            "raw_data": raw_data,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "submitted"
        }
        
        logger.info(f"Successfully submitted background job: {response_id}")
        
        return {
            "status": "submitted",
            "response_id": response_id,
            "message": f"Deep research job submitted for {request.company.get('name', 'Unknown')}",
            "estimated_completion": "5-15 minutes",
            "webhook_url": f"/webhook/openai",
            "check_status_url": f"/job-status/{response_id}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting background job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/openai")
async def handle_openai_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle OpenAI webhook events, specifically response.completed
    """
    try:
        # Get secrets
        openai_api_key = get_secret("OPENAI_API_KEY", "OPENAI_API_KEY")
        openai_webhook_secret = get_secret("openai-webhook-secret", "OPENAI_WEBHOOK_SECRET")
        
        if not openai_api_key or not openai_webhook_secret:
            raise HTTPException(status_code=500, detail="Required secrets not available")
        
        # Initialize OpenAI client with webhook secret
        client = openai.OpenAI(
            api_key=openai_api_key,
            webhook_secret=openai_webhook_secret
        )
        
        # Get raw body for signature verification
        body = await request.body()
        headers = dict(request.headers)
        
        # Verify webhook signature
        try:
            event = client.webhooks.unwrap(body, headers)
        except InvalidWebhookSignatureError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        logger.info(f"Received webhook event: {event.type}")
        
        # Handle response.completed events
        if event.type == "response.completed":
            response_id = event.data.id
            logger.info(f"Processing completed response: {response_id}")
            
            # Add to background tasks to avoid webhook timeout
            background_tasks.add_task(process_completed_response, response_id)
            
            # Return success immediately to acknowledge receipt
            return Response(status_code=200, content="OK")
        
        # For other event types, just acknowledge
        return Response(status_code=200, content="OK")
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_completed_response(response_id: str):
    """
    Process a completed deep research response
    """
    try:
        logger.info(f"Processing response {response_id}")
        
        # Get secrets
        openai_api_key = get_secret("OPENAI_API_KEY", "OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OpenAI API key not available")
            return
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Retrieve the completed response from OpenAI
        response = client.responses.retrieve(response_id)
        
        if response.status != "completed":
            logger.warning(f"Response {response_id} is not completed, status: {response.status}")
            return
        
        # Extract the output text
        output_text = response.output_text
        logger.info(f"Retrieved output text for response {response_id}")
        
        # Get job metadata from our tracker
        job_data = job_tracker.get(response_id)
        if not job_data:
            logger.error(f"No job data found for response {response_id}")
            return
        
        # Parse the JSON response
        try:
            research_result = json.loads(output_text)
            logger.info(f"Successfully parsed JSON response for {response_id}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for {response_id}: {e}")
            # Try fallback parsing
            research_result = openai_service._extract_json_from_response(output_text)
        
        # Count tokens for the output
        output_tokens = openai_service.count_tokens(output_text)
        token_usage = {
            "model": "o3-deep-research",
            "input_tokens": job_data.get("input_tokens", 0),
            "output_tokens": output_tokens,
            "total_tokens": job_data.get("input_tokens", 0) + output_tokens
        }
        
        logger.info(f"Token usage for {response_id}: {token_usage['total_tokens']:,} total tokens")
        
        # Create Google Doc if service is available
        if google_docs_service:
            logger.info(f"Creating Google Doc for {response_id}")
            doc_url, revision_id = await google_docs_service.create_doc_from_template(
                research_result,
                job_data["raw_data"]
            )
            logger.info(f"Successfully created Google Doc: {doc_url}")
        else:
            logger.warning(f"Google Docs service not available, skipping doc creation for {response_id}")
            doc_url = "Google Docs service unavailable"
            revision_id = "N/A"
        
        # Store completion info
        completion_data = {
            "response_id": response_id,
            "doc_url": doc_url,
            "revision_id": revision_id,
            "token_usage": token_usage,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "success"
        }
        
        job_tracker[response_id]["completion"] = completion_data
        job_tracker[response_id]["status"] = "completed"
        
        logger.info(f"Successfully processed response {response_id}")
        
    except Exception as e:
        logger.error(f"Error processing response {response_id}: {str(e)}")
        if response_id in job_tracker:
            job_tracker[response_id]["error"] = str(e)
            job_tracker[response_id]["status"] = "failed"

@app.get("/job-status/{response_id}")
async def get_job_status(response_id: str):
    """
    Get the status of a submitted job
    """
    job_data = job_tracker.get(response_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "response_id": response_id,
        "company_name": job_data["company_name"],
        "status": job_data.get("status", "unknown"),
        "submitted_at": job_data["submitted_at"],
        "completion": job_data.get("completion"),
        "error": job_data.get("error")
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    # Get secrets dynamically
    openai_api_key = get_secret("OPENAI_API_KEY", "OPENAI_API_KEY")
    openai_webhook_secret = get_secret("openai-webhook-secret", "OPENAI_WEBHOOK_SECRET")
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "openai": "configured" if openai_api_key else "missing",
            "google_docs": "available" if google_docs_available else "unavailable",
            "webhook_secret": "configured" if openai_webhook_secret else "missing",
            "secret_manager": "available" if secret_manager_available else "unavailable"
        }
    }

@app.post("/test-google-drive")
async def test_google_drive(request: Request):
    """
    Test Google Drive service directly without OpenAI
    """
    try:
        body = await request.json()
        
        # Extract test data
        company_id = str(body.get("companyId", "99999"))
        company_domain = body.get("company", {}).get("domain", "test.com")
        dummy_research = body.get("dummy_research_result", {})
        
        logger.info(f"Testing Google Drive with company: {company_id}-{company_domain}")
        
        if not google_docs_service:
            raise HTTPException(status_code=500, detail="Google Docs service not available")
        
        # Test Google Drive creation
        doc_url, revision_id = await google_docs_service.create_doc_from_template(
            research_result=dummy_research,
            gtm_context={"test": True},
            company_id=company_id,
            company_domain=company_domain
        )
        
        return {
            "status": "success",
            "doc_url": doc_url,
            "folder_name": f"{company_id}-{company_domain}",
            "revision_id": revision_id,
            "message": "Google Drive test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Google Drive test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-template-access")
async def test_template_access(request: Request):
    """
    Test access to the template document
    """
    try:
        body = await request.json()
        logger.info("Testing template document access")
        
        if not google_docs_service:
            raise HTTPException(status_code=500, detail="Google Docs service not available")
        
        # Try to get template document info
        try:
            template_info = google_docs_service.drive_service.files().get(
                fileId=google_docs_service.template_doc_id,
                fields='id,name,permissions,owners'
            ).execute()
            
            return {
                "status": "success",
                "template_id": template_info.get('id'),
                "template_name": template_info.get('name'),
                "access_status": "accessible",
                "owners": [owner.get('emailAddress') for owner in template_info.get('owners', [])],
                "permissions": len(template_info.get('permissions', []))
            }
            
        except Exception as e:
            logger.error(f"Template access failed: {str(e)}")
            return {
                "status": "error",
                "template_id": google_docs_service.template_doc_id,
                "error": str(e),
                "access_status": "not_accessible"
            }
        
    except Exception as e:
        logger.error(f"Template access test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-create-direct")
async def test_create_direct(request: Request):
    """
    Test creating a document directly without copying template
    """
    try:
        body = await request.json()
        logger.info("Testing direct document creation")
        
        if not google_docs_service:
            raise HTTPException(status_code=500, detail="Google Docs service not available")
        
        # Create document directly without copying template
        try:
            # Create a new document directly
            doc_metadata = {
                'name': 'Test Document Created Directly',
                'mimeType': 'application/vnd.google-apps.document'
            }
            
            doc = google_docs_service.drive_service.files().create(
                body=doc_metadata,
                fields='id,name'
            ).execute()
            
            doc_id = doc['id']
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            return {
                "status": "success",
                "doc_url": doc_url,
                "doc_id": doc_id,
                "message": "Document created directly without template"
            }
            
        except Exception as e:
            logger.error(f"Direct document creation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to create document directly"
            }
        
    except Exception as e:
        logger.error(f"Direct document creation test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-simple-doc")
async def test_simple_doc(request: Request):
    """
    Test creating a simple document without any template or complex logic
    """
    try:
        body = await request.json()
        logger.info("Testing simple document creation")
        
        if not google_docs_service:
            raise HTTPException(status_code=500, detail="Google Docs service not available")
        
        try:
            # Create a simple document directly in the root folder
            doc_metadata = {
                'name': 'Simple Test Document',
                'mimeType': 'application/vnd.google-apps.document',
                'parents': [google_docs_service.root_folder_id]
            }
            
            doc = google_docs_service.drive_service.files().create(
                body=doc_metadata,
                fields='id,name'
            ).execute()
            
            doc_id = doc['id']
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            return {
                "status": "success",
                "doc_url": doc_url,
                "doc_id": doc_id,
                "message": "Simple document created successfully"
            }
            
        except Exception as e:
            logger.error(f"Simple document creation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to create simple document"
            }
        
    except Exception as e:
        logger.error(f"Simple document creation test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "GTM Strategy Document Generator",
        "version": "1.0.0",
        "description": "Webhook-based GTM strategy document generation system",
        "endpoints": {
            "submit_job": "POST /generate",
            "webhook": "POST /webhook/openai",
            "job_status": "GET /job-status/{response_id}",
            "test_google_drive": "POST /test-google-drive",
            "test_template_access": "POST /test-template-access",
            "test_create_direct": "POST /test-create-direct",
            "test_simple_doc": "POST /test-simple-doc",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 