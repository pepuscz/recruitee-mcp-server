# Recruitee MCP Server

A Model Context Protocol (MCP) server for the Recruitee API that enables extraction of candidate profiles from recruitment pipelines. Features clean, purpose-built functions optimized for different use cases: basic overviews, LLM evaluation, and detailed analysis.

## Features

- **LLM Evaluation Optimized**: Clean, bias-free candidate data perfect for AI analysis
- **PDF Text Extraction**: Automatic CV and cover letter extraction using pdfplumber
- **Screening Questions**: Clean Q&A format for easy evaluation
- **Efficient Processing**: CV text processing configurable for performance optimization
- **Advanced Search**: Multi-criteria candidate filtering
- **Notes & Ratings**: Separate access to evaluator feedback

## Available Tools

### Core Tools

1. **`get_candidates_from_pipeline_for_evaluation`** - **Recommended for LLM analysis** - Clean evaluation data
2. **`get_candidate_profile`** - Complete candidate profile with all administrative data
3. **`search_candidates`** - Advanced candidate search with filtering
4. **`get_candidate_notes`** - Access notes, ratings, and evaluator feedback
5. **`list_jobs`** - List all available jobs/pipelines
6. **`get_job_details`** - Get detailed job information

### Tool Details

#### `get_candidates_from_pipeline_for_evaluation(job_id, stage_filter=None, include_full_cv=False)` ⭐ **Recommended**
**LLM evaluation optimized**: Clean, bias-free data perfect for candidate analysis.

**Parameters:**
- `job_id`: The job/pipeline ID (required)
- `stage_filter`: Optional stage name filter
- `include_full_cv`: Whether to include full CV text (default: False). Set to True to include full CV text - basic CV metadata always included.

**Returns:**
- CV full text extraction (PDF → text) - optional based on `include_full_cv` parameter
- Clean screening questions: `[{"question": "...", "answer": "...", "question_type": "text"}]`
- Flattened skills array: `["JavaScript", "React", "Node.js"]`
- Structured experience: `[{"company": "...", "title": "...", "description": "..."}]`
- Cover letter text
- Basic facts only: `has_degree`, `total_screening_questions`, `answered_questions`

#### `get_candidate_profile(candidate_id)`
**Complete candidate profile**: All candidate data including contact info, CV, cover letter, experience, and all custom fields.
- Returns: Full profile with contact info, CV/cover letter PDFs, custom fields, and full PDF text extraction
- Use case: Individual detailed review, contact information access, complete administrative data
- Performance: 🐌 Slow (comprehensive data + PDF processing)

#### `search_candidates(job_ids=None, stage_names=None, status=None, has_cv=None, has_cover_letter=None, limit=50, offset=0)`
**Advanced search**: Multi-criteria candidate filtering across all candidates.
- Returns: Filtered candidate list with pagination support
- Use case: Finding candidates by specific criteria, bulk operations
- Performance: 🔄 Medium (client-side filtering)

#### `get_candidate_notes(candidate_id)`
**Evaluator feedback**: Access to ratings, notes, and comments.
- Returns: Notes, ratings, comments from recruiters/interviewers
- Use case: Review evaluator feedback and scoring

#### `list_jobs()` and `get_job_details(job_id)`
**Job management**: List available jobs and get detailed job information.
- Returns: Job listings with metadata, stages, and requirements
- Use case: Discovering available positions, understanding job requirements

## Installation

```bash
# Install from source
git clone [repository-url]
cd recruitee-mcp-server
pip install -e .
```

## Configuration

```bash
export RECRUITEE_API_TOKEN="your-api-token" 
export RECRUITEE_COMPANY_ID="your-company-id"
```

## Usage

### Recommended Workflow

```python
# 1. Get clean evaluation data for LLM analysis (CV text excluded by default)
evaluation_data = get_candidates_from_pipeline_for_evaluation("job_id")

# 1a. For detailed analysis including CV text
evaluation_data = get_candidates_from_pipeline_for_evaluation("job_id", include_full_cv=True)

# 2. Get individual candidate details with full CV text (always included)
profile = get_candidate_profile("candidate_id")  # Complete administrative data

# 3. Review evaluator feedback separately  
notes = get_candidate_notes("candidate_id")

# 4. Get full administrative details only when needed (contact info, etc.)
full_profile = get_candidate_profile("candidate_id")  # Always returns full data
```

### Function Comparison

| **Function** | **Use Case** | **Fields** | **Performance** |
|-------------|-------------|------------|----------------|
| `get_candidates_from_pipeline_for_evaluation()` | **Pipeline LLM analysis** | 23 clean fields | 🔄 Medium |
| `get_candidate_profile()` | **Complete administrative data** | 80+ raw fields | 🐌 Slow |
| `search_candidates()` | Advanced filtering | Variable | 🔄 Medium |
| `get_candidate_notes()` | Evaluator feedback | Notes & ratings | ⚡ Fast |
| `list_jobs()` | Job/pipeline listing | Job metadata | ⚡ Fast |
| `get_job_details()` | Job information | Complete job data | ⚡ Fast |

## MCP Integration

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

## Performance Tips

- **Pipeline analysis**: Use `get_candidates_from_pipeline_for_evaluation()` (clean, optimized data)
- **Large datasets**: Keep `include_full_cv=False` (default) to skip CV text processing for better performance
- **Individual analysis**: Use `get_candidate_profile()` for complete administrative data with contact info
- **Evaluator feedback**: Use `get_candidate_notes()` for ratings/comments

## License

MIT License

---

> 💼 **Perfect for AI-powered recruitment tools and LLM candidate evaluation systems.** 