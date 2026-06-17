import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the .env file in the root directory
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'

# Load the environment variables from the .env file safely
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Odoo 17 Configuration
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

# LLM Flag Configuration
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "local").lower()

# Local Ollama Configuration
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
LOCAL_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen2.5:1.5b")

# Cloud Providers Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")