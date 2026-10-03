import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("[ERROR] DATABASE_URL is not set in .env")
    sys.exit(1)

# Normalize postgres:// to postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

print(f"Testing database connection...")
# Mask password for display
try:
    if "@" in database_url:
        protocol_and_creds, host_part = database_url.split("@", 1)
        protocol, creds = protocol_and_creds.split("://", 1)
        user = creds.split(":", 1)[0]
        masked_url = f"{protocol}://{user}:***@{host_part}"
    else:
        masked_url = database_url
    print(f"Connecting to: {masked_url}")
except Exception:
    pass

try:
    engine = create_engine(database_url, connect_args={"connect_timeout": 10})
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        if result == 1:
            print("[SUCCESS] Connected to Supabase PostgreSQL successfully!")
            
            # Check existing tables in public schema
            tables_res = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
            )).fetchall()
            table_names = [r[0] for r in tables_res]
            print(f"Tables in public schema ({len(table_names)}):")
            for tbl in table_names:
                cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{tbl}"')).scalar()
                print(f"  - {tbl}: {cnt} rows")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    sys.exit(1)
