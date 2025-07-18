"""
HubSpot Properties Configuration

This file contains the HubSpot properties that will be extracted from the webhook payload.
Properties can be easily added, removed, or modified here without changing the main application code.
Focus: Company GTM strategy analysis, not deal-specific information.
"""

# Company properties to extract from the webhook payload
COMPANY_PROPERTIES = [
    "name",
    "domain", 
    "industry",
    "numberofemployees",
    "annualrevenue",
    "city",
    "state", 
    "country",
    "gtm_description"  # Custom field from account strategists
]

# Properties that will be updated in HubSpot after document generation
# Note: Removed as we no longer update HubSpot
OUTPUT_PROPERTIES = {} 