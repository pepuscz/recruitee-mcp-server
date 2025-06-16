# Recruitee MCP Server

A Model Context Protocol (MCP) server for the Recruitee API that enables extraction of candidate profiles from recruitment pipelines. Features three purpose-built functions optimized for different use cases: basic overviews, LLM evaluation, and detailed analysis.

## Features

- **Three Purpose-Built Functions**: Clean API with distinct functions for different use cases
- **LLM Evaluation Optimized**: `get_candidates_from_pipeline_for_evaluation` provides curated data for candidate analysis
- **Screening Questions Analysis**: Shows completion status of candidate screening questions (open questions only)
- **PDF Text Extraction**: Automatic CV and cover letter text extraction using pdfplumber
- **Server-side Filtering**: Efficient candidate filtering by job/pipeline
- **Comprehensive Search**: Advanced candidate search with multiple filter criteria
- **Notes Access**: Separate access to candidate notes and comments

## Available Tools

### Core Tools

1. **`get_candidates_from_pipeline`** - Get high-level candidate list for quick overviews and filtering
2. **`get_candidates_from_pipeline_for_evaluation`** - Get evaluation-focused data optimized for LLM analysis
3. **`get_candidate_profile`** - Get complete detailed profile for a specific candidate
4. **`search_candidates`** - Search and filter candidates with various criteria
5. **`list_jobs`** - List all available jobs/pipelines
6. **`get_job_details`** - Get detailed information about a specific job
7. **`get_candidate_notes`** - Access notes and comments for a candidate

### Tool Details

#### `get_candidates_from_pipeline(job_id, stage_filter=None)`
**High-level candidate overview**: Returns basic candidate information for quick filtering and counting.
- Returns: id, name, status, dates, source, screening completion %, placement stage
- Use case: Fast pipeline overviews, candidate counting, basic filtering
- Performance: Fast - minimal data per candidate

#### `get_candidates_from_pipeline_for_evaluation(job_id, stage_filter=None)`
**LLM evaluation optimized**: Returns curated data perfect for candidate analysis.
- Returns: CV full text, screening answers, skills/experience, cover letters (no contact info)
- Use case: **Recommended for LLM candidate evaluation and analysis**
- Performance: Medium - fetches full profiles but excludes administrative noise

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

1. **Get high-level candidate overview (for counting/filtering):**
```python
# Returns basic info for all candidates - fast
candidates = get_candidates_from_pipeline("job_id")
```

2. **Get evaluation data for LLM analysis:**
```python
# Returns CV text, screening answers, skills (optimized for LLMs)
evaluation_data = get_candidates_from_pipeline_for_evaluation("job_id")
```

3. **Get detailed profile for specific candidates:**
```python
# Get complete profile including contact info and all metadata
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

### Function Quick Reference

| **Function** | **Use Case** | **Performance** | **Returns** |
|-------------|-------------|----------------|-------------|
| `get_candidates_from_pipeline()` | Counting, basic filtering | ⚡ Fast | 8 basic fields |
| `get_candidates_from_pipeline_for_evaluation()` | **LLM candidate analysis** | 🔄 Medium | 18 evaluation fields (no contact info) |
| `get_candidate_profile()` | Individual detailed analysis | 🐌 Slow | 80+ complete fields |

**💡 Recommendation**: Use `get_candidates_from_pipeline_for_evaluation()` for LLM-powered candidate evaluation.

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

- **Fast overview**: Use `get_candidates_from_pipeline()` for quick candidate counts and basic filtering
- **LLM evaluation**: Use `get_candidates_from_pipeline_for_evaluation()` for candidate analysis (no contact info noise)
- **Selective profiling**: Only call `get_candidate_profile()` for candidates you need complete details on
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