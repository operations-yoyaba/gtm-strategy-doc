import pytest
from datetime import datetime
from models.gtm_context import GtmContext, BusinessModel, Financing, GlobalMetrics, CompanyOverview, Product, Icp, GtmMotion, Definition

class TestGtmContext:
    """Test cases for GtmContext model"""

    def test_business_model_creation(self):
        """Test BusinessModel creation"""
        business_model = BusinessModel(
            description="B2B SaaS company in Software sector",
            types=["Subscription"]
        )
        
        assert business_model.description == "B2B SaaS company in Software sector"
        assert business_model.types == ["Subscription"]

    def test_financing_creation(self):
        """Test Financing creation"""
        financing = Financing(types=["VC backed"])
        
        assert financing.types == ["VC backed"]

    def test_global_metrics_creation(self):
        """Test GlobalMetrics creation"""
        metrics = GlobalMetrics(
            arr=50000000,
            acv=75000,
            yoyGrowthRate=150
        )
        
        assert metrics.arr == 50000000
        assert metrics.acv == 75000
        assert metrics.yoyGrowthRate == 150

    def test_company_overview_creation(self):
        """Test CompanyOverview creation"""
        business_model = BusinessModel(
            description="B2B SaaS company in Software sector",
            types=["Subscription"]
        )
        financing = Financing(types=["VC backed"])
        global_metrics = GlobalMetrics(
            arr=50000000,
            acv=75000,
            yoyGrowthRate=150
        )
        
        company_overview = CompanyOverview(
            businessModel=business_model,
            financing=financing,
            globalMetrics=global_metrics,
            marketMaturity="Growing"
        )
        
        assert company_overview.businessModel.description == "B2B SaaS company in Software sector"
        assert company_overview.financing.types == ["VC backed"]
        assert company_overview.globalMetrics.arr == 50000000
        assert company_overview.marketMaturity == "Growing"

    def test_product_creation(self):
        """Test Product creation"""
        product = Product(
            id="prod_1",
            name="Core Platform",
            coreDescription="Main SaaS platform for business operations",
            basePricingModel="Subscription",
            modules=["analytics", "reporting", "integrations"]
        )
        
        assert product.id == "prod_1"
        assert product.name == "Core Platform"
        assert product.coreDescription == "Main SaaS platform for business operations"
        assert product.basePricingModel == "Subscription"
        assert product.modules == ["analytics", "reporting", "integrations"]

    def test_gtm_motion_creation(self):
        """Test GtmMotion creation"""
        gtm_motion = GtmMotion(
            touchLevels=["medium touch", "high touch"],
            activityTypes=["Inbound", "Outbound"]
        )
        
        assert gtm_motion.touchLevels == ["medium touch", "high touch"]
        assert gtm_motion.activityTypes == ["Inbound", "Outbound"]

    def test_icp_creation(self):
        """Test Icp creation"""
        gtm_motion = GtmMotion(
            touchLevels=["medium touch", "high touch"],
            activityTypes=["Inbound", "Outbound"]
        )
        
        icp = Icp(
            id="icp_1",
            description="Mid-market B2B SaaS companies",
            vertical="Technology",
            employeeRanges="50-500",
            regions="North America, Europe",
            gtmMotion=gtm_motion,
            metrics={
                "acv": 50000.0,
                "numberOfDealsWonPerYear": 24.0
            },
            productsApplied=["prod_1"]
        )
        
        assert icp.id == "icp_1"
        assert icp.description == "Mid-market B2B SaaS companies"
        assert icp.vertical == "Technology"
        assert icp.employeeRanges == "50-500"
        assert icp.regions == "North America, Europe"
        assert icp.gtmMotion.touchLevels == ["medium touch", "high touch"]
        assert icp.metrics["acv"] == 50000.0
        assert icp.productsApplied == ["prod_1"]

    def test_definition_creation(self):
        """Test Definition creation"""
        definition = Definition(
            metric="ARR",
            definition="Annual recurring revenue"
        )
        
        assert definition.metric == "ARR"
        assert definition.definition == "Annual recurring revenue"

    def test_gtm_context_assembly_from_payload(self):
        """Test GtmContext assembly from payload"""
        payload = {
            "company": {
                "id": 15231,
                "name": "TechCorp Solutions",
                "domain": "techcorp.com",
                "industry": "Software",
                "numberofemployees": 250,
                "annualrevenue": 50000000,
                "city": "San Francisco",
                "state": "CA",
                "country": "United States",
                "gtm_description": "TechCorp is a B2B SaaS company focused on enterprise workflow automation."
            },
            "enriched_data": {
                "funding_rounds": [
                    {"round": "Series B", "amount": 25000000, "date": "2023-06-15"}
                ],
                "total_funding": 35000000,
                "investors": ["Sequoia Capital", "Andreessen Horowitz"],
                "competitors": ["Competitor A", "Competitor B"],
                "technologies": ["Python", "React", "AWS"],
                "social_presence": {
                    "linkedin_followers": 15000,
                    "twitter_followers": 8500
                },
                "market_position": "Emerging leader in workflow automation",
                "growth_metrics": {
                    "customer_count": 500,
                    "annual_growth_rate": 150,
                    "churn_rate": 0.05,
                    "avg_deal_size": 75000
                }
            }
        }
        
        gtm_context = GtmContext.assemble_from_payload(payload)
        
        # Test meta
        assert gtm_context.meta["schemaVersion"] == "1.3"
        assert gtm_context.meta["companyId"] == 15231
        assert "updatedAt" in gtm_context.meta
        
        # Test company overview
        assert "Software" in gtm_context.companyOverview.businessModel.description
        assert "Subscription" in gtm_context.companyOverview.businessModel.types
        assert "VC backed" in gtm_context.companyOverview.financing.types
        assert gtm_context.companyOverview.marketMaturity == "Growing"
        assert gtm_context.companyOverview.globalMetrics.arr == 50000000
        assert gtm_context.companyOverview.globalMetrics.acv == 75000
        assert gtm_context.companyOverview.globalMetrics.yoyGrowthRate == 150
        
        # Test products
        assert len(gtm_context.products) > 0
        assert gtm_context.products[0].name == "Core Platform"
        
        # Test ICPs
        assert len(gtm_context.icps) > 0
        assert gtm_context.icps[0].description == "Mid-market B2B SaaS companies"
        
        # Test definitions
        assert len(gtm_context.definitions) > 0
        definition_metrics = [d.metric for d in gtm_context.definitions]
        assert "ARR" in definition_metrics
        assert "ACV" in definition_metrics

    def test_formatted_context_for_prompt(self):
        """Test formatted context generation for prompts"""
        # Create a minimal GtmContext
        business_model = BusinessModel(
            description="B2B SaaS company in Software sector",
            types=["Subscription"]
        )
        financing = Financing(types=["VC backed"])
        global_metrics = GlobalMetrics(
            arr=50000000,
            acv=75000,
            yoyGrowthRate=150
        )
        company_overview = CompanyOverview(
            businessModel=business_model,
            financing=financing,
            globalMetrics=global_metrics,
            marketMaturity="Growing"
        )
        
        gtm_context = GtmContext(
            meta={"schemaVersion": "1.3", "updatedAt": "2025-01-17T10:22:45Z", "companyId": 15231},
            companyOverview=company_overview,
            products=[],
            icps=[],
            definitions=[],
            stakeholderInfo="Key decision makers include CTO, VP Engineering",
            other="Additional context about the company"
        )
        
        formatted_context = gtm_context.get_formatted_context_for_prompt()
        
        assert "company_name" in formatted_context
        assert "company_overview" in formatted_context
        assert "enriched_data" in formatted_context
        assert "gtm_description" in formatted_context
        
        # Test that company overview contains expected data
        overview = formatted_context["company_overview"]
        assert "Business Model:" in overview
        assert "Subscription" in overview
        assert "VC backed" in overview
        assert "Growing" in overview
        assert "$50,000,000" in overview  # Formatted ARR
        assert "$75,000" in overview      # Formatted ACV
        assert "150%" in overview         # Formatted YoY growth

    def test_business_model_determination(self):
        """Test business model determination logic"""
        company_overview = {"industry": "Software"}
        enriched_data = {"market_position": "Emerging leader"}
        
        description = GtmContext._determine_business_model(company_overview, enriched_data)
        assert "B2B SaaS" in description
        assert "Software" in description
        assert "Emerging leader" in description
        
        # Test non-SaaS company
        company_overview = {"industry": "Manufacturing"}
        description = GtmContext._determine_business_model(company_overview, enriched_data)
        assert "B2B" in description
        assert "Manufacturing" in description

    def test_financing_determination(self):
        """Test financing type determination"""
        enriched_data = {"funding_rounds": [{"round": "Series A"}]}
        financing_types = GtmContext._determine_financing_types(enriched_data)
        assert "VC backed" in financing_types
        
        # Test no funding data
        enriched_data = {}
        financing_types = GtmContext._determine_financing_types(enriched_data)
        assert "VC backed" in financing_types  # Default fallback

    def test_market_maturity_determination(self):
        """Test market maturity determination"""
        enriched_data = {}
        maturity = GtmContext._determine_market_maturity(enriched_data)
        assert maturity == "Growing"  # Default fallback

if __name__ == "__main__":
    pytest.main([__file__]) 