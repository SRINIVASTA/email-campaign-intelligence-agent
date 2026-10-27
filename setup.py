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
    
    print("📂 Initializing expanded 4-Quarter annual production schema mirror...")

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
    
    print("🌱 Seeding 4 distinct quarters of enterprise lifecycle records...")

    # 🛍️ 1. PRODUCTS DEMOGRAPHIC REFERENCE
    cursor.executemany("INSERT INTO products VALUES (?,?,?)", [
        (1, "Pro Trainer Shoes", "Fitness Wear"),
        (2, "Ergonomic Hydration Pack", "Accessories"),
        (3, "Performance Tech Fleece", "Casual Wear"),
        (4, "Thermal Expedition Parka", "Jackets")
    ])
    
    # 📈 2. MARKETING METRICS (Distributed across Q1, Q2, Q3, Q4)
    cursor.executemany("INSERT INTO marketing_campaign_metrics VALUES (?,?,?,?,?)", [
        # Q1: Spring Launch
        ("2025-02-10", "Fitness Wear", "Spring Renewal Kickoff", 8500, 1200),
        # Q2: Summer Peak
        ("2025-06-15", "Fitness Wear", "Summer Fitness Blast", 10927, 4800),
        ("2025-07-20", "Fitness Wear", "Midsummer Flash Sale", 7278, 6100),
        # Q3: Back to School Transition
        ("2025-08-05", "Casual Wear", "Back To School Style", 9962, 3200),
        # Q4: Winter Clearance Focus
        ("2025-11-12", "Jackets", "Winter Alpine Extreme", 15400, 7800)
    ])
    
    # 💰 3. TRANSACTIONAL SALES LEDGER (Full Year Scale)
    cursor.executemany("INSERT INTO sales VALUES (?,?,?,?,?)", [
        # Q1 Transactions
        ("2025-02-11", "North", 1, 45, 2250.00),
        ("2025-02-14", "East", 2, 20, 600.00),
        # Q2 Transactions
        ("2025-06-16", "North", 1, 150, 7500.00),
        ("2025-06-17", "East", 2, 80, 2400.00),
        # Q3 Transactions
        ("2025-07-21", "South", 1, 420, 21000.00),
        ("2025-08-06", "North", 3, 310, 15500.00),
        ("2025-08-07", "West", 3, 90, 10800.00),
        # Q4 Transactions
        ("2025-11-15", "East", 4, 180, 32400.00),
        ("2025-11-18", "North", 4, 110, 19800.00)
    ])
    
    # 📱 4. SOCIAL MEDIA INFLUENCER ENGAGEMENT
    cursor.executemany("INSERT INTO social_media VALUES (?,?,?,?,?)", [
        ("2025-02-12", "Fitness Wear", "Instagram", "NovaFitStar", 8),
        ("2025-06-16", "Fitness Wear", "Instagram", "NovaFitStar", 16),
        ("2025-07-21", "Fitness Wear", "TikTok", "AlphaAthlete", 24),
        ("2025-08-06", "Casual Wear", "YouTube", "StyleVlog", 9),
        ("2025-11-14", "Jackets", "TikTok", "WinterExplorer", 42)
    ])
    
    # 💬 5. SUPPORT CASES TRANSCRIPT CHUNKS
    cursor.executemany("INSERT INTO support_cases VALUES (?,?,?,?,?)", [
        ("CS-901", "Promo Code Fail", "Fitness Wear", "The discount code 'FLASH24' provided threw a runtime error at checkout.", "2025-07-20"),
        ("CS-902", "Unsubscribe Spam", "Accessories", "Stop messaging me twice a day, it is too much spam.", "2025-07-21"),
        ("CS-903", "Waterproof Inquiry", "Casual Wear", "Are the jackets featured in the Fall collection waterproof?", "2025-08-06"),
        ("CS-904", "Seam Tearing Defect", "Jackets", "The Thermal Expedition Parka is tearing along the armpit seams after two days of wearing.", "2025-11-20")
    ])
    
    conn.commit()
    conn.close()
    print("✨ Local Snowflake-style database layout initialized successfully across 4 Quarters.")

if __name__ == "__main__":
    provision_enterprise_workspace()

# Insert this directly into your provision_enterprise_workspace() loop in setup.py

    # ==========================================
    # Table 6: SUBSCRIBERS (Profile Reference)
    # ==========================================
    cursor.execute("""
    CREATE TABLE subscribers (
        subscriber_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        first_name TEXT,
        join_date TEXT,
        status TEXT DEFAULT 'ACTIVE'
    )""")
    
    # ==========================================
    # Table 7: EMAIL_EVENT_LOGS (Telemetry Transactional Log)
    # ==========================================
    cursor.execute("""
    CREATE TABLE email_event_logs (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        campaign_name TEXT NOT NULL,
        subscriber_id INTEGER,
        event_type TEXT NOT NULL,    -- 'SENT', 'OPEN', 'CLICK', 'BOUNCE', 'UNSUBSCRIBE'
        link_url TEXT,
        FOREIGN KEY(subscriber_id) REFERENCES subscribers(subscriber_id)
    )""")

    print("🌱 Seeding campaign subscriber profile telemetry records...")
    
    # Seed active profiles
    cursor.executemany("INSERT INTO subscribers (subscriber_id, email, first_name, join_date, status) VALUES (?,?,?,?,?)", [
        (1, "corp_exec1@enterprise.com", "Sarah", "2025-01-10", "ACTIVE"),
        (2, "beta_tester@domain.io", "Alex", "2025-03-12", "ACTIVE"),
        (3, "stale_user@oldmail.com", "John", "2025-05-14", "BOUNCED"),
        (4, "opt_out_client@privacy.net", "Elena", "2025-06-20", "UNSUBSCRIBED")
    ])

    # Seed event logs to instantly test bounce alerts and metrics
    cursor.executemany("INSERT INTO email_event_logs (timestamp, campaign_name, subscriber_id, event_type, link_url) VALUES (?,?,?,?,?)", [
        ("2025-11-12 09:00:00", "Winter Alpine Extreme", 1, "SENT", None),
        ("2025-11-12 09:05:00", "Winter Alpine Extreme", 1, "OPEN", None),
        ("2025-11-12 09:06:00", "Winter Alpine Extreme", 1, "CLICK", "https://store.com"),
        ("2025-11-12 09:00:00", "Winter Alpine Extreme", 2, "SENT", None),
        ("2025-11-12 09:02:00", "Winter Alpine Extreme", 2, "OPEN", None),
        ("2025-11-12 09:00:00", "Winter Alpine Extreme", 3, "SENT", None),
        ("2025-11-12 09:00:02", "Winter Alpine Extreme", 3, "BOUNCE", None), # 🚨 System Alert testing point
        ("2025-11-12 09:00:00", "Winter Alpine Extreme", 4, "SENT", None),
        ("2025-11-12 09:45:00", "Winter Alpine Extreme", 4, "UNSUBSCRIBE", None)
    ])
