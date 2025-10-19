# 🛠️ Setup Guide

Quick installation guide for PORTNET Incident Resolver.

---

## Prerequisites

- Python 3.10+
- Azure OpenAI API access

---

## Installation (5 Minutes)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd portnet-incident-resolver

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API

Create `.env` file:

```properties
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.azure-api.net
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-nano
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

Get credentials from Azure Portal → Your OpenAI Resource → Keys and Endpoint

### 3. Verify Setup

```bash
# Test parsers
python test_parsers.py
# Should show: 6/6 tests passed

# Test API
python test_api_minimal.py
# Should show: SUCCESS! API is working!

# Run application
streamlit run app.py
# Opens browser to http://localhost:8501
```

---

## Troubleshooting

**"Module not found"**
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

**"API key not set"**
- Check `.env` file exists
- Verify `AZURE_OPENAI_API_KEY=...` is set
- Restart Streamlit

**"File not found"**
- Ensure all data files are in project root
- Check file names match exactly (case-sensitive)

---

## That's It!

System should now show ✅ green status in sidebar.

Click "Load Test Case 3" and hit Analyze to try it out.

For usage instructions, see the UI - it's self-explanatory.