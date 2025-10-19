# 🛠️ Setup Guide

Complete installation and configuration guide for PORTNET Incident Resolver.

---

## 📋 **Prerequisites**

### **Required**
- Python 3.10 or higher
- pip (Python package manager)
- Azure OpenAI API access

### **Recommended**
- Virtual environment tool (venv)
- Git (for cloning repository)
- Modern web browser (Chrome, Firefox, Edge)

---

## 🚀 **Installation Steps**

### **Step 1: Clone Repository**

```bash
git clone <repository-url>
cd portnet-incident-resolver
```

---

### **Step 2: Create Virtual Environment**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Installing collected packages: streamlit, openai, pandas, python-docx...
Successfully installed ...
```

**Verify installation:**
```bash
pip list
```

Should show all packages from requirements.txt

---

### **Step 4: Configure API Credentials**

#### **4.1 Create `.env` file**

Create a file named `.env` in the project root:

```bash
# Windows
type nul > .env

# Mac/Linux
touch .env
```

#### **4.2 Add Azure OpenAI credentials**

Open `.env` and add:

```properties
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.azure-api.net
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-nano
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

#### **4.3 Get your API credentials**

**From Azure Portal:**
1. Go to https://portal.azure.com
2. Navigate to your Azure OpenAI resource
3. Click "Keys and Endpoint"
4. Copy:
   - **Key 1** → `AZURE_OPENAI_API_KEY`
   - **Endpoint** → `AZURE_OPENAI_ENDPOINT`

**From Azure API Management:**
1. Go to your APIM portal
2. Find your profile/keys section
3. Copy your subscription key

---

### **Step 5: Verify Data Files**

Ensure all required files are present:

```
portnet-incident-resolver/
├── Case Log.xlsx              ✓ 323 historical cases
├── Knowledge Base.docx        ✓ Procedures & docs
├── Product Team Escalation Contacts.pdf  ✓ Contact info
├── Test Cases.pdf             ✓ Sample incidents
├── Application Logs/          ✓ 6 log files
│   ├── api_event_service.log
│   ├── berth_application_service.log
│   ├── container_service.log
│   ├── edi_adivce_service.log  (note: typo in filename)
│   ├── vessel_advice_service.log
│   └── vessel_registry_service.log
└── Database/
    └── db.sql                 ✓ Schema file
```

---

## ✅ **Testing Installation**

### **Test 1: Validate Setup**

```bash
python test_parsers.py
```

**Expected output:**
```
🚀🚀🚀 PORTNET INCIDENT RESOLVER - PARSER TESTS 🚀🚀🚀

============================================================
  TEST 1: File Existence Check
============================================================
✅ All required files found!

...

Results: 6/6 tests passed
🎉 All tests passed! Ready for Phase 2!
```

---

### **Test 2: Test Azure OpenAI Connection**

```bash
python test_api_minimal.py
```

**Expected output:**
```
============================================================
MINIMAL AZURE OPENAI TEST
============================================================

1️⃣ Checking configuration...
   ✅ API Key: b754615241...c135

2️⃣ Initializing client...
   ✅ Client created

3️⃣ Making API call...
   ✅ Response received!

📨 AI Response: Hello
✅ SUCCESS! API is working!
```

---

### **Test 3: Test Complete Flow**

```bash
python test_phase2.py
```

**Expected output:**
```
============================================================
TEST 1: Incident Parser
============================================================
✅ Incident parsed successfully!

...

Results: 3/3 passed
🎉 Phase 2 complete! Ready for Phase 3!
```

---

### **Test 4: Test Real Incident**

```bash
python test_real_incident.py
```

**Expected output:**
```
======================================================================
  TEST CASE 2: Vessel Advice Creation Error
======================================================================

✅ AI Analysis Results:
📍 Root Cause: ...
💥 Impact: ...

🎉 Test Case 2 completed successfully!
```

---

## 🌐 **Running the Application**

### **Start Streamlit**

```bash
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.X.X:8501
```

**Your browser will automatically open to `http://localhost:8501`**

---

## 🎯 **First Use**

### **1. Verify System Status**

Look at the sidebar:
- Should show: ✅ System validated successfully

If you see ❌ errors, check:
- .env file has correct API credentials
- All data files are present
- Virtual environment is activated

### **2. Try Sample Test Case**

1. Click "Load Test Case 3: EDI Stuck" in sidebar
2. Click "🔍 Analyze Incident"
3. Wait for analysis (30-60 seconds)
4. View results in tabs

### **3. Download Outputs**

- Go to "Escalation Summaries" tab
- Click "📥 Download L3 Summary"
- Click "📥 Download Management Summary"

---

## 🐛 **Troubleshooting**

### **Problem: "Module not found" errors**

**Solution:**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

---

### **Problem: "API key not set" error**

**Solution:**
1. Check `.env` file exists in project root
2. Verify it contains `AZURE_OPENAI_API_KEY=...`
3. Make sure no spaces around `=`
4. Restart Streamlit application

---

### **Problem: "File not found" errors**

**Solution:**
1. Check all data files are in correct locations
2. Verify file names match exactly (including .log extension)
3. Run: `python test_parsers.py` to see which files are missing

---

### **Problem: Streamlit won't start**

**Solution:**
```bash
# Check if port 8501 is already in use
netstat -ano | findstr :8501  # Windows
lsof -i :8501  # Mac/Linux

# Kill the process or use different port
streamlit run app.py --server.port 8502
```

---

### **Problem: API calls timing out**

**Solution:**
1. Check internet connection
2. Verify endpoint URL is correct
3. Test API separately:
   ```bash
   python test_api_minimal.py
   ```
4. Check Azure OpenAI service status

---

### **Problem: Slow analysis**

**Possible causes:**
- First run downloads AI model (normal, 30-60 sec)
- Large log files (check Application Logs/ folder)
- Network latency to Azure

**Normal timing:**
- Parsing: <1 second
- Context gathering: 2-5 seconds
- AI analysis: 20-40 seconds
- Total: 30-60 seconds

---

## 🔄 **Updating the Application**

### **Pull Latest Changes**

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### **Reset Environment**

```bash
# Deactivate current environment
deactivate

# Delete old environment
rm -rf venv  # Mac/Linux
rmdir /s venv  # Windows

# Create new environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📦 **Deployment**

### **Local Network Access**

Others on your network can access via:
```
http://YOUR_IP_ADDRESS:8501
```

Find your IP:
```bash
ipconfig  # Windows
ifconfig  # Mac/Linux
```

### **Cloud Deployment Options**

**Streamlit Community Cloud:**
```bash
# Push to GitHub
git push origin main

# Deploy at streamlit.io
# Connect GitHub repository
# Click "Deploy"
```

**Docker:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

---

## 🔐 **Security Notes**

### **⚠️ Never commit `.env` to Git**

Add to `.gitignore`:
```
.env
*.env
```

### **⚠️ Rotate API keys regularly**

Change API keys every 90 days:
1. Generate new key in Azure Portal
2. Update `.env` file
3. Restart application

### **⚠️ Restrict access in production**

- Use firewall rules
- Enable authentication
- Use HTTPS only

---

## 📞 **Getting Help**

### **Check logs:**
```bash
# Streamlit logs in terminal
# Look for errors in red

# Test individual components
python test_parsers.py
python test_phase2.py
```

### **Common issues:**
1. API credentials → Check `.env`
2. File paths → Check data files exist
3. Dependencies → Reinstall requirements
4. Port conflicts → Use different port

---

## ✅ **Setup Complete!**

If all tests pass, you're ready to use the system!

**Next steps:**
1. Read [USER_GUIDE.md](docs/USER_GUIDE.md) for usage instructions
2. Read [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) for architecture details
3. Try analyzing real incidents!

---

## 🎉 **Success Checklist**

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows all packages)
- [ ] `.env` file configured with API keys
- [ ] All data files present and validated
- [ ] `test_parsers.py` passes (6/6)
- [ ] `test_api_minimal.py` passes (API works)
- [ ] `test_phase2.py` passes (3/3)
- [ ] Streamlit runs (`streamlit run app.py`)
- [ ] System status shows ✅ green check
- [ ] Sample test case analyzes successfully

**If all checked ✅ - You're all set!** 🚀