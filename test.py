import os
from dotenv import load_dotenv
from google import genai

# 1. Try to load the .env file
print("--- STARTING TEST ---")
load_dotenv()

# 2. Check if Python can read the file
api_key = os.getenv("GOOGLE_API_KEY")

if api_key is None:
    print("❌ ERROR: Could not find GOOGLE_API_KEY in .env file.")
    print("   -> Make sure the file is named exactly '.env'")
    print("   -> Make sure it is in the same folder as this script.")
    exit()

print(f"✅ Found API Key! (Length: {len(api_key)} characters)")
print(f"   Key starts with: {api_key[:6]}...")

# 3. Test the actual connection to Google
print("\n--- CONNECTING TO GOOGLE ---")
try:
    client = genai.Client(api_key=api_key)
    
    # Try a simple "Hello" request
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents="Say 'Hello, API works!' if you can hear me."
    )
    
    print("✅ SUCCESS! Google replied:")
    print(f"   \"{response.text}\"")

except Exception as e:
    print("\n❌ CONNECTION FAILED")
    print("   The key was found, but Google rejected it.")
    print(f"   Error details: {e}")