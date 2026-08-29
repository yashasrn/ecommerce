from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
import random
import time
import re
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os

load_dotenv()

# ------------------- DATABASE SETUP -------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# ------------------- FLASK APP -------------------
app = Flask(__name__)
CORS(app)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") 

# ------------------- HUGGING FACE CONFIG -------------------
HF_API_KEY = os.getenv("HF_API_KEY",)
HF_API_URL = os.getenv("HF_API_URL")
FAKESTORE_API = os.getenv("FAKESTORE_API_URL")

# In-memory OTP store
otp_store = {}

# Cache for FakeStore products
fakestore_cache = {"products": None, "last_fetched": 0}

# ------------------- HARDCODED FAKESTORE PRODUCTS (FALLBACK) -------------------
# ------------------- PROFESSIONAL DEMO PRODUCTS FOR FREELANCING -------------------
# All images from Unsplash.com (free for commercial use)
# Created by: Your Name
# Safe to use in client demos and portfolios

DEMO_PRODUCTS = [
    # ELECTRONICS CATEGORY (10 products)
    {
        "id": 1,
        "title": "Premium Wireless Headphones",
        "price": 149.99,
        "description": "Immerse yourself in crystal-clear sound with these premium wireless headphones. Features active noise cancellation, 40-hour battery life, and comfortable over-ear design. Perfect for music lovers, travelers, and professionals.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "rating": {"rate": 4.8, "count": 342}
    },
    {
        "id": 2,
        "title": "Smart Fitness Watch",
        "price": 249.99,
        "description": "Track your health and fitness goals with advanced heart rate monitoring, GPS tracking, sleep analysis, and 50+ workout modes. Water-resistant up to 50m. Compatible with iOS and Android.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "rating": {"rate": 4.7, "count": 289}
    },
    {
        "id": 3,
        "title": "Wireless Bluetooth Speaker",
        "price": 89.99,
        "description": "Portable waterproof speaker with 360° sound and deep bass. 24-hour battery life, built-in microphone for calls, and pairs with multiple devices. Perfect for outdoor adventures.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&q=80",
        "rating": {"rate": 4.6, "count": 456}
    },
    {
        "id": 4,
        "title": "4K Action Camera",
        "price": 299.99,
        "description": "Capture your adventures in stunning 4K resolution. Waterproof up to 30m, image stabilization, wide-angle lens, and voice control. Includes mounting accessories.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800&q=80",
        "rating": {"rate": 4.9, "count": 178}
    },
    {
        "id": 5,
        "title": "Mechanical Gaming Keyboard",
        "price": 159.99,
        "description": "RGB mechanical keyboard with customizable keys and programmable macros. Tactile switches for precise typing and gaming. Durable aluminum frame with wrist rest.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1595225476474-87563907a212?w=800&q=80",
        "rating": {"rate": 4.7, "count": 523}
    },
    {
        "id": 6,
        "title": "Wireless Gaming Mouse",
        "price": 79.99,
        "description": "Ultra-precise wireless gaming mouse with 16,000 DPI sensor. Customizable RGB lighting, 6 programmable buttons, and ergonomic design. 70-hour battery life.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&q=80",
        "rating": {"rate": 4.5, "count": 392}
    },
    {
        "id": 7,
        "title": "Portable Power Bank 30000mAh",
        "price": 49.99,
        "description": "High-capacity power bank with fast charging technology. Charges up to 3 devices simultaneously. LED display shows remaining battery. Perfect for travel.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&q=80",
        "rating": {"rate": 4.6, "count": 678}
    },
    {
        "id": 8,
        "title": "Noise Cancelling Earbuds",
        "price": 129.99,
        "description": "True wireless earbuds with active noise cancellation and transparency mode. 8-hour battery, wireless charging case, and premium sound quality.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1590658165737-15a047b7b6c8?w=800&q=80",
        "rating": {"rate": 4.8, "count": 834}
    },
    {
        "id": 9,
        "title": "HD Webcam with Ring Light",
        "price": 99.99,
        "description": "Professional 1080p webcam with built-in ring light and dual microphones. Auto-focus and low-light correction. Perfect for video calls and streaming.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=800&q=80",
        "rating": {"rate": 4.7, "count": 412}
    },
    {
        "id": 10,
        "title": "Laptop Stand Adjustable",
        "price": 39.99,
        "description": "Ergonomic aluminum laptop stand with 6 adjustable angles. Improves posture and airflow. Compatible with all laptops 10-17 inches.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&q=80",
        "rating": {"rate": 4.5, "count": 289}
    },

    # MEN'S CLOTHING CATEGORY (8 products)
    {
        "id": 11,
        "title": "Classic Denim Jacket",
        "price": 79.99,
        "description": "Timeless denim jacket with a modern fit. 100% cotton, button closure, and multiple pockets. Perfect for casual outings and layering.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&q=80",
        "rating": {"rate": 4.6, "count": 234}
    },
    {
        "id": 12,
        "title": "Premium Cotton T-Shirt",
        "price": 29.99,
        "description": "Soft, breathable 100% organic cotton t-shirt. Classic crew neck design. Available in multiple colors. Perfect for everyday wear.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&q=80",
        "rating": {"rate": 4.7, "count": 567}
    },
    {
        "id": 13,
        "title": "Slim Fit Chinos",
        "price": 59.99,
        "description": "Modern slim-fit chino pants with stretch fabric for comfort. Versatile style suitable for both casual and business casual occasions.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=800&q=80",
        "rating": {"rate": 4.5, "count": 423}
    },
    {
        "id": 14,
        "title": "Leather Bomber Jacket",
        "price": 199.99,
        "description": "Genuine leather bomber jacket with quilted lining. Classic style with ribbed cuffs and hem. Premium quality that ages beautifully.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80",
        "rating": {"rate": 4.9, "count": 156}
    },
    {
        "id": 15,
        "title": "Casual Hoodie",
        "price": 49.99,
        "description": "Comfortable cotton-blend hoodie with kangaroo pocket and adjustable drawstring hood. Perfect for lounging or outdoor activities.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800&q=80",
        "rating": {"rate": 4.6, "count": 678}
    },
    {
        "id": 16,
        "title": "Formal Dress Shirt",
        "price": 69.99,
        "description": "Crisp white dress shirt with wrinkle-resistant fabric. Perfect fit for business and formal occasions. Easy care and iron-free.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&q=80",
        "rating": {"rate": 4.7, "count": 289}
    },
    {
        "id": 17,
        "title": "Performance Running Shorts",
        "price": 34.99,
        "description": "Lightweight athletic shorts with moisture-wicking fabric and built-in liner. Multiple pockets for storage. Perfect for running and training.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=800&q=80",
        "rating": {"rate": 4.5, "count": 512}
    },
    {
        "id": 18,
        "title": "Winter Wool Coat",
        "price": 249.99,
        "description": "Elegant wool-blend coat with modern tailored fit. Double-breasted design with interior pockets. Premium warmth and style.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800&q=80",
        "rating": {"rate": 4.8, "count": 134}
    },

    # WOMEN'S CLOTHING CATEGORY (8 products)
    {
        "id": 19,
        "title": "Elegant Summer Dress",
        "price": 89.99,
        "description": "Flowing maxi dress in lightweight fabric. Beautiful floral print with adjustable straps. Perfect for summer events and beach getaways.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&q=80",
        "rating": {"rate": 4.7, "count": 445}
    },
    {
        "id": 20,
        "title": "Yoga Leggings High-Waist",
        "price": 44.99,
        "description": "Stretchy high-waisted leggings with tummy control and moisture-wicking fabric. Perfect for yoga, gym, or casual wear. Multiple colors available.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=800&q=80",
        "rating": {"rate": 4.8, "count": 892}
    },
    {
        "id": 21,
        "title": "Leather Moto Jacket",
        "price": 179.99,
        "description": "Faux leather moto jacket with asymmetric zipper and multiple pockets. Edgy style with comfortable fit. Perfect for cool weather.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80",
        "rating": {"rate": 4.6, "count": 267}
    },
    {
        "id": 22,
        "title": "Cozy Knit Sweater",
        "price": 64.99,
        "description": "Soft cable-knit sweater in premium wool blend. Oversized fit for maximum comfort. Perfect for layering in cold weather.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&q=80",
        "rating": {"rate": 4.9, "count": 534}
    },
    {
        "id": 23,
        "title": "Blazer Professional",
        "price": 129.99,
        "description": "Tailored blazer with single-button closure. Perfect for office wear or business meetings. Fully lined with structured shoulders.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=800&q=80",
        "rating": {"rate": 4.7, "count": 312}
    },
    {
        "id": 24,
        "title": "Denim Skinny Jeans",
        "price": 69.99,
        "description": "Classic skinny jeans with stretch denim for comfort. Mid-rise fit with five-pocket styling. Versatile and flattering.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=80",
        "rating": {"rate": 4.6, "count": 678}
    },
    {
        "id": 25,
        "title": "Silk Blouse",
        "price": 79.99,
        "description": "Elegant silk blouse with button-down front. Luxurious feel and drape. Perfect for office or evening wear.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?w=800&q=80",
        "rating": {"rate": 4.8, "count": 234}
    },
    {
        "id": 26,
        "title": "Activewear Sports Bra",
        "price": 39.99,
        "description": "High-support sports bra with moisture-wicking fabric and removable pads. Comfortable for high-intensity workouts.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1609873814058-a8928924184a?w=800&q=80",
        "rating": {"rate": 4.7, "count": 567}
    },

    # JEWELRY CATEGORY (4 products)
    {
        "id": 27,
        "title": "Gold Plated Necklace",
        "price": 89.99,
        "description": "Delicate 18k gold-plated chain necklace with minimalist pendant. Hypoallergenic and tarnish-resistant. Perfect for everyday wear.",
        "category": "jewelery",
        "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&q=80",
        "rating": {"rate": 4.8, "count": 234}
    },
    {
        "id": 28,
        "title": "Silver Stud Earrings",
        "price": 49.99,
        "description": "Sterling silver stud earrings with cubic zirconia stones. Classic and elegant design. Comes with gift box.",
        "category": "jewelery",
        "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&q=80",
        "rating": {"rate": 4.9, "count": 567}
    },
    {
        "id": 29,
        "title": "Leather Wrap Bracelet",
        "price": 34.99,
        "description": "Handcrafted leather wrap bracelet with silver accents. Adjustable size with magnetic clasp. Unisex design.",
        "category": "jewelery",
        "image": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80",
        "rating": {"rate": 4.6, "count": 312}
    },
    {
        "id": 30,
        "title": "Designer Watch Classic",
        "price": 199.99,
        "description": "Minimalist watch with genuine leather strap and stainless steel case. Japanese quartz movement. Water-resistant.",
        "category": "jewelery",
        "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&q=80",
        "rating": {"rate": 4.7, "count": 445}
    }
]
# ------------------- DATABASE HELPER -------------------
def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# ------------------- HUGGING FACE HELPERS -------------------
def get_fakestore_products():
    """Fetch and cache products from FakeStore API with hardcoded fallback"""
    current_time = time.time()
    
    # Cache for 5 minutes
    if fakestore_cache["products"] and (current_time - fakestore_cache["last_fetched"]) < 300:
        print("✅ Returning cached FakeStore products")
        return fakestore_cache["products"]
    
    # Validate API URL
    if not FAKESTORE_API:
        print(" FAKESTORE_API_URL not configured, using hardcoded products")
        return DEMO_PRODUCTS
    
    try:
        print(f"🔄 Fetching from: {FAKESTORE_API}")
        response = requests.get(FAKESTORE_API, timeout=10)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            products = response.json()
            fakestore_cache["products"] = products
            fakestore_cache["last_fetched"] = current_time
            print(f"✅ Fetched {len(products)} products from FakeStore API")
            return products
        elif response.status_code == 403:
            print(" FakeStore API blocked (403 Forbidden) - Using hardcoded products")
            return DEMO_PRODUCTS
        else:
            print(f" FakeStore API returned status {response.status_code} - Using hardcoded products")
            return DEMO_PRODUCTS
            
    except requests.exceptions.Timeout:
        print(" FakeStore API request timed out - Using hardcoded products")
        return DEMO_PRODUCTS
    except requests.exceptions.ConnectionError:
        print(" Failed to connect to FakeStore API - Using hardcoded products")
        return DEMO_PRODUCTS
    except Exception as e:
        print(f" Error fetching FakeStore products: {type(e).__name__} - {str(e)}")
        print("   Using hardcoded products as fallback")
        return DEMO_PRODUCTS

def search_fakestore_products(query):
    """Search FakeStore products by query"""
    products = get_fakestore_products()
    if not products:
        return []
    
    query_lower = query.lower()
    matches = []
    
    for product in products:
        title = product.get('title', '').lower()
        category = product.get('category', '').lower()
        description = product.get('description', '').lower()
        
        if query_lower in title or query_lower in category or query_lower in description:
            matches.append(product)
        
        if len(matches) >= 3:
            break
    
    return matches

def call_huggingface_api(messages, max_tokens=150, temperature=0.7):
    """Call Hugging Face Inference API"""
    try:
        # Build prompt from messages
        prompt = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                prompt += f"System: {content}\n\n"
            elif role == 'user':
                prompt += f"User: {content}\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n"
        
        prompt += "Assistant:"
        
        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            return str(result)
        elif response.status_code == 503:
            return "MODEL_LOADING"
        else:
            print(f" HF API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f" HF API Exception: {str(e)}")
        return None

# ------------------- HELPER FUNCTIONS -------------------

def log_product_activity(product_id, seller_email, seller_name, action, product_title, old_data=None, new_data=None):
    """Log product changes to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ProductActivityLog (product_id, seller_email, seller_name, action, product_title, old_data, new_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            product_id,
            seller_email,
            seller_name,
            action,
            product_title,
            json.dumps(old_data) if old_data else None,
            json.dumps(new_data) if new_data else None
        ))
        
        conn.commit()
        print(f"✅ Logged activity: {action} - {product_title}")
        
    except Exception as e:
        print(f" Error logging activity: {str(e)}")
    finally:
        if conn:
            conn.close()


def send_activity_email(seller_email, seller_name, action, product_title, details=""):
    """Send email notification for product actions"""
    try:
        action_emoji = {
            "created": "➕",
            "updated": "✏️",
            "deleted": "🗑️",
            "published": "✅",
            "unpublished": "🔴"
        }
        
        emoji = action_emoji.get(action, "📦")
        
        subject = f"{emoji} Product {action.capitalize()}: {product_title}"
        
        body = f"""
Hello {seller_name},

Your product action was successful!

===========================
{emoji} ACTION: {action.upper()}
============================

Product: {product_title}
Action: {action.capitalize()}
Time: {time.strftime('%B %d, %Y at %I:%M %p')}

{details}

===============================

View your dashboard: http://localhost:5173/seller-dashboard

Best regards,
MyStore Team
"""
        
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = seller_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        
        print(f" Email sent to {seller_email} for {action}")
        
    except Exception as e:
        print(f" Error sending email: {str(e)}")

# ------------------- HOME / HEALTH CHECK -------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🎉 MyStore Backend API is Running!",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "auth": ["/signup", "/login", "/seller-login"],
            "products": ["/products", "/add-product"],
            "chat": ["/chat", "/chat-product-search"],
            "forgot_password": ["/forgot-password/send-otp"]
        }
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')}), 200

# ------------------- SIGNUP -------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    print("📝 Data:", data)
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already registered"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        conn.commit()
        return jsonify({"message": "Signup successful!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- SEND OTP -------------------
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "expires": time.time() + 300}

    try:
        print(f"🔑 [OTP for {email}] → {otp}")
        
        # Use Resend for email
        import resend
        
        RESEND_API_KEY = os.getenv("RESEND_API_KEY")
        resend.api_key = RESEND_API_KEY
        
        params = {
            "from": "MyStore <onboarding@resend.dev>",
            "to": [email],
            "subject": "Your OTP Code - MyStore",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;">Your OTP Code</h2>
                    <p>Your OTP is:</p>
                    <div style="background: #f4f4f4; padding: 15px; text-align: center; font-size: 32px; font-weight: bold; color: #4CAF50; letter-spacing: 5px; border-radius: 8px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #666;">This code expires in 5 minutes.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">MyStore Team</p>
                </div>
            """
        }
        
        email_response = resend.Emails.send(params)
        print(f" Resend email sent! ID: {email_response['id']}")
        
        return jsonify({"message": "OTP sent successfully!"})
        
    except Exception as e:
        print(f" Resend error: {str(e)}")
        return jsonify({"error": f"Failed to send OTP: {str(e)}"}), 500



# ------------------- VERIFY OTP -------------------
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email", "").strip()
    otp = data.get("otp", "").strip()

    if not email or not otp:
        return jsonify({"error": "Email and OTP required"}), 400

    record = otp_store.get(email)
    if not record:
        return jsonify({"error": "OTP not found"}), 400
    if time.time() > record["expires"]:
        return jsonify({"error": "OTP expired"}), 400

    if otp == record["otp"]:
        del otp_store[email]
        return jsonify({"message": "OTP verified successfully!"})
    else:
        return jsonify({"error": "Invalid OTP"}), 400

# ------------------- LOGIN -------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password, name FROM Users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Invalid email or password"}), 401

        if bcrypt.checkpw(password.encode('utf-8'), row[0].encode('utf-8')):
            return jsonify({"message": f"Welcome {row[1]}!"})
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- SEND ORDER EMAIL -------------------
@app.route("/send-order-email", methods=["POST"])
def send_order_email():
    data = request.json
    email = data.get("email")
    fullName = data.get("fullName")
    items = data.get("items", [])
    totalPrice = data.get("totalPrice")
    addressInfo = data.get("address", {})

    if not email or not fullName or not items or not totalPrice or not addressInfo:
        return jsonify({"error": "Missing order information"}), 400

    items_text = "\n".join([f"{item['quantity']} x {item['title']} = ${item['price'] * item['quantity']:.2f}" for item in items])
    body = f"""
Hello {fullName},

Thank you for your order!

{items_text}

Total: ${totalPrice:.2f}

Delivering to:
{addressInfo.get('fullName')}
{addressInfo.get('address')}, {addressInfo.get('city')}, {addressInfo.get('state')} - {addressInfo.get('pincode')}
Phone: {addressInfo.get('phone')}
"""

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = "Your Order Confirmation"
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"message": "Order confirmation email sent successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------- FORGOT PASSWORD: SEND OTP -------------------
@app.route("/forgot-password/send-otp", methods=["POST"])
def forgot_password_send_otp():
    data = request.json
    email = data.get("email", "").strip()
    user_type = data.get("userType", "customer").strip()  # "customer" or "seller"

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check the right table
        if user_type == "seller":
            cursor.execute("SELECT fullname FROM Sellers WHERE email = %s", (email,))
        else:
            cursor.execute("SELECT name FROM Users WHERE email = %s", (email,))
        
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": f"No {user_type} account found with this email"}), 404

        user_name = user[0]
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        otp_store[email] = {
            "otp": otp, 
            "expires": time.time() + 300,
            "user_type": user_type
        }

        print(f"🔑 [Password Reset OTP for {user_type}: {email}] → {otp}")

        # Send email
        subject = "🔐 Password Reset OTP - MyStore"
        body = f"""
Hello {user_name},

You requested to reset your password.

Your OTP is: {otp}

This code expires in 5 minutes.

If you didn't request this, please ignore this email.

Best regards,
MyStore Team
"""
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"message": "OTP sent to your email!"}), 200

    except Exception as e:
        print(f" Error sending OTP: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- FORGOT PASSWORD: VERIFY OTP -------------------
@app.route("/forgot-password/verify-otp", methods=["POST"])
def forgot_password_verify_otp():
    data = request.json
    email = data.get("email", "").strip()
    otp = data.get("otp", "").strip()
    user_type = data.get("userType", "customer").strip()

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    record = otp_store.get(email)
    
    if not record:
        return jsonify({"error": "OTP not found. Please request a new one."}), 400
    
    if record.get("user_type") != user_type:
        return jsonify({"error": "Invalid request"}), 400
    
    if time.time() > record["expires"]:
        del otp_store[email]
        return jsonify({"error": "OTP expired. Please request a new one."}), 400

    if otp == record["otp"]:
        return jsonify({"message": "OTP verified successfully!"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 400

# ------------------- FORGOT PASSWORD: RESET PASSWORD -------------------
@app.route("/forgot-password/reset", methods=["POST"])
def forgot_password_reset():
    data = request.json
    email = data.get("email", "").strip()
    otp = data.get("otp", "").strip()
    new_password = data.get("newPassword", "").strip()
    user_type = data.get("userType", "customer").strip()

    if not email or not otp or not new_password:
        return jsonify({"error": "All fields are required"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Verify OTP again
    record = otp_store.get(email)
    if not record or record["otp"] != otp or record.get("user_type") != user_type:
        return jsonify({"error": "Invalid or expired OTP"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update the right table
        if user_type == "seller":
            cursor.execute("SELECT fullname FROM Sellers WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({"error": "Seller not found"}), 404
            
            user_name = user[0]
            cursor.execute("UPDATE Sellers SET password = %s WHERE email = %s", (hashed_password, email))
            
        else:  # customer
            cursor.execute("SELECT name FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            user_name = user[0]
            cursor.execute("UPDATE Users SET password = %s WHERE email = %s", (hashed_password, email))

        conn.commit()

        # Remove OTP from store
        del otp_store[email]

        print(f"✅ Password reset successful for {user_type}: {email}")

        # Send confirmation email
        subject = "✅ Password Reset Successful - MyStore"
        body = f"""
Hello {user_name},

Your password has been successfully reset.

You can now login with your new password.

If you didn't make this change, please contact support immediately.

Best regards,
MyStore Team
"""
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"message": "Password reset successful! Redirecting to login..."}), 200

    except Exception as e:
        print(f" Error resetting password: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- SAVE ORDER TO DATABASE -------------------
@app.route("/save-order", methods=["POST"])
def save_order():
    data = request.json
    email = data.get("email")
    fullName = data.get("fullName")
    items = data.get("items", [])
    totalPrice = data.get("totalPrice")
    addressInfo = data.get("address", {})

    if not email or not fullName or not items or not totalPrice or not addressInfo:
        return jsonify({"error": "Missing order information"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Orders (email, fullName, totalPrice, address, city, state, pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            email,
            fullName,
            totalPrice,
            addressInfo.get('address'),
            addressInfo.get('city'),
            addressInfo.get('state'),
            addressInfo.get('pincode')
        ))
        order_id = cursor.fetchone()[0]

        for item in items:
            cursor.execute("""
                INSERT INTO OrderItems (order_id, title, price, quantity)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['title'], item['price'], item['quantity']))

        conn.commit()
        return jsonify({"message": "Order saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- GET USER ORDERS -------------------
@app.route("/get-orders/<email>", methods=["GET"])
def get_orders(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, fullName, totalPrice, address, city, state, pincode
            FROM Orders
            WHERE email = %s
            ORDER BY id DESC
        """, (email,))
        orders = cursor.fetchall()

        orders_list = []
        for order in orders:
            order_id = order[0]
            cursor.execute("""
                SELECT title, price, quantity
                FROM OrderItems
                WHERE order_id = %s
            """, (order_id,))
            items = cursor.fetchall()
            items_list = [
                {"title": i[0], "price": float(i[1]), "quantity": i[2]} for i in items
            ]

            orders_list.append({
                "orderId": order_id,
                "fullName": order[1],
                "totalPrice": float(order[2]),
                "address": order[3],
                "city": order[4],
                "state": order[5],
                "pincode": order[6],
                "items": items_list
            })

        return jsonify(orders_list)
    except Exception as e:
        print(" Error fetching orders:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- SELLER SIGNUP -------------------
@app.route("/seller-signup", methods=["POST"])
def apply_seller():
    data = request.json
    print("📝 Incoming JSON:", data)
    
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    storeName = data.get("storeName", "").strip()
    store_description = data.get("store_description", "").strip()
    password = data.get("password", "").strip()

    if not name or not email or not storeName or not store_description or not password:
        return jsonify({"error": "All fields are required"}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Sellers WHERE email = %s", (email,))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": "This email is already registered as a seller. Please login or use a different email."}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor.execute("""
            INSERT INTO Sellers (fullname, store_name, store_description, password, email, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, storeName, store_description, hashed_password, email, "Pending"))
        
        conn.commit()

        subject = "Seller Application Received"
        body = f"""
Hello {name},

Thank you for applying to be a seller on our platform!

Your application is currently **Pending Review**.  
You'll receive another email once your request has been approved.

Store Name: {storeName}

Best,
MyStore Team
"""
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"message": "Seller application submitted successfully! Check your email for confirmation."}), 201

    except Exception as e:
        print(" Error during seller signup:", str(e))
        return jsonify({"error": f"Failed to submit application: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# ------------------- SELLER LOGIN -------------------
@app.route("/seller-login", methods=["POST"])
def seller_login():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password, fullname, status FROM Sellers WHERE email = %s", (email,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Invalid email or password"}), 401

        stored_password, name, status = row

        if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401

        status_lower = status.lower()
        
        if status_lower == "pending":
            return jsonify({
                "error": "Your account is pending approval. Please wait for admin to approve your application."
            }), 403
        
        elif status_lower == "rejected":
            return jsonify({
                "error": "Your seller application was rejected. Please contact support."
            }), 403
        
        elif status_lower == "approved":
            return jsonify({
                "message": f"Welcome {name}!",
                "name": name,
                "email": email,
                "status": "approved"
            }), 200
        
        else:
            return jsonify({"error": "Invalid account status"}), 403

    except Exception as e:
        print(" Error during seller login:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- ADD PRODUCT -------------------
@app.route("/add-product", methods=["POST"])
def add_product():
    data = request.json
    print("📦 Incoming product data:", data)
    
    title = data.get("title", "").strip()
    price = data.get("price")
    description = data.get("description", "").strip()
    category = data.get("category", "").strip()
    image = data.get("image", "").strip()
    seller_email = data.get("sellerId", "").strip()
    seller_name = data.get("sellerName", "").strip()

    if not title or not price or not description or not category:
        return jsonify({"error": "All required fields must be filled"}), 400

    if not seller_email:
        return jsonify({"error": "Seller information missing"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM Sellers WHERE email = %s", (seller_email,))
        seller = cursor.fetchone()
        
        if not seller:
            return jsonify({"error": "Seller not found"}), 404
        
        if seller[0].lower() != "approved":
            return jsonify({
                "error": f"Only approved sellers can add products. Your status: {seller[0]}"
            }), 403

        if not image:
            image = "https://via.placeholder.com/300x300?text=No+Image"
        
        print(f"💾 Saving product: {title} by {seller_name} as DRAFT")
        cursor.execute("""
            INSERT INTO Products (title, price, description, category, image, seller_email, seller_name, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (title, float(price), description, category, image, seller_email, seller_name, 'draft'))
        
        product_id = cursor.fetchone()[0]
        conn.commit()
        print(f" Product saved with ID: {product_id} (Status: draft)")

        # LOG ACTIVITY
        log_product_activity(product_id, seller_email, seller_name, "created", title)

        subject = "📦 Product Saved as Draft"
        body = f"""
Hello {seller_name},

Your product has been successfully saved as a DRAFT.

Product Details:
• Name: {title}
• Price: ${price}
• Category: {category}
• Status: DRAFT (Not visible to customers yet)

Next Steps:
1. Review your product in the dashboard
2. Edit if needed
3. Publish when ready to make it live

Login to Dashboard: http://localhost:5173/seller-dashboard

Best regards,
MyStore Team
"""
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = seller_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        
        print(f"📧 Email sent to {seller_email}")

        return jsonify({
            "message": "Product saved as draft! Check your email and dashboard.",
            "product_id": product_id,
            "status": "draft"
        }), 201

    except Exception as e:
        print(" Error adding product:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# ------------------- GET SELLER'S PRODUCTS -------------------
@app.route("/seller-products", methods=["GET"])
def get_seller_products():
    seller_email = request.args.get('sellerId')
    
    if not seller_email:
        return jsonify({"error": "Seller email is required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM Sellers WHERE email = %s", (seller_email,))
        seller = cursor.fetchone()
        
        if not seller:
            return jsonify({"error": "Seller not found"}), 404
        
        if seller[0].lower() != "approved":
            return jsonify({"error": "Only approved sellers can view products"}), 403
        
        cursor.execute("""
            SELECT id, title, price, description, category, image, seller_email, seller_name, status, created_at
            FROM Products
            WHERE seller_email = %s
            ORDER BY created_at DESC
        """, (seller_email,))
        
        rows = cursor.fetchall()
        
        products = [
            {
                "id": row[0],
                "title": row[1],
                "price": float(row[2]) if row[2] else 0,
                "description": row[3] if row[3] else "",
                "category": row[4] if row[4] else "",
                "image": row[5] if row[5] else "https://via.placeholder.com/300x300?text=No+Image",
                "sellerId": row[6] if row[6] else "",
                "sellerName": row[7] if row[7] else "",
                "status": row[8] if row[8] else "draft",
                "createdAt": row[9].isoformat() if row[9] else "",
                "rating": {"rate": 0, "count": 0}
            }
            for row in rows
        ]
        
        print(f" Found {len(products)} products for seller: {seller_email}")
        return jsonify(products), 200
        
    except Exception as e:
        print(" Error fetching seller products:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- DELETE PRODUCT -------------------
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT title, seller_email, seller_name FROM Products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        title, seller_email, seller_name = product
        
        cursor.execute("DELETE FROM Products WHERE id = %s", (product_id,))
        conn.commit()
        
        print(f" Product deleted: {title} (ID: {product_id})")
        
        # LOG ACTIVITY
        log_product_activity(product_id, seller_email, seller_name, "deleted", title)
        
        # SEND EMAIL
        send_activity_email(
            seller_email, 
            seller_name, 
            "deleted", 
            title,
            f"The product '{title}' has been permanently removed from your store."
        )
        
        return jsonify({"message": "Product deleted successfully!"}), 200
        
    except Exception as e:
        print(" Error deleting product:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- PUBLISH PRODUCT -------------------
@app.route("/products/<int:product_id>/publish", methods=["PATCH"])
def publish_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT title, seller_email, seller_name, status FROM Products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        title, seller_email, seller_name, old_status = product
        
        cursor.execute("UPDATE Products SET status = %s WHERE id = %s", ('published', product_id))
        conn.commit()
        
        print(f" Product published: {title} (ID: {product_id})")
        
        # LOG ACTIVITY
        log_product_activity(
            product_id, 
            seller_email, 
            seller_name, 
            "published", 
            title,
            old_data={"status": old_status},
            new_data={"status": "published"}
        )
        
        # SEND EMAIL
        send_activity_email(
            seller_email, 
            seller_name, 
            "published", 
            title,
            f"Your product '{title}' is now LIVE and visible to all customers on the store! 🎉"
        )
        
        return jsonify({
            "message": "Product published successfully!",
            "status": "published"
        }), 200
        
    except Exception as e:
        print(" Error publishing product:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- UNPUBLISH PRODUCT -------------------
@app.route("/products/<int:product_id>/unpublish", methods=["PATCH"])
def unpublish_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT title, seller_email, seller_name, status FROM Products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        title, seller_email, seller_name, old_status = product
        
        cursor.execute("UPDATE Products SET status = %s WHERE id = %s", ('draft', product_id))
        conn.commit()
        
        print(f"🔴 Product unpublished: {title} (ID: {product_id})")
        
        # LOG ACTIVITY
        log_product_activity(
            product_id, 
            seller_email, 
            seller_name, 
            "unpublished", 
            title,
            old_data={"status": old_status},
            new_data={"status": "draft"}
        )
        
        # SEND EMAIL
        send_activity_email(
            seller_email, 
            seller_name, 
            "unpublished", 
            title,
            f"Your product '{title}' has been moved back to DRAFT status and is no longer visible to customers."
        )
        
        return jsonify({
            "message": "Product unpublished successfully!",
            "status": "draft"
        }), 200
        
    except Exception as e:
        print(" Error unpublishing product:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- CHECK SELLER STATUS -------------------
@app.route("/check-seller-status", methods=["POST"])
def check_seller_status():
    data = request.json
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT fullname, status FROM Sellers WHERE email = %s", (email,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Seller not found", "isApproved": False}), 404

        name, status = row
        status_lower = status.lower()
        
        return jsonify({
            "name": name,
            "email": email,
            "status": status_lower,
            "isApproved": status_lower == "approved"
        }), 200

    except Exception as e:
        print(" Error checking seller status:", str(e))
        return jsonify({"error": str(e), "isApproved": False}), 500
    finally:
        conn.close()

# ------------------- GET SINGLE PRODUCT -------------------
@app.route("/products/<int:product_id>", methods=["GET"])
def get_single_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, price, description, category, image, seller_email, seller_name, status
            FROM Products
            WHERE id = %s
        """, (product_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Product not found"}), 404
        
        product = {
            "id": row[0],
            "title": row[1],
            "price": float(row[2]) if row[2] else 0,
            "description": row[3] if row[3] else "",
            "category": row[4] if row[4] else "",
            "image": row[5] if row[5] else "",
            "sellerId": row[6] if row[6] else "",
            "sellerName": row[7] if row[7] else "",
            "status": row[8] if row[8] else "draft"
        }
        
        return jsonify(product), 200
        
    except Exception as e:
        print(" Error fetching product:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- UPDATE PRODUCT -------------------
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    
    title = data.get("title", "").strip()
    price = data.get("price")
    description = data.get("description", "").strip()
    category = data.get("category", "").strip()
    image = data.get("image", "").strip()
    
    if not title or not price or not description or not category:
        return jsonify({"error": "All required fields must be filled"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, price, description, category, image, seller_email, seller_name 
            FROM Products 
            WHERE id = %s
        """, (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        old_title, old_price, old_desc, old_cat, old_img, seller_email, seller_name = product
        
        old_data = {
            "title": old_title,
            "price": float(old_price),
            "description": old_desc,
            "category": old_cat,
            "image": old_img
        }
        
        new_data = {
            "title": title,
            "price": float(price),
            "description": description,
            "category": category,
            "image": image
        }
        
        cursor.execute("""
            UPDATE Products 
            SET title = %s, price = %s, description = %s, category = %s, image = %s
            WHERE id = %s
        """, (title, float(price), description, category, image, product_id))
        
        conn.commit()
        
        print(f" Product updated: {title} (ID: {product_id})")
        
        # LOG ACTIVITY
        log_product_activity(
            product_id, 
            seller_email, 
            seller_name, 
            "updated", 
            title,
            old_data=old_data,
            new_data=new_data
        )
        
        # Build change summary
        changes = []
        if old_title != title:
            changes.append(f"• Title: '{old_title}' → '{title}'")
        if float(old_price) != float(price):
            changes.append(f"• Price: ${old_price} → ${price}")
        if old_desc != description:
            changes.append(f"• Description updated")
        if old_cat != category:
            changes.append(f"• Category: {old_cat} → {category}")
        if old_img != image:
            changes.append(f"• Image updated")
        
        change_summary = "\n".join(changes) if changes else "No changes detected"
        
        # SEND EMAIL
        send_activity_email(
            seller_email, 
            seller_name, 
            "updated", 
            title,
            f"Changes made:\n{change_summary}"
        )
        
        return jsonify({"message": "Product updated successfully!"}), 200
        
    except Exception as e:
        print(" Error updating product:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- GET SELLER ACTIVITY -------------------
@app.route("/seller-activity", methods=["GET"])
def get_seller_activity():
    seller_email = request.args.get('sellerId')
    
    if not seller_email:
        return jsonify({"error": "Seller email required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, product_id, action, product_title, created_at
            FROM ProductActivityLog
            WHERE seller_email = %s
            ORDER BY created_at DESC
            LIMIT 50
        """, (seller_email,))
        
        rows = cursor.fetchall()
        
        activities = [
            {
                "id": row[0],
                "product_id": row[1],
                "action": row[2],
                "product_title": row[3],
                "timestamp": row[4].isoformat() if row[4] else ""
            }
            for row in rows
        ]
        
        return jsonify(activities), 200
        
    except Exception as e:
        print(" Error fetching seller activity:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- FETCH PRODUCTS (ALL: FAKESTORE + SELLERS) -------------------
@app.route("/products", methods=["GET"])
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get ALL published products (FakeStore + Seller products)
        cursor.execute("SELECT id, title, price, description, category, image FROM Products WHERE status = 'published' ORDER BY id DESC")
        rows = cursor.fetchall()

        products = [
            {
                "id": row[0],
                "title": row[1],
                "price": float(row[2]),
                "description": row[3],
                "category": row[4],
                "image": row[5],
                "rating": {"rate": 4.5, "count": 10},
            }
            for row in rows
        ]
        
        return jsonify(products), 200
        
    except Exception as e:
        print(f" Error fetching products: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
# ------------------- ADMIN: SEED DATABASE WITH FAKESTORE PRODUCTS -------------------
@app.route("/admin/seed-fakestore", methods=["GET"])
def seed_fakestore():
    """Seed database with professional demo products"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM Products WHERE seller_name = 'Demo Store'")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            return jsonify({
                "message": f" Already seeded! {existing_count} demo products exist.",
                "skipped": True,
                "existing_count": existing_count
            }), 200
        
        print("📦 Seeding database with professional demo products...")
        
        # Get demo products
        demo_products = DEMO_PRODUCTS  # Changed from get_fakestore_products()
        
        if not demo_products or len(demo_products) == 0:
            return jsonify({"error": "No demo products available"}), 500
        
        print(f"✅ Found {len(demo_products)} demo products")
        
        # Insert into database
        inserted = 0
        errors = []
        
        for product in demo_products:
            try:
                cursor.execute("""
                    INSERT INTO Products (title, price, description, category, image, seller_email, seller_name, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    product.get('title', 'Unknown Product'),
                    float(product.get('price', 0)),
                    product.get('description', 'No description available'),
                    product.get('category', 'general'),
                    product.get('image', 'https://via.placeholder.com/300'),
                    'demo@mystoreplatform.com',  
                    'Demo Store',  
                    'published'
                ))
                inserted += 1
            except Exception as e:
                error_msg = f"Error inserting '{product.get('title', 'Unknown')}': {str(e)}"
                print(f" {error_msg}")
                errors.append(error_msg)
                continue
        
        conn.commit()
        
        print(f"✅ Successfully inserted {inserted}/{len(demo_products)} products")
        
        response_data = {
            "message": f"✅ Successfully seeded database with {inserted} demo products!",
            "inserted": inserted,
            "total_available": len(demo_products),
            "success": True
        }
        
        if errors:
            response_data["errors"] = errors[:5]
            response_data["error_count"] = len(errors)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        print(f" Error seeding database: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": f"Database error: {str(e)}",
            "type": type(e).__name__
        }), 500
    finally:
        if conn:
            conn.close()

# ------------------- DEBUG: TEST FAKESTORE API CONNECTION -------------------
@app.route("/debug/test-fakestore-api", methods=["GET"])
def test_fakestore_api():
    """Test direct connection to FakeStore API"""
    import traceback
    
    result = {
        "fakestore_url": FAKESTORE_API,
        "url_configured": bool(FAKESTORE_API),
        "test_results": {}
    }
    
    if not FAKESTORE_API:
        result["error"] = " FAKESTORE_API_URL not configured in .env file"
        result["fix"] = "Add FAKESTORE_API_URL=\"https://fakestoreapi.com/products?limit=100\" to your .env file"
        return jsonify(result), 500
    
    try:
        print(f"🧪 Testing FakeStore API: {FAKESTORE_API}")
        
        response = requests.get(FAKESTORE_API, timeout=10)
        
        result["test_results"] = {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response_size": len(response.content),
            "content_type": response.headers.get('Content-Type', 'unknown')
        }
        
        if response.status_code == 200:
            products = response.json()
            result["test_results"]["products_count"] = len(products)
            result["test_results"]["sample_product"] = products[0] if products else None
            result["message"] = f"✅ SUCCESS! Fetched {len(products)} products"
        else:
            result["error"] = f" API returned status {response.status_code}"
            result["response_text"] = response.text[:200]
        
        return jsonify(result), 200
        
    except requests.exceptions.Timeout:
        result["error"] = " Request timed out - API took too long to respond"
        return jsonify(result), 500
        
    except requests.exceptions.ConnectionError as e:
        result["error"] = f" Connection failed - check internet connection"
        result["details"] = str(e)
        return jsonify(result), 500
        
    except Exception as e:
        result["error"] = f" Unexpected error: {type(e).__name__}"
        result["details"] = str(e)
        result["traceback"] = traceback.format_exc()
        return jsonify(result), 500

# ------------------- ADMIN: CHECK SEED STATUS -------------------
@app.route("/admin/seed-status", methods=["GET"])
def seed_status():
    """
    Check how many FakeStore products are in database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count FakeStore products
        cursor.execute("SELECT COUNT(*) FROM Products WHERE seller_name = 'FakeStore'")
        fakestore_count = cursor.fetchone()[0]
        
        # Count seller products
        cursor.execute("SELECT COUNT(*) FROM Products WHERE seller_name != 'FakeStore'")
        seller_count = cursor.fetchone()[0]
        
        # Total published products
        cursor.execute("SELECT COUNT(*) FROM Products WHERE status = 'published'")
        total_published = cursor.fetchone()[0]
        
        return jsonify({
            "fakestore_products": fakestore_count,
            "seller_products": seller_count,
            "total_published": total_published,
            "seeded": fakestore_count > 0
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- ADMIN: LIST ALL SELLERS -------------------
@app.route("/admin/sellers", methods=["GET"])
def admin_list_sellers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT email, fullname, status, store_name FROM Sellers ORDER BY id DESC")
        sellers = cursor.fetchall()
        
        return jsonify({
            "total": len(sellers),
            "sellers": [
                {
                    "email": s[0],
                    "name": s[1],
                    "status": s[2],
                    "store": s[3]
                } for s in sellers
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- ADMIN: APPROVE SELLER -------------------
@app.route("/admin/approve/<email>", methods=["GET"])
def admin_approve_seller(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE Sellers SET status = %s WHERE email = %s RETURNING fullname", ('Approved', email))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Seller not found"}), 404
        
        conn.commit()
        
        return jsonify({
            "message": f"✅ Seller '{result[0]}' ({email}) approved successfully!",
            "success": True
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- UPDATE SELLER STATUS -------------------
@app.route("/update-seller-status", methods=["POST"])
def update_seller_status():
    data = request.json
    email = data.get("email", "").strip()
    new_status = data.get("status", "").strip().capitalize()

    if not email or not new_status:
        return jsonify({"error": "Email and new status are required"}), 400
    if new_status not in ["Approved", "Rejected"]:
        return jsonify({"error": "Invalid status. Must be Approved or Rejected"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT fullname, status FROM Sellers WHERE email = %s", (email,))
        seller = cursor.fetchone()
        if not seller:
            return jsonify({"error": "Seller not found"}), 404

        name, old_status = seller
        if old_status == new_status:
            return jsonify({"message": f"Seller is already {new_status}."}), 200

        cursor.execute("UPDATE Sellers SET status = %s WHERE email = %s", (new_status, email))
        conn.commit()

        subject = "Seller Account Status Update"
        if new_status == "Approved":
            body = f"""
Hello {name},

🎉 Congratulations! Your seller account has been APPROVED by our team.

You can now start adding products and selling on our platform.

Thank you,
MyStore Team
"""
        else:
            body = f"""
Hello {name},

We regret to inform you that your seller application has been REJECTED.

If you believe this is a mistake or would like to reapply, please contact our support team.

Best regards,
MyStore Team
"""

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"message": f"Seller status updated to {new_status} and email sent."})

    except Exception as e:
        print(" Error updating seller status:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- CONTACT US -------------------
@app.route("/contact-us", methods=["POST"])
def contact_us():
    data = request.json
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"error": "Name, email, and message are required"}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ContactMessages (name, email, subject, message, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, subject or "General Inquiry", message, "New"))
        
        conn.commit()
        print(f"💬 Contact message saved from {name} ({email})")

        user_subject = "We Received Your Message! 📧"
        user_body = f"""
Hello {name},

Thank you for contacting MyStore!

We have received your message and will get back to you within 24-48 hours.

Your Message:
================================
Subject: {subject or 'General Inquiry'}

{message}
=================================

Best regards,
MyStore Support Team

---
This is an automated confirmation email.
"""

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = user_subject
        msg.attach(MIMEText(user_body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print(f" Confirmation email sent to {email}")

        admin_subject = f"🔔 New Contact Message from {name}"
        admin_body = f"""
New contact form submission:

From: {name}
Email: {email}
Subject: {subject or 'General Inquiry'}

Message:
{message}

================================
Received at: {time.strftime('%B %d, %Y at %I:%M %p')}
"""

        admin_msg = MIMEMultipart()
        admin_msg["From"] = EMAIL_ADDRESS
        admin_msg["To"] = EMAIL_ADDRESS
        admin_msg["Subject"] = admin_subject
        admin_msg.attach(MIMEText(admin_body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(admin_msg)

        print(f" Admin notification sent")

        return jsonify({
            "message": "Thank you for contacting us! We'll get back to you soon.",
            "success": True
        }), 200

    except Exception as e:
        print(" Error processing contact form:", str(e))
        return jsonify({"error": f"Failed to send message: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# ------------------- GET ALL CONTACT MESSAGES -------------------
@app.route("/admin/contact-messages", methods=["GET"])
def get_contact_messages():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, subject, message, created_at, status
            FROM ContactMessages
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        messages = [
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "subject": row[3],
                "message": row[4],
                "createdAt": row[5].isoformat() if row[5] else "",
                "status": row[6]
            }
            for row in rows
        ]
        
        return jsonify(messages), 200
        
    except Exception as e:
        print(" Error fetching contact messages:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ------------------- CHATBOT WITH HUGGING FACE -------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    print(f"\n{'='*60}")
    print(f" Incoming message: {user_message}")
    print(f"{'='*60}")
    
    try:
        system_prompt = """You are Emma, a friendly AI customer support assistant for MyStore, an e-commerce platform. 
        You help customers with:
        - Product inquiries
        - Order tracking
        - Return policies
        - Account issues
        - General shopping questions
        
        Be friendly, professional, and concise. If you don't know something, admit it and suggest contacting support."""
        
        print(" Calling Hugging Face API...")
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        
        bot_reply = call_huggingface_api(messages, max_tokens=150, temperature=0.7)
        
        if bot_reply and bot_reply != "MODEL_LOADING":
            print(f" Bot replied: {bot_reply[:100]}...")
            print(f"{'='*60}\n")
            
            return jsonify({
                "reply": bot_reply,
                "success": True,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }), 200
        
        elif bot_reply == "MODEL_LOADING":
            return jsonify({
                "reply": "I'm waking up! This might take 20-30 seconds. Please ask again in a moment. 😊",
                "success": False,
                "fallback": True,
                "model_loading": True
            }), 200
        
        else:
            raise Exception("No response from AI")
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        print(f" ERROR!")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print(error_details)
        print(f"{'='*60}\n")
        
        fallback_responses = {
            "shipping": "We offer free shipping on orders over $50! Standard delivery takes 3-5 business days. 📦",
            "return": "We have a hassle-free 30-day return policy! Email support@mystore.com with your order number. 🔄",
            "payment": "We accept all major credit cards, PayPal, and debit cards. All transactions are SSL secured. 💳",
            "default": "I'm having trouble connecting right now. Please email us at support@mystore.com or call 1-800-MYSTORE. We're here 24/7! 😊"
        }
        
        user_lower = user_message.lower()
        if any(word in user_lower for word in ['ship', 'delivery', 'track']):
            fallback = fallback_responses['shipping']
        elif any(word in user_lower for word in ['return', 'refund', 'exchange']):
            fallback = fallback_responses['return']
        elif any(word in user_lower for word in ['pay', 'payment', 'credit', 'card']):
            fallback = fallback_responses['payment']
        else:
            fallback = fallback_responses['default']
        
        return jsonify({
            "reply": fallback,
            "success": False,
            "fallback": True,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }), 200

# ------------------- CHAT WITH CONVERSATION HISTORY -------------------
@app.route("/chat-with-history", methods=["POST"])
def chat_with_history():
    data = request.json
    user_message = data.get("message", "").strip()
    conversation_history = data.get("history", [])
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        system_prompt = """You are Emma, MyStore's friendly AI assistant. You help customers with shopping, orders, returns, and general questions. Be helpful, concise, and friendly!"""
        
        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend(conversation_history[-6:])
        messages.append({'role': 'user', 'content': user_message})
        
        bot_reply = call_huggingface_api(messages, max_tokens=150, temperature=0.7)
        
        if bot_reply and bot_reply != "MODEL_LOADING":
            return jsonify({
                "reply": bot_reply,
                "success": True,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }), 200
        else:
            raise Exception("No response from AI")
        
    except Exception as e:
        print(f" Chatbot Error: {str(e)}")
        return jsonify({
            "reply": "I'm experiencing technical difficulties. Please try again or contact support@mystore.com 💙",
            "success": False,
            "fallback": True
        }), 200

# ------------------- SMART PRODUCT SEARCH CHATBOT (FakeStore API) -------------------
@app.route("/chat-product-search", methods=["POST"])
def chat_product_search():
    data = request.json
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        print(f" Searching FakeStore API for: {user_message}")
        
        # Search FakeStore API
        fakestore_products = search_fakestore_products(user_message)
        
        # Also search your database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, price, category, image 
            FROM Products 
            WHERE status = 'published' 
            AND (title ILIKE %s OR category ILIKE %s OR description ILIKE %s)
            LIMIT 3
        """, (f'%{user_message}%', f'%{user_message}%', f'%{user_message}%'))
        
        db_products = cursor.fetchall()
        conn.close()
        
        all_products = []
        
        # Add FakeStore products
        for p in fakestore_products[:2]:
            all_products.append({
                "title": p.get('title', 'Unknown'),
                "price": float(p.get('price', 0)),
                "category": p.get('category', 'General'),
                "image": p.get('image', ''),
                "source": "fakestore"
            })
        
        # Add database products
        for p in db_products[:2]:
            all_products.append({
                "title": p[0],
                "price": float(p[1]),
                "category": p[2],
                "image": p[3],
                "source": "mystore"
            })
        
        if all_products:
            product_info = "\n".join([
                f"- {p['title']} (${p['price']}) in {p['category']} category"
                for p in all_products
            ])
            
            enhanced_prompt = f"""You are Emma, MyStore's AI shopping assistant. 

The customer asked: "{user_message}"

We found these relevant products:
{product_info}

Recommend these products naturally, mention their prices, and be enthusiastic but not pushy! Keep it under 100 words."""
        
            messages = [
                {'role': 'system', 'content': enhanced_prompt},
                {'role': 'user', 'content': user_message}
            ]
            
            bot_reply = call_huggingface_api(messages, max_tokens=200, temperature=0.8)
            
            if not bot_reply or bot_reply == "MODEL_LOADING":
                bot_reply = f"I found {len(all_products)} great products for you! Check them out below. 🛍️"
            
            return jsonify({
                "reply": bot_reply,
                "products": all_products,
                "success": True
            }), 200
        
        # No products found
        system_prompt = """You are Emma, a helpful shopping assistant for MyStore. The customer is asking about products we don't have. Politely let them know and suggest browsing our categories or contacting support. Keep it friendly and under 50 words."""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        
        bot_reply = call_huggingface_api(messages)
        
        if not bot_reply:
            bot_reply = "I couldn't find exact matches for that. Try browsing our categories or contact support for help! 🛍️"
        
        return jsonify({
            "reply": bot_reply,
            "products": [],
            "success": True
        }), 200
        
    except Exception as e:
        print(f" Product Search Error: {str(e)}")
        return jsonify({
            "reply": "I'm having trouble searching products right now. Please browse our categories or contact support! 🛍️",
            "success": False
        }), 200

# ------------------- RUN APP -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)