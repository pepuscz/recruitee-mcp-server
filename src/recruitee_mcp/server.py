#!/usr/bin/env python3
"""
Recruitee MCP Server

A Model Context Protocol (MCP) server for the Recruitee API that enables extraction 
of candidate profiles from recruitment pipelines. Provides tools to search, filter, 
and retrieve comprehensive candidate information.
"""

import asyncio
import logging
import os
import sys
import tempfile
from typing import Any, Dict, List, Optional, Sequence, Union
import json

import aiohttp
import pdfplumber
from mcp.server.fastmcp import FastMCP
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server import stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastMCP app
mcp = FastMCP("Recruitee MCP Server")

# Global HTTP session
http_session: Optional[aiohttp.ClientSession] = None

class RecruiteeClient:
    """Client for interacting with the Recruitee API"""
    
    def __init__(self, api_token: str, company_id: str):
        self.api_token = api_token
        self.company_id = company_id
        self.base_url = "https://api.recruitee.com/c/{company_id}".format(company_id=company_id)
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to Recruitee API"""
        global http_session
        if not http_session:
            http_session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making GET request to: {url}")
        
        try:
            async with http_session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed: {response.status} - {error_text}")
                    raise Exception(f"API request failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise

async def extract_pdf_text(pdf_url: str) -> Dict[str, Any]:
    """
    Download and extract full text content from a PDF URL
    
    Args:
        pdf_url: Direct URL to the PDF file
        
    Returns:
        Dict containing extracted text, page count, and metadata
    """
    global http_session
    if not http_session:
        http_session = aiohttp.ClientSession()
    
    try:
        logger.info(f"Downloading PDF from: {pdf_url}")
        
        # Download the PDF
        async with http_session.get(pdf_url) as response:
            if response.status != 200:
                logger.error(f"Failed to download PDF: {response.status}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status}",
                    "full_text": "",
                    "pages": [],
                    "page_count": 0
                }
            
            pdf_content = await response.read()
        
        # Save to temporary file and extract text
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_path = temp_file.name
        
        try:
            # Extract text using pdfplumber
            with pdfplumber.open(temp_path) as pdf:
                pages_text = []
                full_text = ""
                
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append({
                            "page_number": page_num + 1,
                            "text": page_text.strip()
                        })
                        full_text += page_text + "\n\n"
                
                # Get PDF metadata
                metadata = {
                    "page_count": len(pdf.pages),
                    "metadata": pdf.metadata or {}
                }
                
                logger.info(f"Successfully extracted {len(pages_text)} pages from PDF")
                
                return {
                    "success": True,
                    "full_text": full_text.strip(),
                    "pages": pages_text,
                    "page_count": len(pdf.pages),
                    "metadata": metadata,
                    "character_count": len(full_text.strip()),
                    "word_count": len(full_text.split()) if full_text else 0
                }
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return {
            "success": False,
            "error": str(e),
            "full_text": "",
            "pages": [],
            "page_count": 0
        }

# Initialize client
recruitee_client: Optional[RecruiteeClient] = None

def get_client() -> RecruiteeClient:
    """Get initialized Recruitee client"""
    global recruitee_client
    if not recruitee_client:
        api_token = os.getenv("RECRUITEE_API_TOKEN")
        company_id = os.getenv("RECRUITEE_COMPANY_ID")
        
        if not api_token or not company_id:
            raise ValueError("RECRUITEE_API_TOKEN and RECRUITEE_COMPANY_ID environment variables must be set")
        
        recruitee_client = RecruiteeClient(api_token, company_id)
    
    return recruitee_client

@mcp.tool()
async def get_candidates_from_pipeline(job_id: str, include_full_profiles: bool = True, stage_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract all candidates from a specific job pipeline with full profiles.
    
    Args:
        job_id: The job/pipeline ID (required)
        include_full_profiles: Fetch complete profiles (default: true)  
        stage_filter: Optional stage name filter
    """
    client = get_client()
    
    try:
        # Use the correct API endpoint with server-side filtering
        logger.info(f"Fetching candidates for job ID: {job_id}")
        candidates_data = await client.get("/candidates", params={"offer_id": job_id, "limit": 1000})
        
        all_candidates = candidates_data.get("candidates", [])
        logger.info(f"Retrieved {len(all_candidates)} candidates for job {job_id}")
        
        # Apply stage filter if specified (client-side)
        pipeline_candidates = []
        for candidate in all_candidates:
            # Apply stage filter if specified
            if stage_filter:
                placements = candidate.get("placements", [])
                stage_match = False
                for placement in placements:
                    if str(placement.get("offer_id")) == str(job_id):
                        stage = placement.get("stage", {})
                        current_stage = stage.get("name", "") if isinstance(stage, dict) else ""
                        if stage_filter.lower() in current_stage.lower():
                            stage_match = True
                            break
                if not stage_match:
                    continue
            
            if include_full_profiles:
                # Fetch full candidate profile
                try:
                    candidate_id = candidate.get("id")
                    full_profile = await get_candidate_profile(str(candidate_id))
                    pipeline_candidates.append(full_profile)
                except Exception as e:
                    logger.warning(f"Failed to get full profile for candidate {candidate.get('id')}: {e}")
                    pipeline_candidates.append(candidate)
            else:
                pipeline_candidates.append(candidate)
        
        result = {
            "job_id": job_id,
            "stage_filter": stage_filter,
            "total_candidates": len(pipeline_candidates),
            "candidates": pipeline_candidates
        }
        
        logger.info(f"Returning {len(pipeline_candidates)} candidates for job {job_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting candidates from pipeline: {e}")
        raise Exception(f"Failed to get candidates from pipeline: {str(e)}")

@mcp.tool()
async def search_candidates(
    job_ids: Optional[List[str]] = None,
    stage_names: Optional[List[str]] = None, 
    status: Optional[str] = None,
    has_cv: Optional[bool] = None,
    has_cover_letter: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search candidates with optional client-side filtering.
    
    Args:
        job_ids: Filter by specific job IDs
        stage_names: Filter by recruitment stages
        status: Filter by status (Qualified, Disqualified, New)
        has_cv: Filter candidates with/without CV
        has_cover_letter: Filter candidates with/without cover letter
        limit: Number of results to return
        offset: Pagination offset
    """
    client = get_client()
    
    try:
        # Use reliable endpoint and apply client-side filtering
        candidates_data = await client.get("/candidates", params={"limit": 1000})
        all_candidates = candidates_data.get("candidates", [])
        
        # Apply client-side filters
        filtered_candidates = []
        
        for candidate in all_candidates:
            # Apply job_ids filter
            if job_ids:
                candidate_jobs = [str(placement.get("offer_id")) for placement in candidate.get("placements", [])]
                if not any(job_id in candidate_jobs for job_id in job_ids):
                    continue
            
            # Apply stage_names filter  
            if stage_names:
                candidate_stages = [placement.get("stage", {}).get("name", "") for placement in candidate.get("placements", [])]
                if not any(any(stage_name.lower() in stage.lower() for stage_name in stage_names) for stage in candidate_stages):
                    continue
            
            # Apply status filter
            if status:
                candidate_status = candidate.get("status", "")
                if status.lower() not in candidate_status.lower():
                    continue
            
            # Apply CV filter
            if has_cv is not None:
                cv_present = bool(candidate.get("cv_url") or candidate.get("cv"))
                if has_cv != cv_present:
                    continue
            
            # Apply cover letter filter
            if has_cover_letter is not None:
                cover_letter_present = bool(candidate.get("cover_letter"))
                if has_cover_letter != cover_letter_present:
                    continue
            
            filtered_candidates.append(candidate)
        
        # Apply pagination
        paginated_candidates = filtered_candidates[offset:offset + limit]
        
        return {
            "total_found": len(filtered_candidates), 
            "returned": len(paginated_candidates),
            "offset": offset,
            "limit": limit,
            "candidates": paginated_candidates
        }
        
    except Exception as e:
        logger.error(f"Error searching candidates: {e}")
        raise Exception(f"Failed to search candidates: {str(e)}")

@mcp.tool()
async def get_candidate_profile(candidate_id: str) -> Dict[str, Any]:
    """
    Get complete candidate details including contact info, CV, cover letter, experience, and all custom fields.
    Now includes full PDF text extraction in addition to Recruitee's structured parsing.
    
    Args:
        candidate_id: The candidate ID (required)
    """
    client = get_client()
    
    try:
        # Get detailed candidate profile
        candidate_data = await client.get(f"/candidates/{candidate_id}")
        candidate = candidate_data.get("candidate", {})
        
        # Get additional profile data
        try:
            # Get CV and documents
            documents = await client.get(f"/candidates/{candidate_id}/documents")
            candidate["documents"] = documents.get("documents", [])
        except Exception as e:
            logger.warning(f"Failed to get documents for candidate {candidate_id}: {e}")
            candidate["documents"] = []
        
        try:
            # Get screening questions/answers
            screening = await client.get(f"/candidates/{candidate_id}/screening")
            candidate["screening"] = screening.get("screening", [])
        except Exception as e:
            logger.warning(f"Failed to get screening for candidate {candidate_id}: {e}")
            candidate["screening"] = []
        
        # Extract full text from CV PDF if available
        cv_url = candidate.get("cv_url")
        if cv_url:
            logger.info(f"Extracting full text from CV for candidate {candidate_id}")
            pdf_extraction = await extract_pdf_text(cv_url)
            
            # Add our PDF extraction results to the candidate data
            candidate["cv_full_text_extraction"] = pdf_extraction
            
            # Add summary of extraction
            if pdf_extraction.get("success"):
                candidate["cv_text_summary"] = {
                    "has_full_text": True,
                    "page_count": pdf_extraction.get("page_count", 0),
                    "character_count": pdf_extraction.get("character_count", 0),
                    "word_count": pdf_extraction.get("word_count", 0),
                    "extraction_method": "pdfplumber"
                }
            else:
                candidate["cv_text_summary"] = {
                    "has_full_text": False,
                    "error": pdf_extraction.get("error", "Unknown error"),
                    "extraction_method": "pdfplumber"
                }
        else:
            candidate["cv_full_text_extraction"] = {
                "success": False,
                "error": "No CV URL available",
                "full_text": "",
                "pages": [],
                "page_count": 0
            }
            candidate["cv_text_summary"] = {
                "has_full_text": False,
                "error": "No CV URL available"
            }
        
        # Extract cover letter PDF if available (in addition to API text)
        cover_letter_file_url = candidate.get("cover_letter_file_url")
        if cover_letter_file_url:
            logger.info(f"Extracting full text from cover letter PDF for candidate {candidate_id}")
            cover_letter_pdf_extraction = await extract_pdf_text(cover_letter_file_url)
            
            # Add cover letter PDF extraction results
            candidate["cover_letter_pdf_extraction"] = cover_letter_pdf_extraction
            
            # Add summary of cover letter extraction
            if cover_letter_pdf_extraction.get("success"):
                candidate["cover_letter_pdf_summary"] = {
                    "has_pdf_text": True,
                    "page_count": cover_letter_pdf_extraction.get("page_count", 0),
                    "character_count": cover_letter_pdf_extraction.get("character_count", 0),
                    "word_count": cover_letter_pdf_extraction.get("word_count", 0),
                    "extraction_method": "pdfplumber"
                }
            else:
                candidate["cover_letter_pdf_summary"] = {
                    "has_pdf_text": False,
                    "error": cover_letter_pdf_extraction.get("error", "Unknown error"),
                    "extraction_method": "pdfplumber"
                }
        else:
            candidate["cover_letter_pdf_extraction"] = {
                "success": False,
                "error": "No cover letter PDF URL available",
                "full_text": "",
                "pages": [],
                "page_count": 0
            }
            candidate["cover_letter_pdf_summary"] = {
                "has_pdf_text": False,
                "error": "No cover letter PDF URL available"
            }
        
        # Create unified cover letter summary
        api_cover_letter = candidate.get("cover_letter", "")
        pdf_cover_letter = candidate["cover_letter_pdf_extraction"].get("full_text", "")
        
        candidate["cover_letter_unified_summary"] = {
            "has_api_text": bool(api_cover_letter),
            "has_pdf_text": bool(pdf_cover_letter),
            "api_character_count": len(api_cover_letter) if api_cover_letter else 0,
            "pdf_character_count": len(pdf_cover_letter) if pdf_cover_letter else 0,
            "total_sources": sum([bool(api_cover_letter), bool(pdf_cover_letter)]),
            "recommendation": "Use PDF text" if pdf_cover_letter and not api_cover_letter else "Use API text" if api_cover_letter and not pdf_cover_letter else "Compare both sources" if api_cover_letter and pdf_cover_letter else "No cover letter available"
        }
        
        return candidate
        
    except Exception as e:
        logger.error(f"Error getting candidate profile: {e}")
        raise Exception(f"Failed to get candidate profile: {str(e)}")

@mcp.tool()
async def extract_cv_text(pdf_url: str) -> Dict[str, Any]:
    """
    Extract full text content from any PDF URL (useful for CVs, cover letters, or other documents).
    
    Args:
        pdf_url: Direct URL to the PDF file to extract text from
    """
    try:
        logger.info(f"Extracting text from PDF: {pdf_url}")
        result = await extract_pdf_text(pdf_url)
        
        return {
            "pdf_url": pdf_url,
            "extraction_result": result
        }
        
    except Exception as e:
        logger.error(f"Error extracting CV text: {e}")
        raise Exception(f"Failed to extract CV text: {str(e)}")

@mcp.tool()
async def list_jobs() -> Dict[str, Any]:
    """List all available jobs/pipelines."""
    client = get_client()
    
    try:
        jobs_data = await client.get("/offers")
        jobs = jobs_data.get("offers", [])
        
        return {
            "total_jobs": len(jobs),
            "jobs": jobs
        }
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise Exception(f"Failed to list jobs: {str(e)}")

@mcp.tool()
async def get_job_details(job_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific job/pipeline.
    
    Args:
        job_id: The job ID (required)
    """
    client = get_client()
    
    try:
        job_data = await client.get(f"/offers/{job_id}")
        job = job_data.get("offer", {})
        
        # Get additional job information
        try:
            stages_data = await client.get(f"/offers/{job_id}/stages")
            job["stages"] = stages_data.get("stages", [])
        except Exception as e:
            logger.warning(f"Failed to get stages for job {job_id}: {e}")
            job["stages"] = []
        
        return job
        
    except Exception as e:
        logger.error(f"Error getting job details: {e}")
        raise Exception(f"Failed to get job details: {str(e)}")

@mcp.tool()
async def get_candidate_notes(candidate_id: str) -> Dict[str, Any]:
    """
    Get notes and comments for a candidate.
    
    Args:
        candidate_id: The candidate ID (required)
    """
    client = get_client()
    
    try:
        notes_data = await client.get(f"/candidates/{candidate_id}/notes")
        notes = notes_data.get("notes", [])
        
        return {
            "candidate_id": candidate_id,
            "total_notes": len(notes),
            "notes": notes
        }
        
    except Exception as e:
        logger.error(f"Error getting candidate notes: {e}")
        raise Exception(f"Failed to get candidate notes: {str(e)}")

@mcp.tool()
async def get_candidates_basic(limit: int = 100) -> Dict[str, Any]:
    """
    Get basic candidate list using the reliable endpoint.
    
    Args:
        limit: Number of candidates to return
    """
    client = get_client()
    
    try:
        candidates_data = await client.get("/candidates", params={"limit": limit})
        candidates = candidates_data.get("candidates", [])
        
        return {
            "total_returned": len(candidates),
            "candidates": candidates
        }
        
    except Exception as e:
        logger.error(f"Error getting basic candidates: {e}")
        raise Exception(f"Failed to get candidates: {str(e)}")

async def cleanup():
    """Cleanup resources"""
    global http_session
    if http_session:
        await http_session.close()

async def main():
    """Main entry point for the MCP server"""
    try:
        # Run the FastMCP app with stdio transport
        await mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        await cleanup()

def main_sync():
    """Synchronous wrapper for main() for console script entry point"""
    try:
        # Let FastMCP handle the event loop
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main_sync() 