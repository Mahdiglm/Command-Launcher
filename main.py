import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

class CommandLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Launcher")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Data file path (same directory as executable)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.data_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.data_dir = Path(__file__).parent
        
        self.data_file = self.data_dir / "commands.json"
        
        # Commands storage
        self.commands = []
        
        # Track running processes for termination
        self.running_processes = []
        
        # Background execution setting
        self.run_in_background = tk.BooleanVar(value=False)
        
        # Load saved commands
        self.load_commands()
        
        # Create GUI
        self.create_widgets()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start periodic cleanup of finished processes
        self.cleanup_finished_processes()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Command Launcher", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Commands list frame
        list_frame = ttk.LabelFrame(main_frame, text="Saved Commands", padding="5")
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for commands
        columns = ('Name', 'Command')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', selectmode='extended')
        
        # Configure columns
        self.tree.heading('#0', text='#')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Command', text='Command')
        
        self.tree.column('#0', width=50, minwidth=50)
        self.tree.column('Name', width=200, minwidth=150)
        self.tree.column('Command', width=400, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid the treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Command management buttons frame
        mgmt_frame = ttk.LabelFrame(main_frame, text="Manage Commands", padding="5")
        mgmt_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Management buttons
        ttk.Button(mgmt_frame, text="Add Command", command=self.add_command, 
                  width=15).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(mgmt_frame, text="Edit Command", command=self.edit_command, 
                  width=15).grid(row=0, column=1, padx=5)
        ttk.Button(mgmt_frame, text="Delete Command", command=self.delete_command, 
                  width=15).grid(row=0, column=2, padx=5)
        ttk.Button(mgmt_frame, text="Duplicate Command", command=self.duplicate_command, 
                  width=15).grid(row=0, column=3, padx=(5, 0))
        
        # Execution buttons frame
        exec_frame = ttk.LabelFrame(main_frame, text="Execute Commands", padding="5")
        exec_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Execution buttons
        ttk.Button(exec_frame, text="Run Selected", command=self.run_selected, 
                  width=15, style='Accent.TButton').grid(row=0, column=0, padx=(0, 5))
        ttk.Button(exec_frame, text="Run All", command=self.run_all, 
                  width=15, style='Accent.TButton').grid(row=0, column=1, padx=5)
        ttk.Button(exec_frame, text="Terminate All", command=self.terminate_all, 
                  width=15, style='Danger.TButton').grid(row=0, column=2, padx=5)
        
        # Background execution checkbox
        background_frame = ttk.Frame(exec_frame)
        background_frame.grid(row=0, column=3, padx=(20, 0), sticky=(tk.W, tk.E))
        exec_frame.columnconfigure(3, weight=1)
        
        ttk.Checkbutton(background_frame, text="Run in Background", 
                       variable=self.run_in_background).grid(row=0, column=0, sticky=tk.W)
        
        # Help text for background mode
        help_text = "When checked, commands run silently in background (can be terminated with 'Terminate All')"
        ttk.Label(background_frame, text=help_text, font=('Arial', 8), 
                 foreground='gray').grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # Status frame
        status_frame = ttk.Frame(exec_frame)
        status_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Populate the tree
        self.refresh_tree()
    
    def load_commands(self):
        """Load commands from JSON file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.commands = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load commands: {str(e)}")
            self.commands = []
    
    def save_commands(self):
        """Save commands to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.commands, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save commands: {str(e)}")
    
    def refresh_tree(self):
        """Refresh the treeview with current commands"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add commands
        for i, cmd in enumerate(self.commands):
            self.tree.insert('', 'end', iid=str(i), text=str(i+1), 
                           values=(cmd['name'], cmd['command']))
    
    def add_command(self):
        """Add a new command"""
        dialog = CommandDialog(self.root, "Add Command")
        if dialog.result:
            name, command = dialog.result
            self.commands.append({'name': name, 'command': command})
            self.save_commands()
            self.refresh_tree()
            self.update_status(f"Added command: {name}")
    
    def edit_command(self):
        """Edit selected command"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a command to edit.")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one command to edit.")
            return
        
        idx = int(selection[0])
        cmd = self.commands[idx]
        
        dialog = CommandDialog(self.root, "Edit Command", cmd['name'], cmd['command'])
        if dialog.result:
            name, command = dialog.result
            self.commands[idx] = {'name': name, 'command': command}
            self.save_commands()
            self.refresh_tree()
            self.update_status(f"Updated command: {name}")
    
    def delete_command(self):
        """Delete selected commands"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select command(s) to delete.")
            return
        
        if len(selection) == 1:
            message = f"Delete command '{self.commands[int(selection[0])]['name']}'?"
        else:
            message = f"Delete {len(selection)} selected commands?"
        
        if messagebox.askyesno("Confirm Delete", message):
            # Sort indices in reverse order to delete from end
            indices = sorted([int(idx) for idx in selection], reverse=True)
            for idx in indices:
                del self.commands[idx]
            
            self.save_commands()
            self.refresh_tree()
            self.update_status(f"Deleted {len(selection)} command(s)")
    
    def duplicate_command(self):
        """Duplicate selected command"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a command to duplicate.")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one command to duplicate.")
            return
        
        idx = int(selection[0])
        cmd = self.commands[idx].copy()
        cmd['name'] = f"{cmd['name']} (Copy)"
        
        self.commands.append(cmd)
        self.save_commands()
        self.refresh_tree()
        self.update_status(f"Duplicated command: {cmd['name']}")
    
    def run_selected(self):
        """Run selected commands"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select command(s) to run.")
            return
        
        commands_to_run = [self.commands[int(idx)] for idx in selection]
        self.execute_commands(commands_to_run)
    
    def run_all(self):
        """Run all commands"""
        if not self.commands:
            messagebox.showwarning("Warning", "No commands to run.")
            return
        
        self.execute_commands(self.commands)
    
    def execute_commands(self, commands_to_run):
        """Execute commands in separate threads"""
        if not commands_to_run:
            return
        
        self.update_status(f"Running {len(commands_to_run)} command(s)...")
        
        # Run each command in a separate thread
        for cmd in commands_to_run:
            thread = threading.Thread(target=self.run_single_command, args=(cmd,))
            thread.daemon = True
            thread.start()
        
        # Update status after a delay
        self.root.after(2000, self.update_status_with_process_count)
    
    def run_single_command(self, cmd):
        """Run a single command in a new command prompt or background"""
        try:
            process = None
            
            if self.run_in_background.get():
                # Run in background (no visible terminal)
                if sys.platform.startswith('win'):
                    # Windows - run in background
                    process = subprocess.Popen(cmd['command'], shell=True, 
                                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    # Unix-like systems - run in background
                    process = subprocess.Popen(cmd['command'], shell=True)
            else:
                # Run in visible terminal
                if sys.platform.startswith('win'):
                    # Windows
                    process = subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', cmd['command']], 
                                             shell=True)
                elif sys.platform.startswith('darwin'):
                    # macOS
                    script = f'''
                    tell application "Terminal"
                        activate
                        do script "{cmd['command']}"
                    end tell
                    '''
                    process = subprocess.Popen(['osascript', '-e', script])
                else:
                    # Linux and other Unix-like systems
                    # Try different terminal emulators
                    terminals = ['gnome-terminal', 'konsole', 'xterm', 'xfce4-terminal']
                    for terminal in terminals:
                        try:
                            if terminal == 'gnome-terminal':
                                process = subprocess.Popen([terminal, '--', 'bash', '-c', 
                                                        f"{cmd['command']}; read -p 'Press Enter to close...'"])
                            elif terminal == 'konsole':
                                process = subprocess.Popen([terminal, '-e', 'bash', '-c', 
                                                        f"{cmd['command']}; read -p 'Press Enter to close...'"])
                            else:
                                process = subprocess.Popen([terminal, '-e', 'bash', '-c', 
                                                        f"{cmd['command']}; read -p 'Press Enter to close...'"])
                            break
                        except FileNotFoundError:
                            continue
                    else:
                        # Fallback: run in background
                        process = subprocess.Popen(cmd['command'], shell=True)
            
            # Track the process if it's a background process
            if process and self.run_in_background.get():
                self.running_processes.append({
                    'process': process,
                    'name': cmd['name'],
                    'command': cmd['command']
                })
                self.update_status(f"Started background process: {cmd['name']}")
                    
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", 
                           f"Failed to run command '{cmd['name']}':\n{str(e)}"))
    
    def terminate_all(self):
        """Terminate all running background processes"""
        if not self.running_processes:
            messagebox.showinfo("Info", "No background processes are running.")
            return
        
        if messagebox.askyesno("Confirm Termination", 
                              f"Terminate {len(self.running_processes)} running background process(es)?"):
            terminated_count = 0
            for proc_info in self.running_processes:
                try:
                    proc_info['process'].terminate()
                    terminated_count += 1
                except Exception as e:
                    print(f"Failed to terminate process {proc_info['name']}: {e}")
            
            # Clear the list
            self.running_processes.clear()
            
            self.update_status(f"Terminated {terminated_count} background process(es)")
            
            # Update status after a delay to show current state
            self.root.after(2000, self.update_status_with_process_count)
            
            # Give processes time to terminate gracefully, then force kill if needed
            self.root.after(3000, self.force_kill_remaining)
    
    def force_kill_remaining(self):
        """Force kill any remaining processes that didn't terminate gracefully"""
        # This method can be called after a delay to force kill any stubborn processes
        # Implementation depends on the specific needs
        pass
    
    def get_running_processes_count(self):
        """Get the number of currently running background processes"""
        return len(self.running_processes)
    
    def update_status_with_process_count(self):
        """Update status to show running process count"""
        count = self.get_running_processes_count()
        if count > 0:
            self.update_status(f"Ready - {count} background process(es) running")
        else:
            self.update_status("Ready")
    
    def cleanup_finished_processes(self):
        """Remove finished processes from tracking list"""
        # Remove finished processes
        self.running_processes = [proc_info for proc_info in self.running_processes 
                                 if proc_info['process'].poll() is None]
        
        # Schedule next cleanup in 5 seconds
        self.root.after(5000, self.cleanup_finished_processes)
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
    
    def on_closing(self):
        """Handle application closing"""
        # Terminate any running background processes
        if self.running_processes:
            for proc_info in self.running_processes:
                try:
                    proc_info['process'].terminate()
                except:
                    pass
        
        self.save_commands()
        self.root.destroy()

class CommandDialog:
    def __init__(self, parent, title, name="", command=""):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x200")
        self.dialog.resizable(True, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, 
                                        parent.winfo_rooty() + 50))
        
        # Create widgets
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Name field
        ttk.Label(main_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Command field
        ttk.Label(main_frame, text="Command:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        self.command_var = tk.StringVar(value=command)
        command_entry = ttk.Entry(main_frame, textvariable=self.command_var, width=50)
        command_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Example label
        example_text = "Example: cd C:\\MyProject && python main.py"
        ttk.Label(main_frame, text=example_text, font=('Arial', 8), 
                 foreground='gray').grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).grid(row=0, column=1, padx=(5, 0))
        
        # Focus and bindings
        name_entry.focus()
        name_entry.select_range(0, tk.END)
        
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def ok_clicked(self):
        name = self.name_var.get().strip()
        command = self.command_var.get().strip()
        
        if not name:
            messagebox.showwarning("Warning", "Please enter a name for the command.")
            return
        
        if not command:
            messagebox.showwarning("Warning", "Please enter a command.")
            return
        
        self.result = (name, command)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()

def main():
    root = tk.Tk()
    
    # Set up the application icon (optional)
    try:
        # You can add an icon file here if you have one
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = CommandLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()