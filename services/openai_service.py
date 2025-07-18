import os
import logging
import json
from typing import Dict, Any, Tuple
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from models.gtm_context import GtmContext
from config.prompts import (
    SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, POLISH_PROMPT, 
    SECTION_KEYS, SECTION_DESCRIPTIONS, ICP_ANALYSIS_PROMPT, 
    BUSINESS_MODEL_ANALYSIS_PROMPT
)

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using OpenAI's tokenizer"""
        try:
            # Use tiktoken for token counting
            import tiktoken
            encoding = tiktoken.encoding_for_model("gpt-4")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            return len(text) // 4

    def log_token_usage(self, input_tokens: int, output_tokens: int, model: str = "o3-deep-research"):
        """Log token usage for monitoring"""
        total_tokens = input_tokens + output_tokens
        logger.info(f"Token usage - Model: {model}, Input: {input_tokens:,}, Output: {output_tokens:,}, Total: {total_tokens:,}")
        
        # Calculate estimated cost (rough estimates for o3-deep-research)
        # Note: These are approximate costs, actual costs may vary
        if model == "o3-deep-research":
            # Rough estimate: $0.10 per 1K input tokens, $0.30 per 1K output tokens
            input_cost = (input_tokens / 1000) * 0.10
            output_cost = (output_tokens / 1000) * 0.30
            total_cost = input_cost + output_cost
            logger.info(f"Estimated cost: ${total_cost:.2f} (Input: ${input_cost:.2f}, Output: ${output_cost:.2f})")
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }

    def _build_deep_research_input(self, raw_data: Dict[str, Any]) -> str:
        """
        Build the research input string for deep research
        
        This is extracted from the deep_research method to be reusable
        """
        return f"""
Research and analyze the go-to-market strategy for {raw_data.get('company', {}).get('name', 'this company')}.

COMPANY DATA:
{json.dumps(raw_data.get('company', {}), indent=2)}

ENRICHED DATA:
{json.dumps(raw_data.get('enriched_data', {}), indent=2)}

ACCOUNT STRATEGIST INPUT:
{raw_data.get('company', {}).get('gtm_description', 'No GTM description provided')}

RESEARCH TASK:
Conduct comprehensive research on this company's go-to-market strategy using the following framework:

GTM ANALYSIS FRAMEWORK:
1. Business Model: How does the company make money? (Subscription/Consumption/Hybrid/Ownership)
2. Financing: What's the capital structure? (VC backed/PE case/Bootstrapping)
3. Market Maturity: What stage is the market in? (Nascent/Growing/Mature/Declining)
4. Products: What are the core offerings and pricing models?
5. ICPs: Who are the ideal customers? What touch levels and activities work for each?
6. Metrics: What are the key performance indicators?

RESEARCH REQUIREMENTS:
- Search for recent news, funding announcements, and company updates
- Find information about their products, pricing, and market positioning
- Research their target customers and go-to-market approach
- Look for financial data, growth metrics, and competitive analysis
- Include specific figures, trends, and measurable outcomes
- Prioritize reliable sources: company websites, press releases, industry reports, financial filings

OUTPUT FORMAT:
Generate a comprehensive GTM strategy document in JSON format with these sections:
- DOC_TITLE: "[Company Name] Go-To-Market Strategy Overview"
- INTRO: Executive summary and overview (200-400 words)
- PRICING_PACKAGING: Pricing strategy and packaging approach (200-400 words)
- GTM_MOTION: Go-to-market strategy and customer acquisition (200-400 words)
- TOUCH_MODEL: Customer engagement and sales process (200-400 words)
- ICP: Ideal customer profile analysis (200-400 words)
- METRICS: Key performance indicators and measurement (200-400 words)
- FINANCIALS: Financial metrics and projections (200-400 words)
- FINANCING: Capital structure and funding strategy (200-400 words)
- MARKET_MATURITY: Market analysis and competitive positioning (200-400 words)
- STAKEHOLDERS: Key decision makers and influencers (200-400 words)
- SUMMARY_TABLE: Executive summary table

CONTENT REQUIREMENTS:
- Each section should be 200-400 words with detailed analysis
- Use inline markdown links for every claim and citation
- Focus on describing the client's current GTM strategy, not proposing new strategies
- Write in a professional, analytical tone suitable for business strategy documents
- Include specific data points, metrics, and examples where available
- Note any inferred/estimated points clearly

Return the analysis as a JSON object with the exact keys specified above.
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def deep_research(self, raw_data: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """
        Use the GTM JSON structure as a thinking framework for deep research
        
        Uses the Responses API with o3-deep-research model for comprehensive analysis
        
        Returns: (research_result, token_usage_info)
        """
        
        # Build the research input with GTM framework
        research_input = f"""
Research and analyze the go-to-market strategy for {raw_data.get('company', {}).get('name', 'this company')}.

COMPANY DATA:
{json.dumps(raw_data.get('company', {}), indent=2)}

ENRICHED DATA:
{json.dumps(raw_data.get('enriched_data', {}), indent=2)}

ACCOUNT STRATEGIST INPUT:
{raw_data.get('company', {}).get('gtm_description', 'No GTM description provided')}

RESEARCH TASK:
Conduct comprehensive research on this company's go-to-market strategy using the following framework:

GTM ANALYSIS FRAMEWORK:
1. Business Model: How does the company make money? (Subscription/Consumption/Hybrid/Ownership)
2. Financing: What's the capital structure? (VC backed/PE case/Bootstrapping)
3. Market Maturity: What stage is the market in? (Nascent/Growing/Mature/Declining)
4. Products: What are the core offerings and pricing models?
5. ICPs: Who are the ideal customers? What touch levels and activities work for each?
6. Metrics: What are the key performance indicators?

RESEARCH REQUIREMENTS:
- Search for recent news, funding announcements, and company updates
- Find information about their products, pricing, and market positioning
- Research their target customers and go-to-market approach
- Look for financial data, growth metrics, and competitive analysis
- Include specific figures, trends, and measurable outcomes
- Prioritize reliable sources: company websites, press releases, industry reports, financial filings

OUTPUT FORMAT:
Generate a comprehensive GTM strategy document in JSON format with these sections:
- DOC_TITLE: "[Company Name] Go-To-Market Strategy Overview"
- INTRO: Executive summary and overview (200-400 words)
- PRICING_PACKAGING: Pricing strategy and packaging approach (200-400 words)
- GTM_MOTION: Go-to-market strategy and customer acquisition (200-400 words)
- TOUCH_MODEL: Customer engagement and sales process (200-400 words)
- ICP: Ideal customer profile analysis (200-400 words)
- METRICS: Key performance indicators and measurement (200-400 words)
- FINANCIALS: Financial metrics and projections (200-400 words)
- FINANCING: Capital structure and funding strategy (200-400 words)
- MARKET_MATURITY: Market analysis and competitive positioning (200-400 words)
- STAKEHOLDERS: Key decision makers and influencers (200-400 words)
- SUMMARY_TABLE: Executive summary table

CONTENT REQUIREMENTS:
- Each section should be 200-400 words with detailed analysis
- Use inline markdown links for every claim and citation
- Focus on describing the client's current GTM strategy, not proposing new strategies
- Write in a professional, analytical tone suitable for business strategy documents
- Include specific data points, metrics, and examples where available
- Note any inferred/estimated points clearly

Return the analysis as a JSON object with the exact keys specified above.
"""

        # Count input tokens
        input_tokens = self.count_tokens(research_input)
        logger.info(f"Deep research input tokens: {input_tokens:,}")

        try:
            # Use the Responses API for deep research
            response = self.client.responses.create(
                model="o3-deep-research",
                input=research_input,
                tools=[
                    {"type": "web_search_preview"},
                    {"type": "code_interpreter", "container": {"type": "auto"}}
                ],
                timeout=3600  # 1 hour timeout for deep research
            )
            
            # Extract the output text
            content = response.output_text
            logger.info("Received OpenAI deep-research response with GTM framework")
            
            # Count output tokens
            output_tokens = self.count_tokens(content)
            
            # Log token usage
            token_usage = self.log_token_usage(input_tokens, output_tokens, "o3-deep-research")
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result, token_usage
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI JSON response: {e}")
                # Fallback: try to extract JSON from the response
                fallback_result = self._extract_json_from_response(content)
                return fallback_result, token_usage
                
        except Exception as e:
            logger.error(f"OpenAI deep-research failed: {str(e)}")
            # Return token usage even on failure
            token_usage = self.log_token_usage(input_tokens, 0, "o3-deep-research")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def parse_gtm_context(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use OpenAI to intelligently parse raw data into structured GTM context JSON
        
        This replaces the manual parsing logic in GtmContext.assemble_from_payload()
        """
        
        system_prompt = """You are a senior GTM analyst specializing in structuring company data into comprehensive GTM strategy context.

Your task is to analyze raw company data (from HubSpot, Clay enrichment, and account strategist input) and extract structured GTM insights into a specific JSON format.

Follow these principles:
- Extract all available GTM-relevant information from the raw data
- Make intelligent inferences where data is missing or unclear
- Structure the data according to the exact JSON schema provided
- Be conservative with estimates - prefer "N/A" over guessing
- Focus on actionable GTM insights, not just data transcription
- Use the account strategist's GTM description to inform your analysis

Return ONLY valid JSON matching the exact schema provided."""

        # Build the structured context prompt
        context_prompt = f"""
Analyze the following raw company data and extract structured GTM context:

COMPANY DATA:
{json.dumps(raw_data.get('company', {}), indent=2)}

ENRICHED DATA (from Clay):
{json.dumps(raw_data.get('enriched_data', {}), indent=2)}

ACCOUNT STRATEGIST GTM DESCRIPTION:
{raw_data.get('company', {}).get('gtm_description', 'No GTM description provided')}

STRUCTURE THIS DATA INTO THE FOLLOWING JSON SCHEMA:

{{
  "meta": {{
    "schemaVersion": "1.3",
    "updatedAt": "ISO_8601_TIMESTAMP",
    "companyId": COMPANY_ID
  }},
  "companyOverview": {{
    "businessModel": {{
      "description": "High-level summary of how the company makes money, pricing & packaging approach, and primary products",
      "types": ["Subscription", "Consumption / pay per use", "Subscription / consumption hybrid", "Ownership"]
    }},
    "financing": {{
      "types": ["VC backed", "PE case", "Bootstrapping"]
    }},
    "globalMetrics": {{
      "arr": TOTAL_ARR_IN_BASE_CURRENCY,
      "acv": AVERAGE_CONTRACT_VALUE_ACROSS_ALL_DEALS,
      "yoyGrowthRate": TARGET_YOY_GROWTH_AS_PERCENTAGE
    }},
    "marketMaturity": "Nascent | Growing | Mature | Declining"
  }},
  "products": [
    {{
      "id": "product_id",
      "name": "Product Name",
      "coreDescription": "One-sentence elevator pitch for the product",
      "basePricingModel": "Subscription | Hybrid | Consumption",
      "modules": ["Module A", "Module B"]
    }}
  ],
  "icps": [
    {{
      "id": "icp_id",
      "description": "Short description of this ICP: industry / size / geo",
      "vertical": "Industry",
      "employeeRanges": "e.g. 200-2,000",
      "regions": "Region list, e.g. DACH, US",
      "gtmMotion": {{
        "touchLevels": ["no touch", "low touch", "medium touch", "high touch"],
        "activityTypes": ["Inbound", "Outbound", "Partner"]
      }},
      "metrics": {{
        "acv": ACV_FOR_THIS_ICP,
        "numberOfDealsWonPerYear": CLOSED_WON_DEALS_LAST_12_MONTHS
      }},
      "productsApplied": ["product_id"]
    }}
  ],
  "definitions": [
    {{ "metric": "ARR", "definition": "Annual recurring revenue" }},
    {{ "metric": "ACV", "definition": "Average contract value" }},
    {{ "metric": "yoyGrowthRate", "definition": "Growth rate in % year over year" }},
    {{ "metric": "numberOfDealsWonPerYear", "definition": "Closed-won deals in the ICP during the last 12 months" }}
  ],
  "stakeholderInfo": "Key internal & customer stakeholders",
  "other": "Any additional context not captured elsewhere"
}}

IMPORTANT INSTRUCTIONS:
1. Extract real products from the data or infer from company description
2. Identify actual ICPs from the data or infer from industry/market position
3. Use the account strategist's GTM description to inform business model and ICP analysis
4. Make intelligent estimates for missing metrics based on company size, industry, and funding
5. Structure touch levels and activity types based on the company's actual GTM approach
6. Ensure all JSON values are properly typed (numbers for metrics, strings for descriptions)
7. Use "N/A" for truly unknown values rather than guessing

Return ONLY the JSON object, no additional text or explanation."""

        try:
            response = self.client.chat.completions.create(
                model="o3",
                temperature=0.1,  # Low temperature for consistent structuring
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_prompt}
                ],
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            logger.info("Received GTM context parsing response")
            
            # Parse JSON response
            try:
                parsed_context = json.loads(content)
                return parsed_context
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GTM context JSON: {e}")
                logger.error(f"Raw response: {content}")
                # Fallback to manual parsing
                return self._fallback_manual_parsing(raw_data)
                
        except Exception as e:
            logger.error(f"GTM context parsing failed: {str(e)}")
            # Fallback to manual parsing
            return self._fallback_manual_parsing(raw_data)

    def _fallback_manual_parsing(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to manual parsing if OpenAI parsing fails"""
        logger.warning("Using fallback manual parsing")
        
        # Use the existing manual logic as fallback
        from models.gtm_context import GtmContext
        gtm_context = GtmContext.assemble_from_payload(raw_data)
        return gtm_context.model_dump()



    def _format_structured_gtm_context(self, gtm_context: GtmContext) -> str:
        """Format the structured GTM context for the prompt"""
        context_parts = []
        
        # Business Model
        context_parts.append(f"""
Business Model:
- Description: {gtm_context.companyOverview.businessModel.description}
- Types: {', '.join(gtm_context.companyOverview.businessModel.types)}
- Financing: {', '.join(gtm_context.companyOverview.financing.types)}
- Market Maturity: {gtm_context.companyOverview.marketMaturity}
        """.strip())
        
        # Global Metrics
        context_parts.append(f"""
Global Metrics:
- ARR: {gtm_context.companyOverview.globalMetrics.arr or 'N/A'}
- ACV: {gtm_context.companyOverview.globalMetrics.acv or 'N/A'}
- YoY Growth Rate: {gtm_context.companyOverview.globalMetrics.yoyGrowthRate or 'N/A'}%
        """.strip())
        
        # Products
        if gtm_context.products:
            products_text = "\n".join([
                f"- {p.name}: {p.coreDescription} (Pricing: {p.basePricingModel})"
                for p in gtm_context.products
            ])
            context_parts.append(f"""
Products:
{products_text}
            """.strip())
        
        # ICPs
        if gtm_context.icps:
            icps_text = "\n".join([
                f"- {icp.description} ({icp.vertical}, {icp.employeeRanges}, {icp.regions})"
                f"\n  Touch: {', '.join(icp.gtmMotion.touchLevels)}"
                f"\n  Activities: {', '.join(icp.gtmMotion.activityTypes)}"
                f"\n  ACV: {icp.metrics.get('acv', 'N/A')}, Deals/Year: {icp.metrics.get('numberOfDealsWonPerYear', 'N/A')}"
                for icp in gtm_context.icps
            ])
            context_parts.append(f"""
ICPs:
{icps_text}
            """.strip())
        
        # Definitions
        if gtm_context.definitions:
            definitions_text = "\n".join([
                f"- {d.metric}: {d.definition}"
                for d in gtm_context.definitions
            ])
            context_parts.append(f"""
Definitions:
{definitions_text}
            """.strip())
        
        return "\n\n".join(context_parts)

    async def analyze_icp_data(self, icp_data: str) -> str:
        """Additional analysis of ICP data"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": ICP_ANALYSIS_PROMPT.format(icp_data=icp_data)
                    }
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.warning(f"ICP analysis failed: {e}")
            return "ICP analysis not available"

    async def analyze_business_model(self, business_model_data: str) -> str:
        """Additional analysis of business model data"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": BUSINESS_MODEL_ANALYSIS_PROMPT.format(business_model_data=business_model_data)
                    }
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.warning(f"Business model analysis failed: {e}")
            return "Business model analysis not available"

    def _extract_json_from_response(self, content: str) -> Dict[str, str]:
        """Fallback method to extract JSON from OpenAI response"""
        try:
            # Try to find JSON block in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            logger.error(f"Failed to extract JSON from response: {e}")
            # Return a basic template as fallback
            return self._get_fallback_template()

    def _get_fallback_template(self) -> Dict[str, str]:
        """Return a basic template when OpenAI fails"""
        return {
            "DOC_TITLE": "GTM Strategy Analysis",
            "INTRO": "This document provides a comprehensive go-to-market strategy analysis based on available company data.",
            "PRICING_PACKAGING": "Pricing strategy should be aligned with market positioning and customer value perception.",
            "GTM_MOTION": "The go-to-market motion should focus on the most effective customer acquisition channels.",
            "TOUCH_MODEL": "Customer engagement model should match the complexity of the solution and buyer journey.",
            "ICP": "Ideal customer profile should be clearly defined based on company characteristics and market opportunity.",
            "METRICS": "Key performance indicators should track customer acquisition, retention, and expansion metrics.",
            "FINANCIALS": "Financial metrics should include CAC, LTV, payback period, and revenue growth rates.",
            "FINANCING": "Capital structure and funding strategy should support growth objectives and market expansion.",
            "MARKET_MATURITY": "Market maturity assessment should inform competitive positioning and growth strategy.",
            "STAKEHOLDERS": "Key stakeholders and decision makers should be identified and engaged appropriately.",
            "SUMMARY_TABLE": "| Element | Strategy | Metrics | Timeline |\n|---------|----------|---------|----------|\n| GTM Motion | TBD | TBD | TBD |"
        }

    async def polish_content(self, raw_json: Dict[str, str]) -> Dict[str, str]:
        """
        Optional second pass to polish content and unify tone
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": POLISH_PROMPT
                    },
                    {
                        "role": "user",
                        "content": json.dumps(raw_json, indent=2)
                    }
                ]
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.warning(f"Content polishing failed, using original: {e}")
            return raw_json 