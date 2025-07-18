"""
OpenAI Prompts Configuration

This file contains all prompts used for generating GTM strategy documents.
Prompts can be easily modified here for testing and iteration.
"""

# System prompt for the main deep-research call
SYSTEM_PROMPT = """You are a senior GTM analyst using Winning-by-Design methodology. 
You specialize in creating comprehensive go-to-market strategies for B2B SaaS companies. 
Your analysis should be data-driven, strategic, and actionable. 

You must follow these principles:
- Use inline markdown links for every claim and citation
- Each section should be 200-400 words and provide specific, actionable insights
- Focus on describing the client's current GTM strategy, not proposing new ideas
- Leverage publicly available information and clearly note any inferred/estimated points
- Use Winning-by-Design Revenue Architecture framework
- Write in a professional, analytical tone suitable for business strategy documents
- Analyze the structured GTM context provided (business model, ICPs, products, metrics)
- Connect insights across sections to show how GTM elements work together
"""

# Enhanced section descriptions that leverage the structured GTM context
SECTION_DESCRIPTIONS = {
    "DOC_TITLE": "Company name + 'Go-To-Market Strategy Overview'",
    
    "INTRO": """Brief company overview (1-2 sentences) + purpose statement explaining this document describes the company's current GTM strategy using Winning-by-Design's Revenue Architecture framework. Should cover pricing model, GTM motions, customer engagement approach, ICP, key metrics, financing, market maturity, and stakeholders. Focus on status quo, not new proposals. Reference the business model type and market maturity from the structured context.""",
    
    "PRICING_PACKAGING": """Detailed analysis of the company's revenue model including:
- Pricing structure based on the business model type (Subscription, Consumption, Hybrid, Ownership)
- Package offerings and service bundles for each product
- Pricing transparency and commitment levels
- Volume discounts and enterprise pricing
- Value-based packaging considerations
- How revenue grows with customer usage
- Connection to the global metrics (ARR, ACV) provided in the structured context
- Analysis of pricing model alignment with ICP needs""",
    
    "GTM_MOTION": """Comprehensive analysis of sales motion and channels including:
- Product-Led Growth (PLG) components and self-service capabilities
- Sales-Led Growth (SLG) for enterprise segments
- Inbound marketing strategies and content approach
- Partnership channels and integrations
- Marketplace dynamics if applicable
- How the dual motion strategy works together
- Analysis of touch levels and activity types from the structured ICP data
- Connection between GTM motion and business model type""",
    
    "TOUCH_MODEL": """Customer engagement and ownership model analysis including:
- No-touch/self-service customer segments
- Low-touch (tech-enabled) engagement for mid-market
- High-touch (dedicated) engagement for enterprise
- Customer journey mapping and ownership assignment
- How touch levels align with customer segments from the structured ICP data
- Real-time updates and transparency features
- Analysis of touch model efficiency based on ICP metrics (ACV, deals won per year)
- Connection between touch model and business model complexity""",
    
    "ICP": """Ideal Customer Profile analysis including:
- Primary industry verticals and use cases from the structured ICP data
- Company size ranges and characteristics (employee ranges)
- Geographic considerations and market reach (regions)
- Behavioral traits and pain points
- Technology adoption patterns
- How ICP segments map to different touch models and GTM motions
- Analysis of ICP metrics (ACV, deals won per year) and what they indicate
- Connection between ICP characteristics and product offerings""",
    
    "METRICS": """Growth and attainment metrics including:
- Customer adoption and growth rates
- Transaction volume and usage metrics
- Revenue growth and diversification
- Customer retention and expansion rates
- Sales efficiency and pipeline metrics
- Operational metrics and success rates
- Growth goals and targets
- Analysis of the global metrics provided (ARR, ACV, YoY growth rate)
- Connection between metrics and business model performance
- ICP-specific metrics and their implications""",
    
    "FINANCIALS": """Financial metrics and performance including:
- Annual Recurring Revenue (ARR) analysis from the structured context
- Average Contract/Customer Value (ACV) analysis
- Gross margins and unit economics
- Cash burn and runway considerations
- ARR growth rates and trends
- LTV/CAC ratios and payback periods
- Financial health indicators
- Connection between financial metrics and business model type
- Analysis of financing structure impact on GTM strategy""",
    
    "FINANCING": """Financing and capital structure including:
- Funding history and rounds from enriched data
- Investor composition and strategic value
- Ownership structure and stakeholder roles
- Use of funds and growth initiatives
- Financial stage and runway
- Strategic financing approach
- Connection between financing type and GTM strategy
- Analysis of how funding enables different GTM motions""",
    
    "MARKET_MATURITY": """Market maturity and strategic position including:
- Traditional market vs. disruption analysis
- Market size and growth potential
- Competition and alternatives from enriched data
- Market maturity stage assessment (Nascent/Growing/Mature/Declining)
- Strategic positioning and differentiation
- Challenges and market education needs
- Network effects and moats
- Connection between market maturity and GTM strategy choices
- Analysis of how market stage affects ICP targeting""",
    
    "STAKEHOLDERS": """Key stakeholders and leadership including:
- Founder and executive team roles
- Key executives and their responsibilities
- Board composition and investor representatives
- Leadership transition and organizational structure
- Strategic decision-making framework
- Company culture and growth management
- Connection between stakeholder structure and GTM execution
- Analysis of how leadership influences GTM strategy""",
    
    "SUMMARY_TABLE": """A comprehensive summary table with columns:
| Element | Strategy | Metrics | Timeline |
|---------|----------|---------|----------|
Include key GTM elements like GTM Motion, Touch Model, ICP, Pricing, etc. based on the structured context provided."""
}

# User prompt template for deep-research
USER_PROMPT_TEMPLATE = """Here is structured company context for {company_name}:

Company Overview:
{company_overview}

Structured GTM Context:
{structured_gtm_context}

Enriched Data:
{enriched_data}

Account Strategist GTM Description:
{gtm_description}

Return STRICT JSON with keys: {section_keys}

Each section should follow the detailed descriptions provided and be 200-400 words. 
Use inline markdown links for every claim. Focus on describing the company's current GTM strategy 
based on the data provided, not proposing new strategies. Leverage the structured GTM context 
to provide deeper insights into how the company's GTM elements work together."""

# Polish prompt for second pass
POLISH_PROMPT = """Polish the following GTM strategy document sections. Maintain all citations and markdown links. 
Unify the tone to be professional and analytical. Ensure consistency across sections while preserving 
the detailed analysis and specific insights. Each section should remain 200-400 words. 
Ensure the analysis flows logically from one section to the next, showing how GTM elements interconnect."""

# Additional prompt for ICP analysis
ICP_ANALYSIS_PROMPT = """Analyze the following ICP data and provide insights on:
1. How the touch levels and activity types align with the ICP characteristics
2. What the metrics (ACV, deals won per year) indicate about the ICP's value and complexity
3. How the ICP segments relate to the business model and product offerings
4. Recommendations for optimizing the GTM approach for each ICP

ICP Data: {icp_data}"""

# Additional prompt for business model analysis
BUSINESS_MODEL_ANALYSIS_PROMPT = """Analyze the following business model data and provide insights on:
1. How the business model type influences pricing and packaging decisions
2. What the financing structure indicates about growth strategy
3. How market maturity affects GTM choices
4. Connection between business model and ICP targeting

Business Model Data: {business_model_data}"""

# Section keys for the output
SECTION_KEYS = [
    "DOC_TITLE", "INTRO", "PRICING_PACKAGING", "GTM_MOTION", 
    "TOUCH_MODEL", "ICP", "METRICS", "FINANCIALS", 
    "FINANCING", "MARKET_MATURITY", "STAKEHOLDERS", "SUMMARY_TABLE"
] 