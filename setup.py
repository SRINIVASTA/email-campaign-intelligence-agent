import sqlite3
import os

def provision_enterprise_workspace():
    # Enforce structured corporate workspace folders
    os.makedirs("data", exist_ok=True)
    os.makedirs("engine", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    db_path = os.path.join("data", "mock_data.db")
    
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📂 Initializing Snowflake Intelligence production schema mirror...")

    # Table 1: MARKETING_CAMPAIGN_METRICS
    cursor.execute("""
    CREATE TABLE marketing_campaign_metrics (
        date TEXT,
        category TEXT,
        campaign_name TEXT,
        impressions INTEGER,
        clicks INTEGER
    )""")
    
    # Table 2: PRODUCTS
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT,
        category TEXT
    )""")
    
    # Table 3: SALES
    cursor.execute("""
    CREATE TABLE sales (
        date TEXT,
        region TEXT,
        product_id INTEGER,
        units_sold INTEGER,
        sales_amount REAL,
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    )""")
    
    # Table 4: SOCIAL_MEDIA
    cursor.execute("""
    CREATE TABLE social_media (
        date TEXT,
        category TEXT,
        platform TEXT,
        influencer TEXT,
        mentions INTEGER
    )""")
    
    # Table 5: SUPPORT_CASES
    cursor.execute("""
    CREATE TABLE support_cases (
        id TEXT PRIMARY KEY,
        title TEXT,
        product TEXT,
        transcript TEXT,
        date TEXT
    )""")
    
    print("🌱 Seeding production partitions with Snowflake reference variables...")

    # Seed Products
    cursor.executemany("INSERT INTO products VALUES (?,?,?)", [
        (1, "Pro Trainer Shoes", "Fitness Wear"),
        (2, "Ergonomic Hydration Pack", "Accessories"),
        (3, "Performance Tech Fleece", "Casual Wear")
    ])
    
    # Seed Marketing Metrics
    cursor.executemany("INSERT INTO marketing_campaign_metrics VALUES (?,?,?,?,?)", [
        ("2025-06-15", "Fitness Wear", "Summer Fitness Blast", 10927, 4800),
        ("2025-07-20", "Fitness Wear", "Midsummer Flash Sale", 7278, 6100),
        ("2025-08-05", "Casual Wear", "Back To School Style", 9962, 3200)
    ])
    
    # Seed Sales Attributions
    cursor.executemany("INSERT INTO sales VALUES (?,?,?,?,?)", [
        ("2025-06-16", "North", 1, 150, 7500.00),
        ("2025-06-17", "East", 2, 80, 2400.00),
        ("2025-07-21", "South", 1, 420, 21000.00),
        ("2025-08-06", "North", 3, 310, 15500.00),
        ("2025-08-07", "West", 3, 90, 10800.00)
    ])
    
    # Seed Social Media Mentions
    cursor.executemany("INSERT INTO social_media VALUES (?,?,?,?,?)", [
        ("2025-06-16", "Fitness Wear", "Instagram", "NovaFitStar", 16),
        ("2025-07-21", "Fitness Wear", "TikTok", "AlphaAthlete", 24),
        ("2025-08-06", "Casual Wear", "YouTube", "StyleVlog", 9)
    ])
    
    # Seed Support Cases (Qualitative Transcript Data)
    cursor.executemany("INSERT INTO support_cases VALUES (?,?,?,?,?)", [
        ("CS-901", "Promo Code Fail", "Fitness Wear", "The discount code 'FLASH24' provided threw a runtime error at checkout.", "2025-07-20"),
        ("CS-902", "Unsubscribe Spam", "Accessories", "Stop messaging me twice a day, it is too much spam.", "2025-07-21"),
        ("CS-903", "Waterproof Inquiry", "Casual Wear", "Are the jackets featured in the Fall collection waterproof?", "2025-08-06")
    ])
    
    conn.commit()
    conn.close()
    print("✨ Local Snowflake-style database layout initialized successfully.")

if __name__ == "__main__":
    provision_enterprise_workspace()
