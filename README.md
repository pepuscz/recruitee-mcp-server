# Recruitee MCP Server

A Model Context Protocol (MCP) server for the Recruitee API that enables extraction of candidate profiles from recruitment pipelines. Optimized for LLM context efficiency with a streamlined set of tools.

## Features

- **LLM-Context Optimized**: `get_candidates_from_pipeline` returns high-level candidate info by default to avoid overwhelming LLM context
- **Screening Questions Analysis**: Shows completion status of candidate screening questions/forms
- **Complete Candidate Profiles**: Use `get_candidate_profile()` to get detailed information for specific candidates
- **PDF Text Extraction**: Automatic CV and cover letter text extraction using pdfplumber
- **Server-side Filtering**: Efficient candidate filtering by job/pipeline
- **Comprehensive Search**: Advanced candidate search with multiple filter criteria
- **Notes Access**: Separate access to candidate notes and comments

## Available Tools

### Core Tools

1. **`get_candidates_from_pipeline`** - Get high-level candidate list from a job pipeline
2. **`get_candidate_profile`** - Get complete detailed profile for a specific candidate
3. **`search_candidates`** - Search and filter candidates with various criteria
4. **`list_jobs`** - List all available jobs/pipelines
5. **`get_job_details`** - Get detailed information about a specific job
6. **`get_candidate_notes`** - Access notes and comments for a candidate

### Tool Details

#### `get_candidates_from_pipeline(job_id, include_full_profiles=False, stage_filter=None)`
**Optimized for LLM Context**: Returns only essential candidate information by default.
- **High-level mode** (default): Returns id, name, status, source, screening questions completion, placement stage
- **Full profile mode**: Set `include_full_profiles=True` for complete data (use sparingly)
- **Stage filtering**: Optional filter by recruitment stage

#### `get_candidate_profile(candidate_id)`
Get complete candidate details including:
- Contact information and basic profile data
- CV text extraction (full PDF text using pdfplumber)
- Cover letter content (both API text and PDF extraction)
- Custom fields and screening questions
- Placement history and ratings
- Source and referral information

#### `search_candidates(job_ids, stage_names, status, has_cv, has_cover_letter, limit, offset)`
Advanced search with client-side filtering:
- Filter by specific job IDs
- Filter by recruitment stages
- Filter by candidate status
- Filter by CV/cover letter presence
- Pagination support

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd recruitee-mcp-server

# Install dependencies
pip install -e .
```

## Configuration

Set environment variables:

```bash
export RECRUITEE_API_TOKEN="your-api-token"
export RECRUITEE_COMPANY_ID="your-company-id"
```

## Usage

### Basic Workflow (Recommended)

1. **Get high-level candidate overview:**
```python
# Returns essential info for all candidates (LLM-friendly)
candidates = get_candidates_from_pipeline("job_id")
```

2. **Get detailed profile for specific candidates:**
```python
# Get complete profile including CV text extraction
profile = get_candidate_profile("candidate_id")
```

### Advanced Usage

**Search candidates:**
```python
results = search_candidates(
    job_ids=["123", "456"],
    stage_names=["Interview", "Assessment"],
    has_cv=True,
    limit=20
)
```

**Get candidate notes:**
```python
notes = get_candidate_notes("candidate_id")
```

## MCP Integration

Add to your MCP settings:

```json
{
  "mcpServers": {
    "recruitee": {
      "command": "python",
      "args": ["-m", "recruitee_mcp.server"],
      "env": {
        "RECRUITEE_API_TOKEN": "your-token",
        "RECRUITEE_COMPANY_ID": "your-company-id"
      }
    }
  }
}
```

## Performance Optimization

- **High-level mode**: Use default settings for `get_candidates_from_pipeline` to get lightweight candidate lists
- **Selective profiling**: Only call `get_candidate_profile()` for candidates you're specifically interested in
- **Efficient filtering**: Use `search_candidates()` for complex queries instead of fetching all candidates

## License

MIT License

## 🔗 Links

- **Repository**: [https://github.com/pepuscz/recruitee-mcp-server](https://github.com/pepuscz/recruitee-mcp-server)
- **Issues**: [https://github.com/pepuscz/recruitee-mcp-server/issues](https://github.com/pepuscz/recruitee-mcp-server/issues)
- **Recruitee API**: [https://docs.recruitee.com/](https://docs.recruitee.com/)
- **Model Context Protocol**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)

---

> 💼 **Perfect for recruitment teams, HR professionals, and developers building recruitment automation tools.** 