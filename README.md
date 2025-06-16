# Recruitee MCP Server

A Model Context Protocol (MCP) server for the Recruitee API that enables extraction of candidate profiles from recruitment pipelines. Features clean, purpose-built functions optimized for different use cases: basic overviews, LLM evaluation, and detailed analysis.

## Features

- **LLM Evaluation Optimized**: Clean, bias-free candidate data perfect for AI analysis
- **PDF Text Extraction**: Automatic CV and cover letter extraction using pdfplumber
- **Screening Questions**: Clean Q&A format for easy evaluation
- **Flexible Data Access**: Three functions for different needs (overview, evaluation, detailed)
- **Advanced Search**: Multi-criteria candidate filtering
- **Notes & Ratings**: Separate access to evaluator feedback

## Available Tools

### Core Tools

1. **`get_candidates_from_pipeline_for_evaluation`** - **Recommended for LLM analysis** - Clean evaluation data
2. **`get_candidates_from_pipeline`** - High-level candidate list for quick overviews
3. **`get_candidate_profile`** - Complete detailed profile for specific candidates
4. **`search_candidates`** - Advanced candidate search with filtering
5. **`get_candidate_notes`** - Access notes, ratings, and evaluator feedback
6. **`list_jobs`** - List all available jobs/pipelines
7. **`get_job_details`** - Get detailed job information

### Tool Details

#### `get_candidates_from_pipeline_for_evaluation(job_id, stage_filter=None)` ⭐ **Recommended**
**LLM evaluation optimized**: Clean, bias-free data perfect for candidate analysis.

**Returns:**
- CV full text extraction (PDF → text)
- Clean screening questions: `[{"question": "...", "answer": "...", "question_type": "text"}]`
- Flattened skills array: `["JavaScript", "React", "Node.js"]`
- Structured experience: `[{"company": "...", "title": "...", "description": "..."}]`
- Cover letter text
- Basic facts only: `has_degree`, `total_screening_questions`, `answered_questions`

**Key Features:**
- ✅ No contact information (privacy-safe)
- ✅ No bias-inducing metrics (counts, ratings)
- ✅ Clean Q&A format for screening questions
- ✅ Raw data for LLM assessment

#### `get_candidates_from_pipeline(job_id, stage_filter=None)`
**Quick overview**: Basic candidate information for filtering and counting.
- Returns: id, name, status, dates, source, screening completion %
- Use case: Fast pipeline overviews, candidate counting
- Performance: ⚡ Fast

#### `get_candidate_profile(candidate_id)`
**Complete profile**: All candidate data including contact information.
- Returns: Full profile with contact info, CV/cover letter PDFs, custom fields
- Use case: Individual detailed review, contact information access
- Performance: 🐌 Slow (comprehensive data)

#### `get_candidate_notes(candidate_id)`
**Evaluator feedback**: Access to ratings, notes, and comments.
- Returns: Notes, ratings, comments from recruiters/interviewers
- Use case: Review evaluator feedback and scoring

## Installation

```bash
# Clone and install
git clone <repository-url>
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
# 1. Get clean evaluation data for LLM analysis
evaluation_data = get_candidates_from_pipeline_for_evaluation("job_id")

# 2. Review evaluator feedback separately  
notes = get_candidate_notes("candidate_id")

# 3. Get full details only when needed
profile = get_candidate_profile("candidate_id")
```

### Function Comparison

| **Function** | **Use Case** | **Fields** | **Performance** |
|-------------|-------------|------------|----------------|
| `get_candidates_from_pipeline_for_evaluation()` | **LLM analysis** | 20 clean fields | 🔄 Medium |
| `get_candidates_from_pipeline()` | Quick overview | 8 basic fields | ⚡ Fast |
| `get_candidate_profile()` | Complete details | 80+ fields | 🐌 Slow |
| `get_candidate_notes()` | Evaluator feedback | Notes & ratings | ⚡ Fast |

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

- **LLM evaluation**: Use `get_candidates_from_pipeline_for_evaluation()` (clean, optimized data)
- **Quick filtering**: Use `get_candidates_from_pipeline()` for overview
- **Contact details**: Only use `get_candidate_profile()` when contact info needed
- **Evaluator feedback**: Use `get_candidate_notes()` for ratings/comments

## License

MIT License

---

> 💼 **Perfect for AI-powered recruitment tools and LLM candidate evaluation systems.** 