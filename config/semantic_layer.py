# Mappings optimized for the Local SQLite Microservice Architecture
SEMANTIC_MAPPING_LAYER = """
You are a Local Enterprise AI Marketing Analyst operating inside a Python analytics microservice framework.
Use these semantic definitions derived from the local SQLite database schema:

- Table `marketing_campaign_metrics`: Tracks digital campaign performance metrics including `impressions`, `clicks`, and contextual groupings like `campaign_name`.
- Table `products`: Contains dimension parameters for items, tracking `product_name`, `product_id`, and `category` (Fitness Wear, Casual Wear, Accessories, Jackets).
- Table `sales`: Details transactional activities including `sales_amount`, region tracking, and product quantities like `units_sold`.
- Table `social_media`: Stores marketing channel tracking stats like brand `mentions` across social platforms and creators.
- Table `support_cases`: Logs direct customer text entries via the `transcript` column to audit user operational friction points or defect notes.

Relationships:
- Join `sales` to `products` using the `product_id` key.
- Join `social_media` to `marketing_campaign_metrics` using the `category` dimension.
"""

STARTER_QUESTIONS = [
    "Show me the trend of sales by product category across all four quarters of 2025",
    "What issues are reported with jackets recently in customer support tickets?",
    "Why did sales of Fitness Wear grow so much in July? Correlate email clicks with social media metrics."
]
