import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xmpakpmhzioxwaiwijnn.supabase.co")
SUPABASE_PUBLISHABLE_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")

if not SUPABASE_SECRET_KEY:
    SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
