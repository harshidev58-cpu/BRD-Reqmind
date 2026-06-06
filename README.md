# 🎯 ReqMind AI - Alignment Intelligence System

> AI-powered system that converts multi-channel stakeholder communication into structured requirements and evaluates project alignment by detecting conflicts, volatility, and stakeholder disagreement.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### Core Capabilities
- **Multi-Channel Ingestion**: Email, Slack, Meeting transcripts
- **Alignment Intelligence**: Real-time conflict detection and risk assessment
- **Automated BRD Generation**: Structured Business Requirements Documents
- **Dataset Processing**: Enron emails, AMI meeting transcripts
- **Early Warning System**: HIGH/MEDIUM/LOW risk classification

### 🆕 Production Features (New!)

#### 1. User Instruction Layer (Gemini Integration)
Convert natural language instructions into structured constraints for intelligent data filtering and prioritization. Simply tell the system what to focus on, what to ignore, and what to prioritize - no complex configuration needed.

**Key Benefits:**
- Filter out irrelevant discussions (e.g., "ignore marketing discussions")
- Focus on specific project phases (e.g., "focus only on MVP")
- Override deadlines with natural language (e.g., "client deadline is June 2024")
- Prioritize specific areas (e.g., "prioritize mobile features")

#### 2. Large Data Handling (Automatic Chunking)
Automatically handles large meeting transcripts and documents exceeding 3000 words without hitting token limits. The system intelligently splits content, processes each chunk, and aggregates results with deduplication.

**Key Benefits:**
- Process meetings of any length (tested up to 10 hours)
- Maintains context with overlapping chunks
- Preserves sentence boundaries (no mid-sentence splits)
- Automatic aggregation with duplicate removal
- Completely transparent to the client

#### 3. Ingestion Transparency (Explainability)
Track and report exactly what data sources were analyzed to generate the BRD. Provides full visibility into the analysis process with counts, samples, and processing metrics.

**Key Benefits:**
- Verify which sources contributed to the BRD
- Audit trail for compliance requirements
- Debug unexpected results
- Understand processing performance
- Representative samples for quick review

### Alignment Analysis
- ✅ Stakeholder agreement detection
- ✅ Timeline consistency analysis
- ✅ Requirement stability tracking
- ✅ Decision volatility measurement
- ✅ Conflict detection with recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/reqmind-ai.git
cd reqmind-ai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Start the backend**
```bash
uvicorn app.main:app --reload
```

6. **Start the frontend** (in a new terminal)
```bash
streamlit run frontend/app_enterprise.py --server.headless true
```

7. **Access the application**
- Backend API: http://127.0.0.1:8000
- Frontend Dashboard: http://localhost:8502
- API Docs: http://127.0.0.1:8000/docs

## 📊 Architecture

```
┌─────────────────────────┐
│  Streamlit Frontend     │ :8502
│  - Dashboard            │
│  - Data Sources         │
│  - Alignment Analysis   │
└────────────┬────────────┘
             │ HTTP
             ▼
┌─────────────────────────┐
│   FastAPI Backend       │ :8000
│   - Alignment Engine    │
│   - BRD Generator       │
│   - Dataset Loaders     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Groq API (LLM)        │
│   - Text Analysis       │
│   - Requirement Extract │
└─────────────────────────┘
```

## 🎯 Usage

### 1. Enterprise Dashboard

Navigate to http://localhost:8502 and:
1. Go to **Data Sources**
2. Click **"Load Sample Dataset"** for demo
3. Click **"Analyze Alignment"**
4. View results with alignment score, conflicts, and recommendations

### 2. API Usage

```bash
curl -X POST "http://127.0.0.1:8000/generate_brd_with_alignment" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "My Project",
    "emailText": "PM: Delivery by March 30",
    "slackText": "Client: Need delivery by April 10"
  }'
```

### 3. Dataset Mode

```bash
curl -X POST "http://127.0.0.1:8000/dataset/generate_brd_from_dataset" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "Trading System",
    "keywords": ["trading", "system", "security"],
    "sampleSize": 20
  }'
```

## 📁 Project Structure

```
reqmind-ai/
├── app/                          # Backend API
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Configuration
│   ├── models/                   # Pydantic models
│   ├── services/
│   │   ├── alignment_intelligence.py  # Alignment engine
│   │   ├── brd_generator.py          # BRD generation
│   │   ├── dataset_loaders.py        # Dataset processing
│   │   └── multi_channel_ingestion.py
│   ├── routers/                  # API endpoints
│   └── utils/                    # Utilities
├── frontend/                     # Streamlit UI
│   ├── app.py                    # Simple dashboard
│   └── app_enterprise.py         # Enterprise SaaS UI
├── tests/                        # Test suite
├── datasets/                     # Sample datasets (gitignored)
├── .env.example                  # Environment template
└── requirements.txt              # Dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# API Configuration
OPENAI_API_KEY=your_groq_api_key_here
OPENAI_MODEL=llama-3.3-70b-versatile
OPENAI_BASE_URL=https://api.groq.com/openai/v1
PORT=8000

# Dataset Configuration (Optional)
DATASET_MODE_ENABLED=false
EMAIL_DATASET_PATH=./datasets/enron_emails.csv
MEETING_DATASET_PATH=./datasets/ami_transcripts/
MAX_DATASET_EMAILS=1000
MAX_DATASET_MEETINGS=100
DATASET_SAMPLE_SIZE=50

# 🆕 Production Features Configuration
# Gemini API (for User Instruction Layer)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro
GEMINI_TIMEOUT=10
GEMINI_MAX_RETRIES=2

# Chunking Configuration (for Large Data Handling)
CHUNK_THRESHOLD_WORDS=3000
CHUNK_SIZE_MIN=1000
CHUNK_SIZE_MAX=1500
CHUNK_OVERLAP=100

# Tracking Configuration (for Ingestion Transparency)
SAMPLE_SOURCES_COUNT=5
TRACKING_SESSION_TTL=3600
```

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate_brd` | POST | Generate standard BRD |
| `/generate_brd_with_alignment` | POST | BRD + Alignment analysis |
| `/generate_brd_with_context` | POST | 🆕 BRD + Context-aware processing with instructions |
| `/dataset/generate_brd_from_dataset` | POST | Dataset-based generation |
| `/dataset/dataset_status` | GET | Dataset configuration |

### 🆕 New Context-Aware Endpoint

The `/generate_brd_with_context` endpoint provides advanced features:

**Request Example:**
```bash
curl -X POST "http://127.0.0.1:8000/generate_brd_with_context" \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "Focus only on MVP features and ignore marketing discussions",
    "data": {
      "emails": [
        {
          "subject": "MVP scope",
          "body": "Core features needed...",
          "sender": "pm@company.com",
          "date": "2024-02-15"
        }
      ],
      "slack_messages": [],
      "meetings": []
    }
  }'
```

**Key Features:**
- **User Instructions**: Natural language filtering and prioritization
- **Automatic Chunking**: Handles large texts (>3000 words) automatically
- **Ingestion Summary**: Detailed tracking of data sources used

**Response includes:**
```json
{
  "brd": { /* Standard BRD structure */ },
  "alignment_analysis": { /* Alignment scores and conflicts */ },
  "ingestion_summary": {
    "emails_used": 12,
    "slack_messages_used": 45,
    "meetings_used": 3,
    "total_chunks_processed": 8,
    "total_words_processed": 15420,
    "processing_time_seconds": 12.5,
    "sample_sources": [ /* 3-5 representative samples */ ]
  }
}
```

### Example Response

```json
{
  "brd": {
    "projectName": "...",
    "executiveSummary": "...",
    "requirements": [...]
  },
  "alignment_analysis": {
    "alignment_score": 85.0,
    "risk_level": "LOW",
    "alert": "Project alignment is stable",
    "conflicts": [],
    "timeline_mismatches": [],
    "component_scores": {
      "stakeholder_agreement": 100.0,
      "timeline_consistency": 85.0,
      "requirement_stability": 100.0,
      "decision_volatility": 100.0
    }
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_alignment_intelligence.py

# Run test scripts
python test_alignment_intelligence.py
python test_dataset_features.py
```

## 🎨 Frontend Features

### Enterprise Dashboard
- **Modern SaaS Design**: Dark theme with gradients
- **OAuth Simulation**: Gmail/Slack integration demo
- **Auto-Ingestion**: No manual pasting required
- **Real-time Analysis**: Fast processing with Groq
- **Export Capability**: Download JSON results

### Pages
1. **Dashboard**: Metrics overview and recent activity
2. **Data Sources**: Integration management
3. **Alignment Analysis**: Detailed results and insights
4. **BRD History**: Analysis archive
5. **Settings**: Configuration and preferences

## 📈 Alignment Scoring

```
Alignment Score = 100 
  - (conflicts × 10)
  - (timeline_mismatches × 15)
  - (requirement_changes × 5)
  - (decision_reversals × 8)
```

### Risk Levels
- **HIGH** (< 70): Immediate review required
- **MEDIUM** (70-85): Monitor changes closely
- **LOW** (> 85): Stable alignment

---

## 🚀 Production Features Guide

### 1. User Instruction Layer (Gemini Integration)

Convert natural language instructions into structured constraints for intelligent data filtering and prioritization. This feature uses Google's Gemini API to understand your instructions and automatically filter/prioritize your data sources.

#### Setup

1. **Get a Gemini API key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key

2. **Configure environment**
   ```bash
   # Add to your .env file
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-pro
   GEMINI_TIMEOUT=10
   GEMINI_MAX_RETRIES=2
   ```

#### Usage Examples

**Basic filtering:**
```bash
curl -X POST "http://127.0.0.1:8000/generate_brd_with_context" \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "Focus on MVP features only",
    "data": {
      "emails": [
        {"subject": "MVP scope", "body": "Core features..."},
        {"subject": "Future enhancements", "body": "Phase 2 features..."}
      ]
    }
  }'
```

**Advanced filtering with multiple constraints:**
```bash
curl -X POST "http://127.0.0.1:8000/generate_brd_with_context" \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "Focus on MVP features, exclude marketing discussions, prioritize mobile features, client deadline is June 2024",
    "data": { /* your data */ }
  }'
```

#### How It Works

1. **Instruction Parsing**: Gemini API converts your natural language to structured constraints:
   ```json
   {
     "scope": "MVP features only",
     "exclude_topics": ["marketing", "phase 2", "future enhancements"],
     "priority_focus": "mobile features",
     "deadline_override": "June 2024"
   }
   ```

2. **Data Filtering**: System applies constraints:
   - Removes items containing excluded topics
   - Filters content to match scope
   - Prioritizes items matching focus areas

3. **Graceful Fallback**: If Gemini API fails:
   - System logs the error
   - Continues processing without constraints
   - Returns successful BRD (no user impact)

#### Example Instructions

| Instruction | Effect |
|-------------|--------|
| "Focus only on Phase 1" | Filters to Phase 1 content only |
| "Ignore marketing discussions" | Removes marketing-related items |
| "Prioritize mobile features" | Ranks mobile content higher |
| "Client deadline is June 2024" | Overrides timeline in BRD |
| "Exclude internal team discussions" | Removes internal-only content |

#### Performance

- **API Call**: < 2 seconds
- **Retry Logic**: 2 retries with exponential backoff
- **Timeout**: 10 seconds
- **Fallback**: Automatic if Gemini unavailable

---

### 2. Large Data Handling (Automatic Chunking)

Automatically handles large meeting transcripts and documents without token limit issues. The system detects large texts, intelligently splits them into processable chunks, and aggregates results seamlessly.

#### Configuration

```env
# Add to your .env file
CHUNK_THRESHOLD_WORDS=3000    # Trigger chunking above this word count
CHUNK_SIZE_MIN=1000           # Minimum chunk size in words
CHUNK_SIZE_MAX=1500           # Maximum chunk size in words
CHUNK_OVERLAP=100             # Overlap between chunks for context
```

#### How It Works

1. **Detection**: System counts words in each text
   - If > 3000 words → automatic chunking
   - If ≤ 3000 words → process normally

2. **Intelligent Splitting**:
   - Splits at sentence boundaries (no mid-sentence cuts)
   - Maintains 100-word overlap between chunks
   - Preserves speaker context in meeting transcripts
   - Each chunk: 1000-1500 words

3. **Processing**:
   - Each chunk processed independently
   - Extracts: requirements, decisions, stakeholders, timelines

4. **Aggregation**:
   - Combines results from all chunks
   - Deduplicates requirements (>80% similarity)
   - Merges stakeholder lists
   - Resolves timeline conflicts

#### Usage Example

**No client-side changes needed** - chunking is automatic:

```bash
curl -X POST "http://127.0.0.1:8000/generate_brd_with_context" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "meetings": [
        {
          "transcript": "... 5000 word transcript ...",
          "topic": "Technical Architecture Review",
          "speakers": ["PM", "Tech Lead", "Architect"]
        }
      ]
    }
  }'
```

**Response includes chunking details:**
```json
{
  "brd": { /* Generated BRD */ },
  "alignment_analysis": { /* Alignment scores */ },
  "ingestion_summary": {
    "meetings_used": 1,
    "total_chunks_processed": 4,      // Automatically chunked into 4 parts
    "total_words_processed": 5000,
    "processing_time_seconds": 18.5
  }
}
```

#### Chunking Algorithm

```
Example: 5000-word meeting transcript

Step 1: Detect threshold exceeded (5000 > 3000)
Step 2: Calculate chunks needed (≈4 chunks)
Step 3: Split with overlap:
  - Chunk 1: words 0-1500
  - Chunk 2: words 1400-2900 (100-word overlap)
  - Chunk 3: words 2800-4300 (100-word overlap)
  - Chunk 4: words 4200-5000 (100-word overlap)
Step 4: Process each chunk independently
Step 5: Aggregate and deduplicate results
```

#### Benefits

- **No Token Limits**: Process meetings of any length
- **Context Preservation**: Overlapping chunks maintain continuity
- **Quality**: Sentence boundaries prevent information loss
- **Transparency**: Chunk count tracked in response
- **Performance**: Parallel processing potential

#### Performance

- **Chunking Speed**: < 1 second per 10,000 words
- **Overhead**: Minimal (< 100ms)
- **Tested**: Up to 10-hour meeting transcripts

---

### 3. Ingestion Transparency (Explainability)

Track and report exactly what data sources were analyzed to generate the BRD. Provides complete visibility into the analysis process with detailed metrics and representative samples.

#### Configuration

```env
# Add to your .env file
SAMPLE_SOURCES_COUNT=5        # Number of sample sources to include
TRACKING_SESSION_TTL=3600     # Session expiration in seconds (1 hour)
```

#### What's Tracked

**Counts:**
- Number of emails processed
- Number of Slack messages processed
- Number of meetings processed
- Total chunks created from large texts
- Total word count across all sources
- Processing time in seconds

**Sample Sources:**
- 3-5 representative samples from each source type
- Includes metadata for verification and debugging

#### Sample Metadata by Type

| Source Type | Metadata Included |
|-------------|-------------------|
| **Email** | subject, date, sender |
| **Slack** | channel, user, timestamp, preview (first 50 chars) |
| **Meeting** | timestamp, topic, speakers list |

#### Usage Example

**Standard request** - tracking is automatic:

```bash
curl -X POST "http://127.0.0.1:8000/generate_brd_with_context" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "emails": [
        {"subject": "Q1 Deadline", "body": "...", "sender": "pm@company.com", "date": "2024-02-15"},
        {"subject": "Feature Request", "body": "...", "sender": "client@company.com", "date": "2024-02-16"}
      ],
      "slack_messages": [
        {"channel": "#project-alpha", "user": "sarah.dev", "text": "...", "timestamp": "2024-02-15 14:30"}
      ],
      "meetings": [
        {"transcript": "...", "topic": "Sprint Planning", "speakers": ["PM", "Dev Lead"]}
      ]
    }
  }'
```

#### Response Format

**Complete ingestion summary:**
```json
{
  "brd": { /* Generated BRD */ },
  "alignment_analysis": { /* Alignment analysis */ },
  "ingestion_summary": {
    "emails_used": 12,
    "slack_messages_used": 45,
    "meetings_used": 3,
    "total_chunks_processed": 8,
    "total_words_processed": 15420,
    "processing_time_seconds": 12.5,
    "sample_sources": [
      {
        "type": "email",
        "metadata": {
          "subject": "Deadline discussion",
          "date": "2024-02-12",
          "sender": "john.pm@company.com"
        }
      },
      {
        "type": "meeting",
        "metadata": {
          "timestamp": "01:15:30",
          "topic": "API dependency risk",
          "speakers": ["PM", "Tech Lead"]
        }
      },
      {
        "type": "slack",
        "metadata": {
          "channel": "#project-alpha",
          "user": "sarah.dev",
          "timestamp": "2024-02-15 14:30",
          "preview": "We need to prioritize mobile features for MVP..."
        }
      }
    ]
  }
}
```

#### Use Cases

**1. Verification**
- Confirm the right sources were analyzed
- Verify no important sources were missed
- Check data coverage across channels

**2. Debugging**
- Understand why certain requirements appeared
- Trace back to original source discussions
- Identify gaps in data collection

**3. Compliance & Audit**
- Document what data was used
- Provide audit trail for decisions
- Meet regulatory requirements

**4. Performance Monitoring**
- Track processing times
- Identify bottlenecks
- Optimize data collection

#### Sample Selection

- **Random sampling** with reproducible seed
- **Representative distribution** across source types
- **Metadata only** (no full content for privacy)
- **Configurable count** (default: 5 samples)

#### Benefits

- **Full Transparency**: Know exactly what was analyzed
- **Audit Trail**: Complete record of data sources
- **Debugging**: Trace unexpected results to sources
- **Verification**: Confirm data quality and coverage
- **Performance Insights**: Monitor processing metrics

---

### Combined Features Example

Here's how all three production features work together in a real-world scenario:

```bash
curl -X POST "http://127.0.0.1:8000/generate_brd_with_context" \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "Focus on MVP features only, exclude marketing discussions, prioritize mobile functionality",
    "data": {
      "emails": [
        {"subject": "MVP Requirements", "body": "Core features needed for launch...", "sender": "pm@company.com", "date": "2024-02-10"},
        {"subject": "Marketing Strategy", "body": "Social media campaign...", "sender": "marketing@company.com", "date": "2024-02-11"},
        {"subject": "Mobile Features", "body": "iOS and Android requirements...", "sender": "mobile-lead@company.com", "date": "2024-02-12"}
      ],
      "slack_messages": [
        {"channel": "#mvp-planning", "user": "sarah.dev", "text": "Mobile app needs offline mode", "timestamp": "2024-02-13 10:30"},
        {"channel": "#marketing", "user": "john.marketing", "text": "Launch event planning", "timestamp": "2024-02-13 11:00"}
      ],
      "meetings": [
        {
          "transcript": "... 4500 word technical architecture discussion covering mobile app design, API requirements, database schema, security considerations, and deployment strategy ...",
          "topic": "Technical Architecture Review",
          "speakers": ["PM", "Tech Lead", "Mobile Lead", "Architect"],
          "timestamp": "2024-02-14"
        }
      ]
    }
  }'
```

**What Happens:**

1. **User Instruction Layer** (Gemini):
   - Converts instructions to constraints
   - Filters out marketing email and Slack message
   - Prioritizes mobile-related content
   - Keeps MVP-focused items

2. **Large Data Handling** (Chunking):
   - Detects 4500-word meeting transcript
   - Splits into 3 chunks (1500 words each with overlap)
   - Processes each chunk independently
   - Aggregates results with deduplication

3. **Ingestion Transparency** (Tracking):
   - Tracks: 2 emails used (1 filtered out)
   - Tracks: 1 Slack message used (1 filtered out)
   - Tracks: 1 meeting, 3 chunks processed
   - Provides samples from each source type

**Response:**
```json
{
  "brd": {
    "projectName": "Mobile MVP",
    "executiveSummary": "Mobile-first MVP focusing on core functionality...",
    "requirements": [
      "Mobile app with offline mode",
      "iOS and Android support",
      "API integration for data sync",
      /* ... prioritized mobile features ... */
    ]
  },
  "alignment_analysis": {
    "alignment_score": 88.0,
    "risk_level": "LOW",
    "conflicts": []
  },
  "ingestion_summary": {
    "emails_used": 2,              // Marketing email filtered out
    "slack_messages_used": 1,      // Marketing message filtered out
    "meetings_used": 1,
    "total_chunks_processed": 3,   // Large meeting chunked
    "total_words_processed": 4500,
    "processing_time_seconds": 15.2,
    "sample_sources": [
      {
        "type": "email",
        "metadata": {
          "subject": "Mobile Features",
          "date": "2024-02-12",
          "sender": "mobile-lead@company.com"
        }
      },
      {
        "type": "slack",
        "metadata": {
          "channel": "#mvp-planning",
          "user": "sarah.dev",
          "timestamp": "2024-02-13 10:30",
          "preview": "Mobile app needs offline mode"
        }
      },
      {
        "type": "meeting",
        "metadata": {
          "timestamp": "2024-02-14",
          "topic": "Technical Architecture Review",
          "speakers": ["PM", "Tech Lead", "Mobile Lead", "Architect"]
        }
      }
    ]
  }
}
```

**Key Outcomes:**
- ✅ Irrelevant marketing content filtered out
- ✅ Mobile features prioritized in BRD
- ✅ Large meeting processed without token limits
- ✅ Complete transparency on what was analyzed
- ✅ Fast processing with intelligent chunking

---

### Rate Limiting

The context-aware endpoint has rate limiting:
- **Limit**: 10 requests per minute per IP
- **Response**: 429 Too Many Requests if exceeded
- **Solution**: Implement delays between requests or contact support for higher limits

---

### Troubleshooting

#### Gemini API Issues

**Problem**: "Gemini API timeout" or "Constraint generation failed"
```
Solution: System automatically falls back to processing without constraints.
No action needed - BRD will still be generated successfully.
```

**Problem**: "Invalid Gemini API key"
```
Solution:
1. Verify GEMINI_API_KEY in .env file
2. Check key is active at https://makersuite.google.com/app/apikey
3. Restart the backend server
```

**Problem**: Rate limit exceeded
```
Solution:
1. Reduce request frequency
2. Implement caching for identical instructions
3. Consider upgrading Gemini API quota
```

#### Chunking Issues

**Problem**: "Chunking failed" error
```
Solution: System automatically processes text as single chunk.
Check logs for details. Usually caused by malformed text.
```

**Problem**: Chunks seem too small/large
```
Solution: Adjust configuration in .env:
CHUNK_SIZE_MIN=1000
CHUNK_SIZE_MAX=1500
CHUNK_OVERLAP=100
```

**Problem**: Context lost between chunks
```
Solution: Increase CHUNK_OVERLAP value (default: 100 words)
Higher overlap = better context but slower processing
```

#### Tracking Issues

**Problem**: Ingestion summary missing or incomplete
```
Solution:
1. Check TRACKING_SESSION_TTL (default: 3600 seconds)
2. Verify request completed successfully
3. Check logs for tracking errors
Note: Tracking failures don't block BRD generation
```

**Problem**: Sample sources don't match expectations
```
Solution: Samples are randomly selected. To get different samples:
1. Adjust SAMPLE_SOURCES_COUNT in .env
2. Re-run the request (random seed changes)
```

#### General Issues

**Problem**: Slow response times
```
Possible causes:
1. Large texts requiring chunking (expected)
2. Gemini API latency (check GEMINI_TIMEOUT)
3. Network issues

Solutions:
- Monitor processing_time_seconds in response
- Check total_chunks_processed (more chunks = longer time)
- Consider async processing for very large datasets
```

**Problem**: Unexpected filtering results
```
Solution:
1. Review instructions - be specific
2. Check ingestion_summary to see what was filtered
3. Try without instructions to see unfiltered results
4. Refine instructions based on results
```

---

### Backward Compatibility

All existing endpoints continue to work unchanged:
- `/generate_brd` - Standard BRD generation
- `/generate_brd_with_alignment` - BRD with alignment analysis

The new `/generate_brd_with_context` endpoint is fully backward compatible:
- Works without instructions (behaves like standard endpoint)
- Adds optional features when instructions are provided
- Always includes ingestion summary

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for fast LLM inference
- **FastAPI** for the backend framework
- **Streamlit** for the frontend framework
- **Enron Email Dataset** for testing
- **AMI Meeting Corpus** for transcript analysis

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🔗 Links

- [Documentation](./ALIGNMENT_INTELLIGENCE.md)
- [API Docs](http://127.0.0.1:8000/docs)
- [🆕 Production Features API Documentation](./docs/API_DOCUMENTATION.md)
- [Enterprise Frontend Guide](./frontend/ENTERPRISE_README.md)
- [Quick Start Guide](./QUICKSTART.md)

---

**Built with ❤️ for better project alignment**
