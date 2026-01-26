let isLoggedIn = false; // By default, user is guest
let currentUser = "";

// Initialize CodeMirror
var editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
    mode: "python", theme: "dracula", lineNumbers: true
});

const fileInput = document.getElementById("file-input");
const messageDisplay = document.getElementById("message");

fileInput.addEventListener("change", handleFileSelection);

function handleFileSelection(event) {
    const file = event.target.files[0];
    messageDisplay.textContent = "";

    if (!file) return;

    const allowedFile = ['.py', '.java', '.cpp', '.js'];
    let detectedLang = null;
    let detectedMode = null;

    if (file.name.endsWith('.py')) {
        detectedLang = 'python';
        detectedMode = 'python';
    } else if (file.name.endsWith('.js')) {
        detectedLang = 'javascript';
        detectedMode = 'javascript';
    } else if (file.name.endsWith('.java')) {
        detectedLang = 'java';
        detectedMode = 'text/x-java';
    } else if (file.name.endsWith('.cpp')) {
        detectedLang = 'cpp';
        detectedMode = 'text/x-c++src';
    } else {
        showMessage("Unsupported file type.", "error");
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        document.getElementById("language-select").value = detectedLang;
        
        // UPDATE EDITOR MODE
        editor.setOption("mode", detectedMode);
        
        // LOAD CONTENT INTO EDITOR
        editor.setValue(reader.result);
        showMessage(`Loaded ${file.name} successfully!`, "success");
    };
    reader.onerror = () => showMessage("Error reading file.", "error");
    reader.readAsText(file);
}

function showMessage(message, type) {
    messageDisplay.textContent = message;
    messageDisplay.style.color = type === "error" ? "#ff5555" : "#50fa7b";
}

// Programming Language Selection
function changeLanguage() {
    var lang = document.getElementById("language-select").value;
    var mode = "python";
    var defaultCode = "";

    if (lang === "python") {
        mode = "python"; defaultCode = "print('Hello Python!')";
    } else if (lang === "javascript") {
        mode = "javascript"; defaultCode = "console.log('Hello JavaScript!');";
    } else if (lang === "java") {
        mode = "text/x-java"; defaultCode = "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello Java!\");\n    }\n}";
    } else if (lang === "cpp") {
        mode = "text/x-c++src"; defaultCode = "#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << \"Hello C++!\" << endl;\n    return 0;\n}";
    }
    editor.setOption("mode", mode);
    editor.setValue(defaultCode);
}

async function runCode() {
    const outputBox = document.getElementById('output');
    const lang = document.getElementById("language-select").value;
    outputBox.innerText = "Running...";
    
    try {
        const response = await fetch('/run', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ code: editor.getValue(), language: lang })
        });
        const data = await response.json();
        if (data.run) {
            outputBox.innerText = data.run.output;
        } else {
            outputBox.innerText = "Error running code.";
        }
    } catch (err) { outputBox.innerText = "Error: " + err; }
}

async function submitSignup(){


    const username = document.getElementById('reg-user').value;
    const firstname = document.getElementById('reg-fname').value;
    const lastname = document.getElementById('reg-lname').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-pass').value;

    
    const response = await fetch('/register',{
        method: 'POST',
        headers: {
            'Content-Type':'application/json',
        },
        body: JSON.stringify({
            username: username,
            firstname: firstname,
            lastname: lastname,
            email: email,
            password: password,
        })
    })

    const data = await response.json();

    if(data.success){
        document.getElementById('signup-section').style.display = 'none';
        document.getElementById('login-section').style.display = 'block';
    }
    else{
        alert('An error occurred during registration.')
    }
}

async function submitLogin(){

    const username = document.getElementById('login-user').value;
    const email = document.getElementById('login-user').value;
    const password = document.getElementById('login-pass').value;

    const response = await fetch('/login',{
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password: password
        })
    })

    const data = await response.json();

    if(data.success){
        isLoggedIn = true;

        document.getElementById('user-display').textContent = username; 
        document.getElementById('user-display').style.color = "#50fa7b";

        closeModal();
    }
    else{
        alert('An error occurred during login.')
    }
}

async function triggerAskAI() {
    const aiBox = document.getElementById('ai-response');
    const question = document.getElementById('question').value;
    const lang = document.getElementById("language-select").value;

    if(isLoggedIn === false){
        document.getElementById('auth-modal').style.display = 'block';
    } else {
        aiBox.innerHTML = "<i>Thinking...</i>";
        const response = await fetch('/ask_ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                code: editor.getValue(), 
                question: question, 
                language: lang 
            })
        });    
        
        const data = await response.json();
        
        let formattedResponse = data.answer;
        if (data.solution) {
            formattedResponse += "\n\n**Suggested Solution:**\n```" + lang + "\n" + data.solution + "\n```";
        }
        aiBox.innerHTML = marked.parse(formattedResponse);
    }
}

async function triggerFeedback() {
 
    if(isLoggedIn === false){
        document.getElementById('auth-modal').style.display = 'block';
    }
    else{
       document.getElementById('feedback-text').value = "";
       document.getElementById('feedback-modal').style.display = 'block';
    }
}

async function submitFeedback() {
    
    const feedback = document.getElementById('feedback-text').value;
    const username = document.getElementById('user-display').textContent;

    const response = await fetch('/feedback',{
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
        },
        body: JSON.stringify({
            feedback: feedback,
            username: username
        })            
    })

    const data = await response.json();

    if(data.success){
        alert("Feedback sent!");
        closeModal();
    }
    else{
        alert('Something is wrong!!!')
    }
}

function showSignup(){
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('signup-section').style.display = 'block';
}

function showLogin(){
    document.getElementById('signup-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
}

function closeModal() {
    document.getElementById('auth-modal').style.display = 'none';
    document.getElementById('feedback-modal').style.display = 'none';
}