import sqlite3
import os

def provision_enterprise_workspace():
    # Enforce structured enterprise layout directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("engine", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # MATCH THE PATH EXPECTED BY YOUR FRONTEND WEB HUB
    db_path = os.path.join("data", "mock_data.db")
    
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📂 Provisioning email analytics database schemas...")

    # Table 1: CAMPAIGNS (Core operational metadata)
    cursor.execute("""
    CREATE TABLE email_campaigns (
        campaign_id TEXT PRIMARY KEY,
        campaign_name TEXT,
        audience_segment TEXT,
        subject_line TEXT,
        launch_date TEXT
    )""")
    
    # Table 2: METRICS (Performance facts)
    cursor.execute("""
    CREATE TABLE campaign_metrics (
        campaign_id TEXT,
        sent_count INTEGER,
        delivered_count INTEGER,
        open_count INTEGER,
        click_count INTEGER,
        unsubscribe_count INTEGER,
        FOREIGN KEY(campaign_id) REFERENCES email_campaigns(campaign_id)
    )""")
    
    # Table 3: REVENUE_ATTRIBUTION (Financial outcomes linked to emails)
    cursor.execute("""
    CREATE TABLE revenue_attribution (
        attribution_id TEXT PRIMARY KEY,
        campaign_id TEXT,
        product_category TEXT,
        units_sold INTEGER,
        attributed_sales REAL,
        conversion_date TEXT,
        FOREIGN KEY(campaign_id) REFERENCES email_campaigns(campaign_id)
    )""")
    
    # Table 4: RECIPIENT_FEEDBACK (Unstructured responses/complaints)
    cursor.execute("""
    CREATE TABLE recipient_feedback (
        feedback_id TEXT PRIMARY KEY,
        campaign_id TEXT,
        feedback_type TEXT,
        transcript TEXT,
        date TEXT,
        FOREIGN KEY(campaign_id) REFERENCES email_campaigns(campaign_id)
    )""")
    
    print("🌱 Seeding email performance data layers...")

    # Campaigns Dimensions
    cursor.executemany("INSERT INTO email_campaigns VALUES (?,?,?,?,?)", [
        ("CMP-001", "Summer Fitness Blast", "Fitness Enthusiasts", "🔥 Crush Your Summer Goals - 20% Off Inside!", "2025-06-15"),
        ("CMP-002", "Midsummer Flash Sale", "Lapsed Shoppers", "⚡ Flash Sale: 24 Hours Only!", "2025-07-20"),
        ("CMP-003", "Back To School Style", "Parents & Students", "🎒 Ready, Set, Style! Fall Arrivals Are Here", "2025-08-05")
    ])
    
    # Campaign Performance Facts
    cursor.executemany("INSERT INTO campaign_metrics VALUES (?,?,?,?,?,?)", [
        ("CMP-001", 50000, 49800, 18500, 3200, 120),
        ("CMP-002", 75000, 74200, 22100, 4800, 450),
        ("CMP-003", 60000, 59900, 25000, 6100, 95)
    ])
    
    # Revenue Attribution Facts
    cursor.executemany("INSERT INTO revenue_attribution VALUES (?,?,?,?,?,?)", [
        ("ATT-101", "CMP-001", "Fitness Wear", 150, 7500.00, "2025-06-16"),
        ("ATT-102", "CMP-001", "Accessories", 80, 2400.00, "2025-06-17"),
        ("ATT-103", "CMP-002", "Fitness Wear", 420, 21000.00, "2025-07-21"), 
        ("ATT-104", "CMP-003", "Casual Wear", 310, 15500.00, "2025-08-06"),
        ("ATT-105", "CMP-003", "Jackets", 90, 10800.00, "2025-08-07")
    ])
    
    # Unstructured Feedback Logs
    cursor.executemany("INSERT INTO recipient_feedback VALUES (?,?,?,?,?)", [
        ("FB-201", "CMP-002", "Complaint", "The discount code 'FLASH24' provided in the email threw an error at checkout.", "2025-07-20"),
        ("FB-202", "CMP-002", "Unsubscribe request", "Stop emailing me twice a day, it is too much spam.", "2025-07-21"),
        ("FB-203", "CMP-003", "Product Inquiry", "Are the jackets featured in the Fall collection waterproof?", "2025-08-06")
    ])
    
    conn.commit()
    conn.close()
    print("🛠️ Enterprise workspace initialized successfully. Core tables nested in data/mock_data.db.")

if __name__ == "__main__":
    provision_enterprise_workspace()
