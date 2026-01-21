import os
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, session
from google import genai
from pydantic import BaseModel, Field
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Load environment variables
load_dotenv()

app = Flask(__name__)

# Access the API key
api_key = os.getenv('GOOGLE_API_KEY')
print(f"DEBUG: API Key : {api_key}")
if not api_key:
    print(f"Something is wrong. API key is not found")

# We create the client once.
client = genai.Client(api_key=api_key)



# # Configure SQLAlchemy
# app.config["SQLALCHEMY_DATABSE_URI"] = "sqlite:///info.db"
# db = SQLAlchemy(app)

# # Database Model

# class User(db.model):
#     id = db.Column(db.Integer,primary=True)
#     firstname = db.Column(db.String(50))
#     lastname = db.Column(db.String(50))
#     username = db.Column(db.String(50),unique=True,nullable=False)
#     password = db.Column(db.String(50),nullable=False)

#     def set_password(self,password):
#         self.set_password = generate_password_hash(password)

#     def check_password(self,password):
#         return check_password_hash(self.set_password, password)




# Structure for the AI Response 
class AIResponse(BaseModel):
    """Structure for the AI's coding assistance response."""
    solution_code: str = Field(
        description="The corrected or requested Python/Java/C++/JS code snippet. It should be complete and runnable."
    )
    explanation: str = Field(
        description="A clear, concise explanation of what changed, why the error occurred, or how the logic works."
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    data = request.json
    code = data.get('code')
    language = data.get('language', 'python')

    version_map = {
        "python": "3.10.0",
        "javascript": "18.15.0",
        "java": "15.0.2",
        "cpp": "10.2.0"
    }

    try:
        response = requests.post("https://emkc.org/api/v2/piston/execute", json={
            "language": language,
            "version": version_map.get(language),
            "files": [{"content": code}] 
        })
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"run": {"output": f"Error: {str(e)}"}})

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    data = request.json
    language = data.get('language')
    code = data.get('code')
    question = data.get('question')

    # Prompt
    prompt = f"""
    You are an expert Coding Tutor.
    The user has written the following code in {language} language, Suggest soutions for {language} language only:
    ---
    {code}
    ---
    
    The User asked: "{question}"
    
    Provide the corrected code (or the code they asked for) and a clear explanation.
    """

    try:
        # Call Gemini with Strict JSON Schema
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": AIResponse,
            }
        )

        # Parse the JSON response securely using Pydantic
        # This guarantees you get exactly the fields you asked for.
        ai_data = response.parsed # The SDK automatically parses it into the AIResponse object
        
        # Return structured data to Frontend
        # We send back 'answer' (explanation) and 'solution' (code) separately
        return jsonify({
            "answer": ai_data.explanation,
            "solution": ai_data.solution_code
        })

    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify({"answer": f"Error generating response: {str(e)}", "solution": ""})

if __name__ == '__main__':
    app.run(debug=True)