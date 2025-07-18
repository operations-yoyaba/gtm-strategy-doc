from typing import List, Literal, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class GenerateRequest(BaseModel):
    companyId: int = Field(..., description="HubSpot company ID")
    stageTs: str = Field(..., description="ISO 8601 timestamp when stage changed")
    company: Dict[str, Any] = Field(..., description="Company data from HubSpot (already enriched)")
    enriched_data: Dict[str, Any] = Field(..., description="Enriched data from Clay")
    
    # Optional fields for backward compatibility
    gtm_description: Optional[str] = Field(None, description="GTM description (can also be in company.gtm_description)")
    
    def get_company_data(self) -> Dict[str, Any]:
        """Get company data with fallback for gtm_description"""
        company_data = self.company.copy()
        if self.gtm_description and not company_data.get('gtm_description'):
            company_data['gtm_description'] = self.gtm_description
        return company_data

class BusinessModel(BaseModel):
    description: str
    types: List[Literal["Subscription", "Consumption / pay per use", "Subscription / consumption hybrid", "Ownership"]]

class Financing(BaseModel):
    types: List[Literal["VC backed", "PE case", "Bootstrapping"]]

class GlobalMetrics(BaseModel):
    arr: Optional[float] = None
    acv: Optional[float] = None
    yoyGrowthRate: Optional[float] = None

class CompanyOverview(BaseModel):
    businessModel: BusinessModel
    financing: Financing
    globalMetrics: GlobalMetrics
    marketMaturity: Literal["Nascent", "Growing", "Mature", "Declining"]

class Product(BaseModel):
    id: str
    name: str
    coreDescription: str
    basePricingModel: str
    modules: List[str] = []

class GtmMotion(BaseModel):
    touchLevels: List[Literal["no touch", "low touch", "medium touch", "high touch"]]
    activityTypes: List[Literal["Inbound", "Outbound", "Partner"]]

class Icp(BaseModel):
    id: str
    description: str
    vertical: str
    employeeRanges: str
    regions: str
    gtmMotion: GtmMotion
    metrics: Dict[str, Optional[float]]
    productsApplied: List[str] = []

class Definition(BaseModel):
    metric: str
    definition: str

class GtmContext(BaseModel):
    meta: Dict[str, Any] = Field(default_factory=dict)
    companyOverview: CompanyOverview
    products: List[Product] = Field(default_factory=list)
    icps: List[Icp] = Field(default_factory=list)
    definitions: List[Definition] = Field(default_factory=list)
    stakeholderInfo: Optional[str] = None
    other: Optional[str] = None

    @classmethod
    def assemble_from_payload(cls, payload: Dict[str, Any]) -> "GtmContext":
        """
        Assemble GtmContext from webhook payload that already contains enriched data
        Data flow: HubSpot -> Clay -> HubSpot -> Cloud Function
        Focus: Company GTM strategy, not deal-specific
        """
        # Extract company data from payload
        company_data = payload.get("company", {})
        enriched_data = payload.get("enriched_data", {})
        
        # Extract basic company information using config
        from config.hubspot_properties import COMPANY_PROPERTIES
        
        company_overview = {}
        for prop in COMPANY_PROPERTIES:
            if prop in company_data:
                company_overview[prop] = company_data[prop]
        
        # Merge with enriched data from Clay
        if enriched_data:
            company_overview.update({
                "funding_rounds": enriched_data.get("funding_rounds"),
                "total_funding": enriched_data.get("total_funding"),
                "investors": enriched_data.get("investors"),
                "competitors": enriched_data.get("competitors"),
                "technologies": enriched_data.get("technologies"),
                "social_presence": enriched_data.get("social_presence"),
                "market_position": enriched_data.get("market_position"),
                "growth_metrics": enriched_data.get("growth_metrics"),
            })

        # Determine business model type based on enriched data
        business_model_description = cls._determine_business_model(company_overview, enriched_data)
        business_model_types = cls._determine_business_model_types(company_overview, enriched_data)
        
        # Determine financing type
        financing_types = cls._determine_financing_types(enriched_data)
        
        # Determine market maturity
        market_maturity = cls._determine_market_maturity(enriched_data)
        
        # Create global metrics
        global_metrics = GlobalMetrics(
            arr=company_overview.get("annualrevenue"),
            acv=enriched_data.get("growth_metrics", {}).get("avg_deal_size"),
            yoyGrowthRate=enriched_data.get("growth_metrics", {}).get("annual_growth_rate")
        )

        # Create company overview
        company_overview_obj = CompanyOverview(
            businessModel=BusinessModel(
                description=business_model_description,
                types=business_model_types
            ),
            financing=Financing(types=financing_types),
            globalMetrics=global_metrics,
            marketMaturity=market_maturity
        )

        # Create products list (this would typically come from your product catalog)
        # For now, using placeholder - in practice this would be customized per client
        products = [
            Product(
                id="prod_1",
                name="Core Platform",
                coreDescription="Main SaaS platform for business operations",
                basePricingModel="Subscription",
                modules=["analytics", "reporting", "integrations"]
            )
        ]

        # Create ICPs (this would be customized based on the client's business)
        icps = [
            Icp(
                id="icp_1",
                description="Mid-market B2B SaaS companies",
                vertical="Technology",
                employeeRanges="50-500",
                regions="North America, Europe",
                gtmMotion=GtmMotion(
                    touchLevels=["medium touch", "high touch"],
                    activityTypes=["Inbound", "Outbound"]
                ),
                metrics={
                    "acv": 50000.0,
                    "numberOfDealsWonPerYear": 24.0
                },
                productsApplied=["prod_1"]
            )
        ]

        # Create definitions
        definitions = [
            Definition(metric="ARR", definition="Annual recurring revenue"),
            Definition(metric="ACV", definition="Average contract value"),
            Definition(metric="yoyGrowthRate", definition="Growth rate in % year over year"),
            Definition(metric="numberOfDealsWonPerYear", definition="Closed-won deals in the ICP during the last 12 months")
        ]

        return cls(
            meta={
                "schemaVersion": "1.3",
                "updatedAt": datetime.utcnow().isoformat(),
                "companyId": company_data.get("id")
            },
            companyOverview=company_overview_obj,
            products=products,
            icps=icps,
            definitions=definitions,
            stakeholderInfo="Key decision makers include CTO, VP Engineering, and Head of Product",
            other="Additional context about the company's growth stage and market position"
        )

    @staticmethod
    def _determine_business_model(company_overview: Dict[str, Any], enriched_data: Dict[str, Any]) -> str:
        """Determine business model description based on available data"""
        industry = company_overview.get("industry", "")
        market_position = enriched_data.get("market_position", "")
        
        if "SaaS" in industry or "Software" in industry:
            return f"B2B SaaS company in {industry} sector with {market_position}"
        else:
            return f"B2B company in {industry} sector with {market_position}"

    @staticmethod
    def _determine_business_model_types(company_overview: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[str]:
        """Determine business model types based on available data"""
        types = []
        
        # This would be more sophisticated in practice
        # For now, default to subscription model for SaaS companies
        if "Software" in company_overview.get("industry", ""):
            types.append("Subscription")
        
        return types if types else ["Subscription"]

    @staticmethod
    def _determine_financing_types(enriched_data: Dict[str, Any]) -> List[str]:
        """Determine financing types based on enriched data"""
        types = []
        
        if enriched_data.get("funding_rounds"):
            types.append("VC backed")
        
        # Add more logic based on funding data
        return types if types else ["VC backed"]

    @staticmethod
    def _determine_market_maturity(enriched_data: Dict[str, Any]) -> str:
        """Determine market maturity based on enriched data"""
        # This would be more sophisticated in practice
        # For now, default to Growing
        return "Growing"

    def get_formatted_context_for_prompt(self) -> Dict[str, str]:
        """
        Format the context for use in OpenAI prompts
        """
        company_name = self.companyOverview.businessModel.description.split()[0] if self.companyOverview.businessModel.description else "Unknown Company"
        
        # Format company overview
        company_overview = f"""
Business Model: {self.companyOverview.businessModel.description}
Business Model Types: {', '.join(self.companyOverview.businessModel.types)}
Financing: {', '.join(self.companyOverview.financing.types)}
Market Maturity: {self.companyOverview.marketMaturity}
ARR: {self.companyOverview.globalMetrics.arr or 'N/A'}
ACV: {self.companyOverview.globalMetrics.acv or 'N/A'}
YoY Growth Rate: {self.companyOverview.globalMetrics.yoyGrowthRate or 'N/A'}%
        """.strip()
        
        # Format enriched data
        enriched_data = ""
        if hasattr(self, 'companyOverview') and hasattr(self.companyOverview, 'businessModel'):
            # This would be populated from the enriched data
            enriched_data = "Enriched data available for analysis"
        
        # Get GTM description from account strategist
        gtm_description = "No GTM description provided by account strategist."
        
        return {
            "company_name": company_name,
            "company_overview": company_overview,
            "enriched_data": enriched_data,
            "gtm_description": gtm_description
        } 