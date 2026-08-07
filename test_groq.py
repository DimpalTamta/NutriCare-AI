import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
print("API Key:", api_key[:10] + "...")  # print first 10 chars to verify
if api_key:
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print("✅ Success:", response.choices[0].message.content)
    except Exception as e:
        print("❌ Error:", e)
else:
    print("❌ No API key found.")