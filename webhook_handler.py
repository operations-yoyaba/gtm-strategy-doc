#!/usr/bin/env python3
"""
Webhook handler for OpenAI deep research completion events
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import Response
import openai
from openai import InvalidWebhookSignatureError

from services.openai_service import OpenAIService
from services.google_docs_service import GoogleDocsService
from models.gtm_context import GenerateRequest

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="GTM Strategy Doc Webhook Handler")

# Initialize OpenAI client with webhook secret
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    webhook_secret=os.getenv("OPENAI_WEBHOOK_SECRET")
)

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

# In-memory job tracking (in production, use a proper database)
job_tracker = {}

@app.post("/webhook/openai")
async def handle_openai_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle OpenAI webhook events, specifically response.completed
    """
    try:
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
        
        # Create Google Doc
        logger.info(f"Creating Google Doc for {response_id}")
        if google_docs_service:
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
        
        # In production, store this in a database
        job_tracker[response_id]["completion"] = completion_data
        
        logger.info(f"Successfully processed response {response_id}")
        
    except Exception as e:
        logger.error(f"Error processing response {response_id}: {str(e)}")
        # In production, store error state in database
        if response_id in job_tracker:
            job_tracker[response_id]["error"] = str(e)

@app.post("/submit-job")
async def submit_deep_research_job(request: GenerateRequest):
    """
    Submit a deep research job in background mode
    """
    try:
        logger.info(f"Submitting deep research job for company: {request.company.name}")
        
        # Prepare raw data
        raw_data = {
            "company": request.get_company_data(),
            "enriched_data": request.enriched_data
        }
        
        # Build the research input (same as before)
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
        
        # Store job metadata for later correlation
        job_tracker[response_id] = {
            "company_name": request.company.name,
            "company_id": request.companyId,
            "input_tokens": input_tokens,
            "raw_data": raw_data,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "submitted"
        }
        
        return {
            "status": "submitted",
            "response_id": response_id,
            "message": f"Deep research job submitted for {request.company.name}",
            "estimated_completion": "5-15 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error submitting job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 