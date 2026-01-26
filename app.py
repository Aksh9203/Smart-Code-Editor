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
app.secret_key='secretkey_project'

# Access the API key
api_key = os.getenv('GOOGLE_API_KEY')
print(f"DEBUG: API Key : {api_key}")
if not api_key:
    print(f"Something is wrong. API key is not found")

# We create the client once.
client = genai.Client(api_key=api_key)

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///info.db"
db = SQLAlchemy(app)

# # Database Model

class FeedbackUser(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    feedback = db.Column(db.String(1000))
    username = db.Column(db.String(50),nullable=False)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    firstname = db.Column(db.String(50),nullable=False)
    lastname = db.Column(db.String(50),nullable=False)
    username = db.Column(db.String(50),unique=True,nullable=False)
    email = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(150),nullable=False)

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password, password)


@app.route('/login', methods=['POST'])
def login():
    #Collect info
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['username'] = username
        return jsonify({"success": True, "username": username})
    else:
        return jsonify({"success": False})
    
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify({"success": False, "message": "User exists"})
    else:
        new_user = User(username=username, firstname=firstname, lastname=lastname, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "message": "Account created"})


@app.route('/feedback', methods=['POST'])
def feedback():

    data = request.json
    user_msg = data.get('feedback')
    username = data.get('username') or "Anonymous"

    feedback = FeedbackUser.query.filter_by(username=username).first()

    new_feedback = FeedbackUser(feedback=user_msg, username=username)

    db.session.add(new_feedback)
    db.session.commit()

    return jsonify({"success":True})
  

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
    with app.app_context():
        db.create_all()
    app.run(debug=True)