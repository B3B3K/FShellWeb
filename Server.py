from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

BASE_DIR = os.getcwd()  # Set file manager base directory
CURRENT_DIR = BASE_DIR  # File manager starts in BASE_DIR
SHELL_DIR = BASE_DIR  # Shell starts in BASE_DIR too

# Serve the HTML page
@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Web Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: row;
            height: 100vh;
        }
        #shell, #file-manager {
            flex: 1;
            padding: 10px;
            box-sizing: border-box;
            overflow-y: auto;
        }
        #shell {
            border-right: 5px solid red;
            display: flex;
            flex-direction: column;
        }
        #terminal {
            background-color: #000;
            color: #0f0;
            padding: 5px;
            font-family: monospace;
            flex-grow: 1;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        #input-line {
            display: flex;
            align-items: center;
            background-color: #000;
            padding: 5px;
        }
        #input-line span {
            color: #0f0;
            margin-right: 5px;
            font-family: monospace;
        }
        input {
            flex: 1;
            font-family: monospace;
            border: none;
            outline: none;
            color: #0f0;
            background-color: #000;
        }
        #file-manager {
            background-color: #000;
            color: #fff;
        }
        #file-manager h3, #current-dir {
            color: #fff;
        }
        #file-manager h3 {
            margin: 0 0 10px;
        }
        #current-dir {
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .file {
            margin: 5px 0;
            cursor: pointer;
            color: cyan;
            text-decoration: underline;
        }
        .file:hover {
            text-decoration: none;
        }
        #upload-box {
            border: 2px dashed cyan;
            padding: 10px;
            margin-top: 10px;
            text-align: center;
        }
        #upload-box:hover {
            background-color: rgba(0, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div id="shell">
        <h3>Shell Emulator</h3>
        <div id="terminal"></div>
        <div id="input-line">
            <span>&gt;</span>
            <input id="command" type="text" placeholder="Type a command" autocomplete="off" />
        </div>
    </div>
    <div id="file-manager">
        <h3>File Manager</h3>
        <div id="current-dir">Current Directory: <span id="dir-path">/</span></div>
        <div id="files"></div>
        <div id="upload-box">
            Drag and drop files here to upload
        </div>
    </div>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script>
        const socket = io();
        const terminal = document.getElementById("terminal");
        const commandInput = document.getElementById("command");
        const filesDiv = document.getElementById("files");
        const dirPath = document.getElementById("dir-path");
        const uploadBox = document.getElementById("upload-box");
        let commandHistory = [];
        let historyIndex = -1;

        // Handle command submission
        commandInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                const command = commandInput.value.trim();
                if (command) {
                    terminal.innerHTML += `&gt; ${command}\n`;
                    terminal.scrollTop = terminal.scrollHeight;
                    if (command === "clear") {
                        terminal.innerHTML = ""; // Clear terminal
                    } else {
                        socket.emit("command", { command });
                    }
                    commandHistory.push(command);
                    historyIndex = commandHistory.length;
                }
                commandInput.value = "";
            } else if (event.key === "ArrowUp") {
                if (historyIndex > 0) {
                    historyIndex--;
                    commandInput.value = commandHistory[historyIndex];
                }
            } else if (event.key === "ArrowDown") {
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    commandInput.value = commandHistory[historyIndex];
                } else {
                    commandInput.value = "";
                }
            }
        });

        // Display shell output
        socket.on("output", data => {
            terminal.innerHTML += data.output;
            terminal.scrollTop = terminal.scrollHeight;
        });

        // List files and update current directory
        function listFiles() {
            fetch("/files")
                .then(response => response.json())
                .then(data => {
                    dirPath.textContent = data.current_dir; // Update current directory
                    filesDiv.innerHTML = '<div class="file" onclick="goUp()">.. (Go Up)</div>';
                    data.files.forEach(file => {
                        const fileElement = document.createElement("div");
                        fileElement.className = "file";
                        fileElement.textContent = file.is_dir ? `${file.name}/` : file.name;
                        fileElement.onclick = () => {
                            if (file.is_dir) {
                                changeDir(file.name);
                            } else {
                                window.location.href = `/download/${file.name}`;
                            }
                        };
                        filesDiv.appendChild(fileElement);
                    });
                });
        }

        // Change directory
        function changeDir(path) {
            fetch(`/change_dir?path=${encodeURIComponent(path)}`)
                .then(response => response.text())
                .then(() => listFiles());
        }

        // Go up a directory
        function goUp() {
            fetch("/change_dir?path=..")
                .then(response => response.text())
                .then(() => listFiles());
        }

        // Handle file drag and drop
        uploadBox.addEventListener("dragover", function (e) {
            e.preventDefault();
            e.stopPropagation();
        });

        uploadBox.addEventListener("drop", function (e) {
            e.preventDefault();
            e.stopPropagation();
            const files = e.dataTransfer.files;
            const formData = new FormData();
            for (const file of files) {
                formData.append("files[]", file);
            }
            fetch("/upload", { method: "POST", body: formData })
                .then(() => listFiles())
                .catch(err => alert("Error uploading files: " + err));
        });

        // Initialize file manager
        listFiles();
    </script>
</body>
</html>
    """

# Shell commands endpoint
@socketio.on("command")
def handle_command(data):
    global SHELL_DIR  # To track the current directory for shell commands
    try:
        command = data.get("command", "").strip()
        if command.startswith("cd "):
            # Handle the cd command within the shell
            path = command[3:].strip()
            if path == "..":
                SHELL_DIR = os.path.dirname(SHELL_DIR)
            else:
                new_dir = os.path.join(SHELL_DIR, path)
                if os.path.isdir(new_dir):
                    SHELL_DIR = new_dir
            output = f"Changed directory to {SHELL_DIR}\n"
        else:
            output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT, cwd=SHELL_DIR)
    except subprocess.CalledProcessError as e:
        output = e.output
    emit("output", {"output": output})

# File manager list files
@app.route("/files", methods=["GET"])
def list_files():
    global CURRENT_DIR
    try:
        files = [
            {"name": f, "is_dir": os.path.isdir(os.path.join(CURRENT_DIR, f))}
            for f in os.listdir(CURRENT_DIR)
        ]
        return jsonify({"current_dir": CURRENT_DIR, "files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# File manager change directory
@app.route("/change_dir", methods=["GET"])
def change_dir():
    global CURRENT_DIR
    path = request.args.get("path", "")
    try:
        if path == "..":
            CURRENT_DIR = os.path.dirname(CURRENT_DIR)
        else:
            new_dir = os.path.join(CURRENT_DIR, path)
            if os.path.isdir(new_dir):
                CURRENT_DIR = new_dir
        return "", 200
    except Exception as e:
        return str(e), 500

# File upload
@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        for file in request.files.getlist("files[]"):
            file.save(os.path.join(CURRENT_DIR, file.filename))
        return "", 200
    except Exception as e:
        return str(e), 500

# Download file
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(CURRENT_DIR, filename)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=80)
