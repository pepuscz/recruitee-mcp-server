# Recruitee MCP Server

A comprehensive Model Context Protocol (MCP) server for the Recruitee API that enables extraction of candidate profiles from recruitment pipelines. Features advanced PDF text extraction capabilities combined with Recruitee's AI-parsed structured data for complete candidate analysis.

## ✨ Features

- **🔍 Comprehensive Candidate Extraction**: Access complete candidate data including contact details, CVs, cover letters, screening questions, experience, and custom fields
- **📄 Advanced PDF Text Extraction**: Extract full text content from CV and cover letter PDFs using pdfplumber
- **🏢 Pipeline-Based Filtering**: Extract candidates from specific job pipelines with server-side optimization
- **🎯 Intelligent Filtering**: Robust client-side filtering to work around API limitations
- **🤖 Dual Data Sources**: Combines Recruitee's AI-parsed structured data with complete PDF text extraction
- **🔒 Read-Only Operations**: Safe data extraction without modification capabilities
- **📊 Analytics Ready**: Built-in candidate analytics and pipeline statistics

## 🛠 Installation

```bash
git clone https://github.com/pepuscz/recruitee-mcp-server.git
cd recruitee-mcp-server

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## ⚙️ Configuration

### Get Recruitee API Credentials

1. Log in to Recruitee → **Settings** → **Apps and plugins** → **Personal API tokens**
2. Create new token and note your **Company ID** (found in Company Settings)

### Cursor/Claude Desktop Setup

Create your MCP configuration file with the following structure:

```json
{
  "mcpServers": {
    "recruitee": {
      "command": "python",
      "args": ["-m", "recruitee_mcp.server"],
      "env": {
        "RECRUITEE_API_TOKEN": "your_api_token_here",
        "RECRUITEE_COMPANY_ID": "your_company_id_here"
      }
    }
  }
}
```

**For Cursor**: Add this to Cursor Settings → MCP Servers
**For Claude Desktop**: Add this to your Claude Desktop configuration

## 🚀 Available Tools

### `get_candidates_from_pipeline`
Extract all candidates from a specific job pipeline with complete profiles.
- `job_id`: The job/pipeline ID (required)
- `include_full_profiles`: Fetch complete profiles with PDF extraction (default: true)
- `stage_filter`: Optional stage name filter

### `get_candidate_profile`  
Get comprehensive candidate details including full PDF text extraction.
- `candidate_id`: The candidate ID (required)

Returns complete profile with:
- Basic contact information
- **Full CV text** extracted from PDF
- **Cover letter content** from both API and PDF sources
- Screening question responses
- AI-parsed skills, experience, education
- Document URLs and metadata

### `search_candidates`
Search candidates with advanced client-side filtering.
- `job_ids`: Filter by specific job IDs
- `stage_names`: Filter by recruitment stages  
- `status`: Filter by status (Qualified, Disqualified, New)
- `has_cv`: Filter candidates with/without CV
- `has_cover_letter`: Filter candidates with/without cover letter
- `limit`/`offset`: Pagination controls

### `list_jobs`
List all available jobs/pipelines in your Recruitee account.

### `get_job_details`
Get detailed information about a specific job/pipeline.
- `job_id`: The job ID (required)

### `get_candidate_notes`
Get notes and comments for a candidate.
- `candidate_id`: The candidate ID (required)

### `get_candidates_basic`
Get basic candidate list for quick overview.
- `limit`: Number of candidates to return (default: 100)

### `extract_cv_text`
Extract full text from any PDF URL (utility function).
- `pdf_url`: Direct URL to PDF file

## 📊 Extracted Data

The server provides comprehensive candidate information combining multiple data sources:

### **Contact & Basic Info**
- Email addresses, phone numbers
- Address and location data
- Social media profiles and links
- Application status and stage information

### **Document Analysis**
- **CV/Resume**: Full text extraction + AI-parsed structure
- **Cover Letters**: Both API text and PDF extraction
- **Portfolio**: Additional document access

### **Screening & Assessment**
- Application form responses
- Screening question answers
- Custom field values
- Evaluation scores and notes

### **Professional Profile**
- **AI-Parsed Data**: Skills, experience, education, languages
- **Full Text Content**: Complete CV and cover letter text
- **Structured Fields**: All custom profile fields
- **Timeline Data**: Application history and stage progression

## 🔧 Technical Implementation

### Server-Side Optimization
Uses Recruitee's `/candidates?offer_id=` endpoint for efficient pipeline filtering, avoiding unreliable search endpoints.

### Dual PDF Extraction
1. **Recruitee AI Parsing**: Structured skills, experience, education data
2. **Full Text Extraction**: Complete PDF content using pdfplumber for comprehensive analysis

### Client-Side Filtering
Implements robust filtering as a workaround for API limitations:
- Fetches data using reliable endpoints
- Applies complex filters client-side
- Maintains consistent tool interface

## 💡 Usage Examples

```json
// Get all candidates from a specific job pipeline
{
  "tool": "get_candidates_from_pipeline", 
  "arguments": {"job_id": "12345", "include_full_profiles": true}
}

// Search candidates with CV in specific stage
{
  "tool": "search_candidates",
  "arguments": {
    "job_ids": ["12345"],
    "stage_names": ["Final Interview"],
    "has_cv": true
  }
}

// Get complete candidate profile with PDF extraction
{
  "tool": "get_candidate_profile",
  "arguments": {"candidate_id": "67890"}
}

// Extract text from any PDF document
{
  "tool": "extract_cv_text",
  "arguments": {"pdf_url": "https://example.com/cv.pdf"}
}
```

## 📈 Pipeline Analytics

The server automatically provides analytics for job pipelines:
- Candidate source breakdown
- Referrer analysis  
- Document coverage statistics
- Stage distribution
- Application timeline data

## 🔒 Security & Privacy

- **Read-only access**: No data modification capabilities
- **Environment variables**: Secure credential management
- **No data storage**: Processes data without persistence
- **API compliance**: Follows Recruitee API best practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🔗 Links

- **Repository**: [https://github.com/pepuscz/recruitee-mcp-server](https://github.com/pepuscz/recruitee-mcp-server)
- **Issues**: [https://github.com/pepuscz/recruitee-mcp-server/issues](https://github.com/pepuscz/recruitee-mcp-server/issues)
- **Recruitee API**: [https://docs.recruitee.com/](https://docs.recruitee.com/)
- **Model Context Protocol**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)

---

> 💼 **Perfect for recruitment teams, HR professionals, and developers building recruitment automation tools.** 