"""
Configuration management for PORTNET Incident Resolver
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(os.getcwd())

# Data directories
DATA_DIR = PROJECT_ROOT
LOGS_DIR = DATA_DIR / "Application Logs"
DATABASE_DIR = DATA_DIR / "Database"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Data files
CASE_LOG_FILE = DATA_DIR / "Case Log.xlsx"
KNOWLEDGE_BASE_FILE = DATA_DIR / "Knowledge Base.docx"
ESCALATION_CONTACTS_FILE = DATA_DIR / "Product Team Escalation Contacts.pdf"
TEST_CASES_FILE = DATA_DIR / "Test Cases.pdf"
DB_SCHEMA_FILE = DATABASE_DIR / "db.sql"

# Application log files
LOG_FILES = {
    'api_event': LOGS_DIR / "api_event_service.log",
    'berth_application': LOGS_DIR / "berth_application_service.log",
    'container': LOGS_DIR / "container_service.log",
    'edi_advice': LOGS_DIR / "edi_adivce_service.log",  # Note: file has typo "adivce"
    'vessel_advice': LOGS_DIR / "vessel_advice_service.log",
    'vessel_registry': LOGS_DIR / "vessel_registry_service.log",
}

# Azure OpenAI configuration
AZURE_OPENAI_CONFIG = {
    'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
    'endpoint': os.getenv('AZURE_OPENAI_ENDPOINT', 'https://psacodesprint2025.azure-api.net'),
    'deployment': os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4.1-nano'),
    'api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
}

# Create outputs directory if it doesn't exist
OUTPUTS_DIR.mkdir(exist_ok=True)


def validate_files():
    """Validate that all required files exist"""
    missing_files = []
    
    # Check data files
    if not CASE_LOG_FILE.exists():
        missing_files.append(str(CASE_LOG_FILE))
    if not KNOWLEDGE_BASE_FILE.exists():
        missing_files.append(str(KNOWLEDGE_BASE_FILE))
    if not ESCALATION_CONTACTS_FILE.exists():
        missing_files.append(str(ESCALATION_CONTACTS_FILE))
    if not DB_SCHEMA_FILE.exists():
        missing_files.append(str(DB_SCHEMA_FILE))
    
    # Check log files
    for name, path in LOG_FILES.items():
        if not path.exists():
            missing_files.append(f"{name}: {path}")
    
    if missing_files:
        raise FileNotFoundError(
            f"Missing required files:\n" + "\n".join(f"  - {f}" for f in missing_files)
        )
    
    return True


def validate_azure_config():
    """Validate Azure OpenAI configuration"""
    if not AZURE_OPENAI_CONFIG['api_key']:
        raise ValueError("AZURE_OPENAI_API_KEY not set in .env file")
    if not AZURE_OPENAI_CONFIG['endpoint']:
        raise ValueError("AZURE_OPENAI_ENDPOINT not set in .env file")
    
    return True