# GTM Strategy Document Generator

An automated system that generates comprehensive go-to-market strategy documents when a HubSpot deal reaches the "Meeting Booked" stage. The system enriches company data, runs deep research using OpenAI's "o3-deep-research" model, and creates fully formatted Google Docs with inline citations.

## Architecture Overview

### Data Flow
```
HubSpot Deal → Clay Enrichment → HubSpot Update → Cloud Function → OpenAI Deep Research → Google Doc
```

### Key Components
- **FastAPI Cloud Function**: Main service with `/generate`, `/patch`, and `/healthz` endpoints
- **OpenAI Deep Research**: Uses "o3-deep-research" model for comprehensive GTM analysis
- **Google Docs API**: Creates and patches documents with inline citations
- **GTM Framework**: JSON structure used as a thinking framework for consistent analysis

## GTM Framework Approach

The system uses a **GTM JSON structure as a thinking framework** rather than a data storage format. This ensures:

### **Consistent Analysis Across Companies**
The JSON structure serves as a mental model that forces the LLM to think systematically about:
1. **Business Model**: How does the company make money? (Subscription/Consumption/Hybrid/Ownership)
2. **Financing**: What's the capital structure? (VC backed/PE case/Bootstrapping)
3. **Market Maturity**: What stage is the market in? (Nascent/Growing/Mature/Declining)
4. **Products**: What are the core offerings and pricing models?
5. **ICPs**: Who are the ideal customers? What touch levels and activities work for each?
6. **Metrics**: What are the key performance indicators?

### **Direct Raw Data to Research**
Instead of trying to parse data into the JSON structure, the system:
1. Takes raw company data (HubSpot + Clay enrichment)
2. Uses the GTM framework as a prompt engineering tool
3. Generates comprehensive analysis directly from raw data
4. Ensures all GTM elements are covered systematically

### **Benefits**
- **No chicken-and-egg problem**: Works with any quality of GTM description
- **Consistent thinking**: Same analytical framework across all companies
- **Comprehensive coverage**: Guarantees all GTM aspects are analyzed
- **Flexible input**: Handles poor/missing data gracefully

## Quick Start

### 1. Environment Setup
```bash
# Clone and setup
git clone <repo>
cd gtm-strategy-doc
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Required Environment Variables
```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google (for document generation)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GS_TEMPLATE_DOC_ID=your_template_doc_id
GS_DRIVE_FOLDER_ID=your_drive_folder_id

# HubSpot (for production)
HUBSPOT_API_KEY=your_hubspot_api_key
HUBSPOT_PORTAL_ID=your_portal_id
```

### 3. Test the System
```bash
# Test the new GTM framework approach
python -m dev.mock_call --framework

# Test OpenAI-based parsing (legacy approach)
python -m dev.mock_call --parse

# Test full document generation (requires Google credentials)
python -m dev.mock_call --generate
```

### 4. Run the Service
```bash
# Development
python main.py

# Production (Cloud Run)
make deploy
```

## API Endpoints

### POST `/generate`
Generates a new GTM strategy document using the GTM framework approach.

**Request:**
```json
{
  "companyId": 15231,
  "stageTs": "2024-01-15T10:30:00Z",
  "company": {
    "id": 15231,
    "name": "TechCorp Solutions",
    "domain": "techcorp.com",
    "industry": "Software",
    "numberofemployees": 250,
    "annualrevenue": 50000000,
    "gtm_description": "TechCorp is a B2B SaaS company focused on enterprise workflow automation..."
  },
  "enriched_data": {
    "funding_rounds": [...],
    "total_funding": 35000000,
    "investors": ["Sequoia Capital", "Andreessen Horowitz"],
    "competitors": [...],
    "technologies": [...],
    "growth_metrics": {...}
  }
}
```

**Response:**
```json
{
  "status": "success",
  "doc_url": "https://docs.google.com/document/d/...",
  "revision_id": "revision_id",
  "processing_time": "completed"
}
```

### POST `/patch`
Applies patches to existing documents (future implementation).

### GET `/healthz`
Health check endpoint for Cloud Run.

## GTM Framework Structure

The system uses this JSON structure as a **thinking framework**:

```json
{
  "meta": {
    "schemaVersion": "1.3",
    "updatedAt": "ISO_8601_TIMESTAMP",
    "companyId": "COMPANY_ID"
  },
  "companyOverview": {
    "businessModel": {
      "description": "High-level summary of how the company makes money",
      "types": ["Subscription", "Consumption / pay per use", "Subscription / consumption hybrid", "Ownership"]
    },
    "financing": {
      "types": ["VC backed", "PE case", "Bootstrapping"]
    },
    "globalMetrics": {
      "arr": "TOTAL_ARR_IN_BASE_CURRENCY",
      "acv": "AVERAGE_CONTRACT_VALUE_ACROSS_ALL_DEALS",
      "yoyGrowthRate": "TARGET_YOY_GROWTH_AS_PERCENTAGE"
    },
    "marketMaturity": "Nascent | Growing | Mature | Declining"
  },
  "products": [
    {
      "id": "product_id",
      "name": "Product Name",
      "coreDescription": "One-sentence elevator pitch",
      "basePricingModel": "Subscription | Hybrid | Consumption",
      "modules": ["Module A", "Module B"]
    }
  ],
  "icps": [
    {
      "id": "icp_id",
      "description": "Short description: industry / size / geo",
      "vertical": "Industry",
      "employeeRanges": "e.g. 200-2,000",
      "regions": "Region list, e.g. DACH, US",
      "gtmMotion": {
        "touchLevels": ["no touch", "low touch", "medium touch", "high touch"],
        "activityTypes": ["Inbound", "Outbound", "Partner"]
      },
      "metrics": {
        "acv": "ACV_FOR_THIS_ICP",
        "numberOfDealsWonPerYear": "CLOSED_WON_DEALS_LAST_12_MONTHS"
      },
      "productsApplied": ["product_id"]
    }
  ],
  "definitions": [
    {"metric": "ARR", "definition": "Annual recurring revenue"},
    {"metric": "ACV", "definition": "Average contract value"}
  ],
  "stakeholderInfo": "Key internal & customer stakeholders",
  "other": "Any additional context not captured elsewhere"
}
```

## Document Sections

The generated document includes these sections:

- **DOC_TITLE**: Document title with company name
- **INTRO**: Executive summary and overview
- **PRICING_PACKAGING**: Pricing strategy and packaging approach
- **GTM_MOTION**: Go-to-market strategy and customer acquisition
- **TOUCH_MODEL**: Customer engagement and sales process
- **ICP**: Ideal customer profile analysis
- **METRICS**: Key performance indicators and measurement
- **FINANCIALS**: Financial metrics and projections
- **FINANCING**: Capital structure and funding strategy
- **MARKET_MATURITY**: Market analysis and competitive positioning
- **STAKEHOLDERS**: Key decision makers and influencers
- **SUMMARY_TABLE**: Executive summary table

## Development

### Project Structure
```
gtm-strategy-doc/
├── config/                 # Configuration files
│   ├── hubspot_properties.py
│   └── prompts.py
├── models/                 # Pydantic models
│   └── gtm_context.py
├── services/              # External service integrations
│   ├── clay_service.py
│   ├── google_docs_service.py
│   ├── hubspot_service.py
│   └── openai_service.py
├── utils/                 # Utilities
│   └── idempotency.py
├── dev/                   # Development tools
│   └── mock_call.py
├── tests/                 # Tests
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
└── Dockerfile           # Container configuration
```

### Testing
```bash
# Run all tests
python -m pytest

# Test specific functionality
python -m dev.mock_call --framework  # Test GTM framework approach
python -m dev.mock_call --parse      # Test OpenAI parsing
python -m dev.mock_call --generate   # Test full generation
```

### Deployment
```bash
# Deploy to Cloud Run
make deploy

# Or manually
gcloud run deploy gtm-strategy-doc \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

### HubSpot Properties
Configure which HubSpot properties to track in `config/hubspot_properties.py`.

### OpenAI Prompts
Customize prompts and section descriptions in `config/prompts.py`.

### Winning-by-Design Principles
The system incorporates Winning-by-Design Revenue Architecture framework for consistent GTM analysis.

## Monitoring & Alerts

- **Idempotency**: Prevents duplicate processing
- **Retries**: Automatic retry on failures
- **Logging**: Comprehensive logging for debugging
- **Health Checks**: `/healthz` endpoint for monitoring

## Future Enhancements

- [ ] Document patching functionality
- [ ] Slack integration for alerts
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Custom template support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license here] 