# 🐍 Smart Code Editor (AI-Powered IDE)

A full-stack web-based code editor that integrates **Google Gemini AI** to act as a real-time intelligent programming mentor. 

Unlike standard compilers, this tool allows users to not only run code safely but also ask natural language questions about their logic, errors, or syntax directly within the interface.

## 🚀 Features (Version 1.0)

* **Interactive Code Editor:** Syntax highlighting, line numbers, and auto-indentation (powered by CodeMirror).
* **Safe Code Execution:** Compiles and runs Python code securely using the Piston API.
* **AI Mentor Integration:** innovative "Ask AI" feature that sends code context + user questions to Google Gemini (v2.5 Flash) for instant explanations.
* **Modern UI:** Clean, dark-mode interface designed for developer focus.

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript, CodeMirror (UI Library)
* **Backend:** Python, Flask
* **AI Engine:** Google GenAI SDK (Gemini 2.5 Flash)
* **Compiler Engine:** Piston API (REST via `requests`)
* **Tools:** Dotenv for environment management

## 📂 Project Structure

```text
flask_code_editor/
├── .env                  # API Keys (Not tracked by Git)
├── requirements.txt      # Python dependencies
├── app.py                # Main Flask backend application
└── templates/
    └── index.html        # Frontend UI
```
## 🔮 Future Roadmap (Version 2.0)
* **Multi-Language Support:** Expanding compiler support to Java and C++.
* **User Accounts:** Ability to save code snippets to a database.
