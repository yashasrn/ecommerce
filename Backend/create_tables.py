import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
# Default to a local PostgreSQL database for development.
# Override with a production DATABASE_URL when you deploy later.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ecommerce")

print("Starting database setup...")
print("=" * 50)

try:
    # Connect to database
    print(" Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print(" Connected successfully!")
    print("=" * 50)
    
    # Drop existing tables (in correct order - dependencies first)
    print("\n  Dropping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS OrderItems CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS Orders CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS Users CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS ContactMessages CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS SellerStatusChanges CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS ProductActivityLog CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS Products CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS Sellers CASCADE;")
    print("Old tables dropped!")
    
    # Create Users table
    print("\n Creating Users table...")
    cursor.execute("""
        CREATE TABLE Users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
    """)
    print(" Users table created!")
    
    # Create Orders table
    print(" Creating Orders table...")
    cursor.execute("""
        CREATE TABLE Orders (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) NOT NULL,
            fullName VARCHAR(100) NOT NULL,
            totalPrice DECIMAL(10,2) NOT NULL,
            address VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            pincode VARCHAR(20)
        );
    """)
    print(" Orders table created!")
    
    # Create OrderItems table
    print(" Creating OrderItems table...")
    cursor.execute("""
        CREATE TABLE OrderItems (
            id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES Orders(id),
            title VARCHAR(255) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            quantity INT NOT NULL
        );
    """)
    print(" OrderItems table created!")
    
    # Create ContactMessages table
    print(" Creating ContactMessages table...")
    cursor.execute("""
        CREATE TABLE ContactMessages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            subject VARCHAR(200),
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            status VARCHAR(20) DEFAULT 'New'
        );
    """)
    print(" ContactMessages table created!")
    
    # Create Sellers table
    print(" Creating Sellers table...")
    cursor.execute("""
        CREATE TABLE Sellers (
            id SERIAL PRIMARY KEY,
            fullname VARCHAR(255) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            store_name VARCHAR(255),
            store_description TEXT,
            status VARCHAR(50) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    print(" Sellers table created!")
    
    # Create Products table
    print(" Creating Products table...")
    cursor.execute("""
        CREATE TABLE Products (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            category VARCHAR(100),
            image TEXT,
            seller_email VARCHAR(100) NOT NULL REFERENCES Sellers(email),
            seller_name VARCHAR(255),
            status VARCHAR(20) DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    print(" Products table created!")
    
    # Create ProductActivityLog table
    print(" Creating ProductActivityLog table...")
    cursor.execute("""
        CREATE TABLE ProductActivityLog (
            id SERIAL PRIMARY KEY,
            product_id INT,
            seller_email VARCHAR(100) NOT NULL REFERENCES Sellers(email),
            seller_name VARCHAR(255),
            action VARCHAR(50) NOT NULL,
            product_title VARCHAR(255),
            old_data TEXT,
            new_data TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    print(" ProductActivityLog table created!")
    
    # Create SellerStatusChanges table
    print(" Creating SellerStatusChanges table...")
    cursor.execute("""
        CREATE TABLE SellerStatusChanges (
            id SERIAL PRIMARY KEY,
            seller_id INT NOT NULL REFERENCES Sellers(id),
            seller_email VARCHAR(100) NOT NULL,
            seller_name VARCHAR(255),
            store_name VARCHAR(255),
            old_status VARCHAR(50),
            new_status VARCHAR(50),
            email_sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    print(" SellerStatusChanges table created!")
    
    # Create indexes
    print("\n Creating indexes...")
    cursor.execute("CREATE INDEX idx_seller_email ON ProductActivityLog(seller_email);")
    cursor.execute("CREATE INDEX idx_product_id ON ProductActivityLog(product_id);")
    cursor.execute("CREATE INDEX idx_created_at ON ProductActivityLog(created_at DESC);")
    cursor.execute("CREATE INDEX idx_products_seller ON Products(seller_email);")
    cursor.execute("CREATE INDEX idx_orders_email ON Orders(email);")
    cursor.execute("CREATE INDEX idx_status_changes_email_sent ON SellerStatusChanges(email_sent) WHERE email_sent = FALSE;")
    print(" Indexes created!")
    
    # Create trigger function
    print("\n Creating trigger function...")
    cursor.execute("""
        CREATE OR REPLACE FUNCTION log_seller_status_change()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.status IS DISTINCT FROM NEW.status THEN
                INSERT INTO SellerStatusChanges (
                    seller_id, seller_email, seller_name, store_name,
                    old_status, new_status, email_sent, created_at
                ) VALUES (
                    NEW.id, NEW.email, NEW.fullname, NEW.store_name,
                    OLD.status, NEW.status, FALSE, NOW()
                );
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    print(" Trigger function created!")
    
    # Create trigger
    print(" Creating trigger...")
    cursor.execute("""
        DROP TRIGGER IF EXISTS trg_seller_status_change ON Sellers;
        CREATE TRIGGER trg_seller_status_change
            AFTER UPDATE ON Sellers
            FOR EACH ROW
            EXECUTE FUNCTION log_seller_status_change();
    """)
    print(" Trigger created!")
    
    # Commit all changes
    conn.commit()
    
    # Verify tables
    print("\n" + "=" * 50)
    print(" VERIFICATION - Tables Created:")
    print("=" * 50)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    for table in tables:
        print(f"   {table[0]}")
    
    print("\n" + "=" * 50)
    print(" DATABASE SETUP COMPLETE!")
    print("=" * 50)
    print("\n All tables created successfully!")
    print(" Triggers and indexes created!")
    print(" Your database is ready to use!")
    print("\n Next step: Update your app.py to use PostgreSQL")
    
except Exception as e:
    print(f"\n ERROR: {e}")
    print("\n Make sure:")
    print("  1. DATABASE_URL is correct")
    print("  2. You have internet connection")
    print("  3. psycopg2-binary is installed")
    
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print("\n🔌 Database connection closed.")