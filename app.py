import os
import requests
from dotenv import load_dotenv
from flask import Flask,jsonify,request,render_template
from google import genai

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Access the API key
api_key = os.getenv('GOOGLE_API_KEY')
print(f"DEBUG: API Key : {api_key}")
if not api_key:
    print(f"Something is wrong. API key is not found")

# Only run this block for Gemini Developer API
# We create the client once.
client = genai.Client(api_key='AIzaSyCRFPMZ2MOOTKTcEo9_qVqkjYaMLUrKoLk')

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/run', methods=['POST'])
def run():
    data = request.json
    code = data.get('code')

    reponse = requests.post("https://emkc.org/api/v2/piston/execute", json={
        "language": "python",
        "version": "3.10.0",
        "files": [{"content": code}] 
    })

    return jsonify(reponse.json())


@app.route('/ask_ai', methods=['POST'])
def ask_ai():

    data = request.json
    code = data.get('code')
    question = data.get('question')

    prompt = f"""
    You are a helpful Smart Tutor masters of many programming languages like Python, JavaScript, C++, and Java. 
    Based on you knowledge in these languages help the user understand and resolve any errot the code has.
    The User wrote this code:
    {code}
    
    The User asked: "{question}"
    Please answer clearly and concisely. If the code has an error, explain how to fix it.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return jsonify({"answer":response.text})


if __name__ == '__main__':
    # Run the application
    app.run(debug=True)