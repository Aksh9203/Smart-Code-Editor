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
        // UPDATE DROPDOWN
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

// Standard Language Change (Resets to Hello World)
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

async function askAI() {
    const aiBox = document.getElementById('ai-response');
    const question = document.getElementById('question').value;
    const lang = document.getElementById("language-select").value;
    aiBox.innerHTML = "<i>Thinking...</i>";
    
    const response = await fetch('/ask_ai', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ code: editor.getValue(), question: question, language: lang })
    });
    const data = await response.json();
    
    let formattedResponse = data.answer;
    if (data.solution) {
        formattedResponse += "\n\n**Suggested Solution:**\n```" + lang + "\n" + data.solution + "\n```";
    }
    aiBox.innerHTML = marked.parse(formattedResponse);
}