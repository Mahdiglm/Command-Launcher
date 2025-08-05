<div align="center">

# Command Launcher

> A modern Python GUI application for efficient command-line management and execution

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

<div align="center">

## Features

### Core Functionality
- **Command Management**: Add, edit, delete, and duplicate commands
- **Batch Execution**: Run selected commands or execute all at once
- **Cross-Platform**: Native support for Windows, macOS, and Linux
- **Persistent Storage**: Automatic JSON-based command persistence

### Advanced Features
- **Background Execution**: Silent command execution with process tracking
- **Process Control**: One-click termination of all background processes
- **Real-time Monitoring**: Live status updates and process count display
- **Auto Cleanup**: Automatic cleanup of finished background processes

</div>

---

<div align="center">

## Quick Start

### Prerequisites
```bash
pip install pyinstaller
```

### Installation
1. Clone the repository
2. Run the application:
   ```bash
   python main.py
   ```

</div>

---

<div align="center">

## Usage Guide

### Command Execution Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Normal** | Commands run in visible terminal windows | Interactive debugging, monitoring |
| **Background** | Silent execution with process tracking | Long-running tasks, services |

### Process Management
- **Start**: Check "Run in Background" for silent execution
- **Monitor**: Status bar shows active background processes
- **Terminate**: Use "Terminate All" to stop background processes
- **Auto-cleanup**: Finished processes are automatically removed

</div>

---

<div align="center">

## Building Executable

```bash
pyinstaller --onefile --windowed main.py
```

</div>

---

<div align="center">

## Technical Architecture

### Background Process Implementation
```python
# Windows
subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

# Unix-like systems  
subprocess.Popen(command, shell=True)
```

### Key Components
- **Process Tracking**: `running_processes` list with automatic cleanup
- **Cross-Platform Support**: Platform-specific terminal emulation
- **Memory Management**: Periodic cleanup prevents memory leaks

</div>

---

<div align="center">

## Project Structure

```
command_runner/
├── main.py              # Main application
├── README.md            # Documentation
├── LICENSE              # MIT License
├── CHANGELOG.md         # Version history
├── .gitignore           # Git ignore rules
└── main.spec            # PyInstaller configuration
```

</div>

---

<div align="center">

## Example Commands

<details>
<summary>Development Commands</summary>

```json
[
  {
    "name": "Start Dev Server",
    "command": "python -m http.server 8000"
  },
  {
    "name": "Run Tests",
    "command": "python -m pytest tests/"
  }
]
```
</details>

<details>
<summary>Database Commands</summary>

```json
[
  {
    "name": "Database Backup",
    "command": "mysqldump -u root -p mydb > backup.sql"
  },
  {
    "name": "Start Redis",
    "command": "redis-server"
  }
]
```
</details>

</div>

---

<div align="center">

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

</div>

---

<div align="center">

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

For a complete list of changes, see the [CHANGELOG](CHANGELOG.md).

</div>

---

<div align="center">

**Made with Python and Tkinter**

</div> 