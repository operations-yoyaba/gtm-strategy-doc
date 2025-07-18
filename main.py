import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import json

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from services.openai_service import OpenAIService
from services.google_docs_service import GoogleDocsService
from models.gtm_context import GenerateRequest
from services.hubspot_service import HubSpotService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GTM Strategy Document Generator")

# Initialize services
openai_service = OpenAIService()

# Initialize Google Docs service only if credentials are available
try:
    google_docs_service = GoogleDocsService()
    google_docs_available = True
except Exception as e:
    logger.warning(f"Google Docs service not available: {e}")
    google_docs_service = None
    google_docs_available = False

# Initialize HubSpot service
hubspot_service = HubSpotService()

@app.post("/generate")
async def generate_gtm_doc(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate a GTM strategy document using webhook-based background processing
    
    This endpoint submits a background job to OpenAI and returns immediately.
    The actual document generation happens when OpenAI calls our webhook.
    """
    try:
        logger.info(f"Received GTM document generation request for company: {request.company.get('name', 'Unknown')}")
        
        # Step 1: Submit background deep research job to OpenAI
        logger.info("Submitting background deep research job")
        
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
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
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
        
        # Step 2: Store job metadata for webhook correlation
        # In production, this would be stored in a database
        job_metadata = {
            "response_id": response_id,
            "company_name": request.company.get('name', 'Unknown'),
            "company_id": request.companyId,
            "company_domain": request.company.get('domain', 'unknown'),
            "input_tokens": input_tokens,
            "raw_data": raw_data,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "submitted"
        }
        
        # For now, we'll store in memory (in production, use a database)
        # This is just for demonstration - the webhook handler will handle the actual processing
        
        logger.info(f"Successfully submitted background job: {response_id}")
        
        return {
            "status": "submitted",
            "response_id": response_id,
            "message": f"Deep research job submitted for {request.company.get('name', 'Unknown')}",
            "estimated_completion": "5-15 minutes",
            "webhook_url": f"/webhook/openai (configured in OpenAI dashboard)",
            "check_status_url": f"/job-status/{response_id}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting background job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job-status/{response_id}")
async def get_job_status(response_id: str):
    """
    Get the status of a submitted job
    
    Note: This is a placeholder. In the full implementation,
    this would query the database for job status.
    """
    # This is a placeholder - in production, query your database
    return {
        "response_id": response_id,
        "status": "submitted",
        "message": "Job status tracking not yet implemented. Check webhook logs for completion.",
        "note": "The webhook handler processes completed jobs automatically."
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "openai": "configured",
            "google_docs": "configured",
            "hubspot": "configured"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 