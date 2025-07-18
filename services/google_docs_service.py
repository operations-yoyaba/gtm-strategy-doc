import os
import logging
import json
from typing import Dict, Any, Tuple
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class GoogleDocsService:
    def __init__(self):
        self.template_doc_id = os.getenv("GS_TEMPLATE_DOC_ID")
        self.folder_id = os.getenv("GS_DRIVE_FOLDER_ID")
        
        # Initialize Google Docs API client
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=[
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        self.docs_service = build('docs', 'v1', credentials=credentials)
        self.drive_service = build('drive', 'v3', credentials=credentials)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def create_doc_from_template(self, research_result: Dict[str, str], gtm_context: Dict[str, Any] = None) -> Tuple[str, str]:
        """
        Create a new Google Doc from template and populate with research results
        
        Returns: (doc_url, revision_id)
        """
        try:
            # Step 1: Copy template to new document
            doc_id = await self._copy_template()
            
            # Step 2: Replace all placeholders with content
            revision_id = await self._replace_content(doc_id, research_result)
            
            # Step 3: Store JSON file for subsequent iterations
            if gtm_context:
                await self._store_json_file(doc_id, research_result, gtm_context)
            
            # Step 4: Generate shareable URL
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            logger.info(f"Created Google Doc: {doc_url}")
            return doc_url, revision_id
            
        except Exception as e:
            logger.error(f"Failed to create Google Doc: {str(e)}")
            raise

    async def _copy_template(self) -> str:
        """Copy the template document to create a new document"""
        try:
            # Copy the template
            copied_file = self.drive_service.files().copy(
                fileId=self.template_doc_id,
                body={
                    'name': f'GTM Strategy - {self._generate_timestamp()}',
                    'parents': [self.folder_id] if self.folder_id else None
                }
            ).execute()
            
            return copied_file['id']
            
        except HttpError as e:
            if e.resp.status == 429:
                logger.error("Google Drive API rate limit exceeded")
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                logger.error(f"Failed to copy template: {e}")
                raise

    async def _replace_content(self, doc_id: str, research_result: Dict[str, str]) -> str:
        """Replace all placeholders in the document with actual content"""
        try:
            # Build batch update request
            requests = []
            
            # Define the placeholders and their corresponding content
            placeholders = {
                "{{DOC_TITLE}}": research_result.get("DOC_TITLE", ""),
                "{{INTRO}}": research_result.get("INTRO", ""),
                "{{PRICING_PACKAGING}}": research_result.get("PRICING_PACKAGING", ""),
                "{{GTM_MOTION}}": research_result.get("GTM_MOTION", ""),
                "{{TOUCH_MODEL}}": research_result.get("TOUCH_MODEL", ""),
                "{{ICP}}": research_result.get("ICP", ""),
                "{{METRICS}}": research_result.get("METRICS", ""),
                "{{FINANCIALS}}": research_result.get("FINANCIALS", ""),
                "{{FINANCING}}": research_result.get("FINANCING", ""),
                "{{MARKET_MATURITY}}": research_result.get("MARKET_MATURITY", ""),
                "{{STAKEHOLDERS}}": research_result.get("STAKEHOLDERS", ""),
                "{{SUMMARY_TABLE}}": research_result.get("SUMMARY_TABLE", "")
            }
            
            # Create replaceAllText requests for each placeholder
            for placeholder, content in placeholders.items():
                if content:  # Only replace if content exists
                    requests.append({
                        'replaceAllText': {
                            'containsText': {
                                'text': placeholder,
                                'matchCase': True
                            },
                            'replaceText': content
                        }
                    })
            
            # Execute batch update
            if requests:
                result = self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': requests}
                ).execute()
                
                # Get the revision ID
                document = self.docs_service.documents().get(documentId=doc_id).execute()
                return str(document.get('revisionId', 1))
            else:
                return "1"
                
        except HttpError as e:
            if e.resp.status == 429:
                logger.error("Google Docs API rate limit exceeded")
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                logger.error(f"Failed to replace content: {e}")
                raise

    async def _store_json_file(self, doc_id: str, research_result: Dict[str, str], gtm_context: Dict[str, Any]) -> None:
        """Store JSON file for subsequent iterations"""
        try:
            # Create JSON content with metadata
            json_content = {
                "doc_id": doc_id,
                "created_at": self._generate_timestamp(),
                "gtm_context": gtm_context,
                "research_result": research_result,
                "version": 1
            }
            
            # Create JSON file in the same folder
            file_metadata = {
                'name': f'{doc_id}-json.json',
                'parents': [self.folder_id] if self.folder_id else None,
                'mimeType': 'application/json'
            }
            
            # Upload the JSON file
            self.drive_service.files().create(
                body=file_metadata,
                media_body=json.dumps(json_content, indent=2)
            ).execute()
            
            logger.info(f"Stored JSON file for doc {doc_id}")
            
        except Exception as e:
            logger.error(f"Failed to store JSON file: {str(e)}")
            # Don't raise - this is not critical for the main flow

    async def get_stored_json(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve stored JSON for a document"""
        try:
            # Search for the JSON file
            query = f"name='{doc_id}-json.json' and '{self.folder_id}' in parents"
            results = self.drive_service.files().list(q=query).execute()
            
            if results.get('files'):
                file_id = results['files'][0]['id']
                # Download the file content
                file_content = self.drive_service.files().get_media(fileId=file_id).execute()
                return json.loads(file_content.decode('utf-8'))
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve stored JSON: {str(e)}")
            return None

    async def update_stored_json(self, doc_id: str, new_research_result: Dict[str, str], gtm_context: Dict[str, Any]) -> None:
        """Update stored JSON with new research result"""
        try:
            # Get existing JSON
            existing_json = await self.get_stored_json(doc_id)
            
            if existing_json:
                # Update version and research result
                existing_json["research_result"] = new_research_result
                existing_json["gtm_context"] = gtm_context
                existing_json["version"] = existing_json.get("version", 1) + 1
                existing_json["updated_at"] = self._generate_timestamp()
                
                # Find the file and update it
                query = f"name='{doc_id}-json.json' and '{self.folder_id}' in parents"
                results = self.drive_service.files().list(q=query).execute()
                
                if results.get('files'):
                    file_id = results['files'][0]['id']
                    self.drive_service.files().update(
                        fileId=file_id,
                        media_body=json.dumps(existing_json, indent=2)
                    ).execute()
                    
                    logger.info(f"Updated JSON file for doc {doc_id}")
            else:
                # Create new JSON file if it doesn't exist
                await self._store_json_file(doc_id, new_research_result, gtm_context)
                
        except Exception as e:
            logger.error(f"Failed to update stored JSON: {str(e)}")

    async def patch_document(self, doc_id: str, diff: Dict[str, Any], revision_id: str) -> str:
        """
        Patch specific sections of a document based on diff
        
        This is for future implementation when volume > 2/day
        """
        try:
            # This would implement the patch strategy outlined in section 6
            # For now, return the current revision ID
            return revision_id
            
        except Exception as e:
            logger.error(f"Failed to patch document: {str(e)}")
            raise

    def _generate_timestamp(self) -> str:
        """Generate a timestamp for document naming"""
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    async def get_document_revision(self, doc_id: str) -> str:
        """Get the current revision ID of a document"""
        try:
            document = self.docs_service.documents().get(documentId=doc_id).execute()
            return str(document.get('revisionId', 1))
        except Exception as e:
            logger.error(f"Failed to get document revision: {str(e)}")
            raise 