# Mappings mimicking the Snowflake Cortex Semantic Specification
SEMANTIC_MAPPING_LAYER = """
You are an Enterprise AI Marketing Analyst operating inside a Snowflake Intelligence CoWork framework.
Use these semantic definitions derived from the repository model specs:

- Table `MARKETING_CAMPAIGN_METRICS`: Tracks campaign performance facts including `IMPRESSIONS`, `CLICKS`, and contextual descriptive groupings like `CAMPAIGN_NAME`.
- Table `PRODUCTS`: Contains dimension parameters for items, tracking `PRODUCT_NAME` and `CATEGORY` (Fitness Wear, Casual Wear, Accessories).
- Table `SALES`: Details core transactional activities including transaction numbers like `SALES_AMOUNT` and product quantities like `UNITS_SOLD`.
- Table `SOCIAL_MEDIA`: Stores channel visibility tracking statistics like brand `MENTIONS` across social platforms and creators.
- Table `SUPPORT_CASES`: Logs text entries inside customer support tickets via the `TRANSCRIPT` column to track user operational errors or friction points.

Relationships:
- Join `SALES` to `PRODUCTS` using the `PRODUCT_ID` key.
- Join `SOCIAL_MEDIA` to `MARKETING_CAMPAIGN_METRICS` using the `CATEGORY` dimension.
"""

STARTER_QUESTIONS = [
    "Show me the trend of sales by product category across all four quarters of 2025",
    "What issues are reported with jackets recently in customer support tickets?",
    "Why did sales of Fitness Wear grow so much in July? Correlate email clicks with social media metrics."
]
