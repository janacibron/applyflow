import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xmpakpmhzioxwaiwijnn.supabase.co")
SUPABASE_PUBLISHABLE_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_HIISbZ96Wwn439slDaWXTg_JhkeT0R4")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")

# Try to load from local config if secret key is empty
if not SUPABASE_SECRET_KEY:
    try:
        import sys
        sys.path.insert(0, 'C:/va-pipeline')
        from supabase_config_local import SUPABASE_SECRET_KEY as LOCAL_KEY
        SUPABASE_SECRET_KEY = LOCAL_KEY
    except:
        pass
