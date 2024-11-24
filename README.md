# Python Web Server with Shell Emulator and File Manager

This project is a Flask-based web application that provides a simple interface for running shell commands and managing files on a server. The application has two main components: a shell emulator that executes commands on the server and displays their output in real time, and a file manager that allows browsing, uploading, and downloading files. The interface is powered by Flask and SocketIO, providing a dynamic and responsive user experience.

## Features
- **Shell Emulator**: Allows users to execute shell commands via a web interface. The output of each command is displayed in real time.
- **File Manager**: Browse files on the server, navigate directories, and upload/download files.
- **Drag-and-Drop File Upload**: Easily upload files by dragging them into the designated area on the web page.
- **Directory Navigation**: Change directories, go up a directory, and view file and folder details.

## Requirements
- Python 3.x
- Flask
- Flask-SocketIO
- Web browser (for interacting with the UI)

You can install the required dependencies using the following command:
```bash
pip install flask flask-socketio
```

## Structure

```
/project-directory
│
├── server.py             # Main Python script with the Flask server and logic

```

## How It Works

### Shell Emulator
The shell emulator allows users to type and execute shell commands directly from the browser. The output of the command is captured and displayed in real time. Commands like `cd` (change directory) are handled by the server, and other commands are executed via Python’s `subprocess` module. This is facilitated using **SocketIO** for real-time communication between the client and server.

### File Manager
The file manager enables browsing the file system, uploading files, and downloading files. It provides the following features:
1. **Directory Navigation**: Users can move between directories and view their contents.
2. **File Upload**: Users can drag and drop files into the upload area for easy file uploads.
3. **File Download**: Users can click on a file to download it.

### Key Routes
1. **`/`**: Serves the main HTML interface.
2. **`/files`**: Lists all files and directories in the current directory.
3. **`/change_dir`**: Changes the current directory.
4. **`/upload`**: Handles file uploads.
5. **`/download/<filename>`**: Downloads the specified file.

### How to Run

1. Clone or download the repository.
2. Navigate to the project directory.
3. Run the application:
   ```bash
   python app.py
   ```
4. Open a web browser and go to `http://localhost:5000`.

### Usage

- **Shell Emulator**: Type shell commands into the command input field and press Enter. The output will be displayed in the terminal area.
- **File Manager**: 
  - Navigate directories by clicking on folder names.
  - Download files by clicking on them.
  - Upload files by dragging them into the drag-and-drop area.

### Example
When the user navigates to the root directory, the file manager will show a list of files and folders, along with an option to go up a directory. The shell emulator can be used to run system commands like `ls` to list files or `clear` to clear the terminal output.

### Sample Output

#### Shell Command Execution
```
> command
```

#### File Uploads
```
Drag and Drop method
```

## License

This project is open source and available under the [MIT License](LICENSE).

