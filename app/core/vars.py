from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DB_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
STRIPE_KEY = os.getenv("STRIPE_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")