"""
Minimal Azure OpenAI API test with detailed progress
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.config import AZURE_OPENAI_CONFIG
from openai import AzureOpenAI

print("=" * 60)
print("MINIMAL AZURE OPENAI TEST")
print("=" * 60)

# Step 1: Check config
print("\n1️⃣ Checking configuration...")
print(f"   Endpoint: {AZURE_OPENAI_CONFIG['endpoint']}")
print(f"   Deployment: {AZURE_OPENAI_CONFIG['deployment']}")
print(f"   API Version: {AZURE_OPENAI_CONFIG['api_version']}")

if AZURE_OPENAI_CONFIG['api_key']:
    key_preview = AZURE_OPENAI_CONFIG['api_key'][:10] + "..." + AZURE_OPENAI_CONFIG['api_key'][-4:]
    print(f"   API Key: {key_preview}")
else:
    print("   ❌ API Key: NOT SET")
    print("\n⚠️  Please add your API key to .env file:")
    print("   AZURE_OPENAI_API_KEY=your-key-here")
    sys.exit(1)

# Step 2: Initialize client
print("\n2️⃣ Initializing client...")
try:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_CONFIG['api_key'],
        api_version=AZURE_OPENAI_CONFIG['api_version'],
        azure_endpoint=AZURE_OPENAI_CONFIG['endpoint'],
        timeout=30.0  # 30 second timeout
    )
    print("   ✅ Client created")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Step 3: Make API call
print("\n3️⃣ Making API call (timeout: 30s)...")
print("   Sending test message...")

try:
    response = client.chat.completions.create(
        model=AZURE_OPENAI_CONFIG['deployment'],
        messages=[
            {"role": "user", "content": "Reply with just: Hello"}
        ],
        max_tokens=50,
        temperature=0
    )
    
    print("   ✅ Response received!")
    print(f"\n📨 AI Response: {response.choices[0].message.content}")
    print("\n✅ SUCCESS! API is working!")
    
except Exception as e:
    print(f"\n   ❌ API call failed")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error: {str(e)}")
    
    print("\n🔍 Troubleshooting:")
    print("   1. Check if API key is correct")
    print("   2. Verify endpoint URL")
    print("   3. Check deployment name")
    print("   4. Ensure you have internet connection")
    sys.exit(1)