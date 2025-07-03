# gui/app_gui.py

import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, PhotoImage # Added PhotoImage
import threading # To run AI/command processing in a separate thread
import requests # For handling network exceptions specifically

# Placeholder for application logic integration
from utils.command_executor import CommandExecutor
from utils.openrouter_client import OpenRouterClient
import re # For AI_RESPONSE_PATTERN

# --- Logic moved from main.py ---
# System prompt to guide the AI for command interpretation
SYSTEM_PROMPT = """\
You are an AI assistant that interprets user commands for controlling a computer.
The available commands are:
1.  "search [query]": To search the web. Example: "search for funny cat videos"
2.  "sort_files": To sort files in the current folder. Example: "sort files"
3.  "browse [task_or_url]": To open a web browser for a task or URL. Example: "browse open a news website" or "browse https://example.com"

Given a user's command, identify which of these three commands is most appropriate.
Respond ONLY with the command name and the argument, in the format:
COMMAND: [command_name] ARGUMENT: [argument_value]
If there is no argument, respond with:
COMMAND: [command_name] ARGUMENT: None
If the command is unclear or doesn't match any of the above, respond with:
COMMAND: unknown ARGUMENT: None
"""

# Pre-compile regex for parsing the AI's structured response
AI_RESPONSE_PATTERN = re.compile(r"COMMAND:\s*(\w+)\s*ARGUMENT:\s*(.+)", re.IGNORECASE)

def parse_ai_response_to_command(ai_text_response: str):
    if not ai_text_response:
        return None, None
    match = AI_RESPONSE_PATTERN.match(ai_text_response.strip())
    if match:
        command_name = match.group(1).lower()
        argument_str = match.group(2).strip()
        if command_name == "unknown": return None, None
        argument = None if argument_str.lower() == "none" else argument_str
        # Optional: further validate command_name against a list of known commands
        # if command_name not in ["search", "sort_files", "browse"]: return None, None
        return command_name, argument
    return None, None
# --- End of logic moved from main.py ---


class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Control Application")
        self.root.geometry("700x500")

        # --- Load Icon (Optional) ---
        # Create a simple icon with Tkinter drawing for placeholder
        # In a real app, you'd use `self.root.iconbitmap('path/to/icon.ico')` on Windows
        # or PhotoImage for other systems if you have an image file.
        try:
            # Attempt to create a simple icon (may not work on all OS/Tk configurations for window icon)
            # For a more robust solution, provide an actual .png or .ico file.
            icon_image = PhotoImage(width=16, height=16)
            icon_image.put(("black",), to=(0,0,7,7)) # Draw a small black square
            icon_image.put(("white",), to=(8,8,15,15)) # Draw a small white square
            self.root.iconphoto(True, icon_image) # True means default icon for all windows
        except tk.TclError:
            print("Could not set a placeholder window icon (PhotoImage might not be fully supported for icons on this system without a file).")


        # --- Main Frame ---
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Command History / Output Area ---
        history_label = tk.Label(main_frame, text="Command History & AI Responses:")
        history_label.pack(anchor=tk.W)

        self.history_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        self.history_text.pack(fill=tk.BOTH, expand=True, pady=(0,10))

        # --- Input Frame ---
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X)

        input_label = tk.Label(input_frame, text="Your Command:")
        input_label.pack(side=tk.LEFT, padx=(0,5))

        self.command_entry = tk.Entry(input_frame, width=60)
        self.command_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        self.command_entry.bind("<Return>", self.submit_command_event) # Bind Enter key

        self.submit_button = tk.Button(input_frame, text="Submit", command=self.submit_command)
        self.submit_button.pack(side=tk.LEFT)

        # --- Status Bar (Optional) ---
        self.status_bar = tk.Label(root, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Initialize application logic components ---
        self.executor = CommandExecutor()
        self.openrouter_client = None
        try:
            self.openrouter_client = OpenRouterClient()
            self.update_status(f"Connected to OpenRouter: {self.openrouter_client.model_name}")
            self.add_to_history(f"System: Connected to OpenRouter model: {self.openrouter_client.model_name}", "system_info")
        except ValueError as e: # Catch specific ValueError from OpenRouterClient
            self.update_status(f"Error: Could not connect to OpenRouter: {e}")
            self.add_to_history(f"System Error: Could not connect to OpenRouter: {e}", "system_error")
            messagebox.showerror("OpenRouter Connection Error", f"Could not initialize OpenRouterClient: {e}\nPlease check API key and configuration.")
        except Exception as e: # Catch any other unexpected errors during init
            self.update_status(f"Critical Error: Initialization failed: {e}")
            self.add_to_history(f"System Critical Error: Initialization failed: {e}", "system_error")
            messagebox.showerror("Initialization Error", f"A critical error occurred during app initialization: {e}")

        self.add_to_history("Welcome to the AI Control Application (GUI Mode)!\nType your command below and press Enter or click Submit.")

        # Define tags for styling history text (optional)
        self.history_text.tag_config("user_command", foreground="blue")
        self.history_text.tag_config("ai_raw", foreground="gray", font=('TkDefaultFont', 8))
        self.history_text.tag_config("ai_interpreted", foreground="purple")
        self.history_text.tag_config("ai_result", foreground="green")
        self.history_text.tag_config("ai_thinking", foreground="orange")
        self.history_text.tag_config("ai_error", foreground="red")
        self.history_text.tag_config("system_info", foreground="dark cyan")
        self.history_text.tag_config("system_error", foreground="red", font=('TkDefaultFont', 9, 'bold'))


    def update_status(self, message):
        self.status_bar.config(text=f"Status: {message}")
        self.root.update_idletasks()

    def add_to_history(self, message, tag=None):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, message + "\n", tag)
        self.history_text.see(tk.END) # Scroll to the end
        self.history_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def submit_command_event(self, event): # Handles Enter key press
        self.submit_command()

    def submit_command(self):
        user_input = self.command_entry.get()
        if not user_input:
            messagebox.showwarning("Empty Command", "Please enter a command.")
            return

        self.add_to_history(f"You: {user_input}", "user_command")
        self.command_entry.delete(0, tk.END)
        self.update_status("Processing command...")

        # Disable button during processing
        self.submit_button.config(state=tk.DISABLED)
        self.command_entry.config(state=tk.DISABLED)

        # Simulate processing for now - replace with actual logic
        # In a real app, this would call the AI and command execution logic
        # This should be run in a separate thread to avoid freezing the GUI
        # Also, ensure openrouter_client is available before proceeding
        if not self.openrouter_client:
            messagebox.showerror("OpenRouter Error", "OpenRouter client is not available. Cannot process command.")
            self.add_to_history("System Error: OpenRouter client not initialized. Command aborted.", "system_error")
            self._finalize_command_processing() # Re-enable UI
            return

        threading.Thread(target=self._process_command_thread, args=(user_input,), daemon=True).start()

    def _process_command_thread(self, user_input):
        try:
            self.root.after(0, self.add_to_history, "AI: Thinking...", "ai_thinking")

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]

            ai_response_json = self.openrouter_client.send_chat_completion(messages)

            parsed_command = None
            argument = None
            ai_raw_response_for_history = "No valid response structure from AI."

            if ai_response_json:
                if ai_response_json.get("choices") and \
                   isinstance(ai_response_json["choices"], list) and \
                   len(ai_response_json["choices"]) > 0 and \
                   isinstance(ai_response_json["choices"][0], dict) and \
                   ai_response_json["choices"][0].get("message") and \
                   isinstance(ai_response_json["choices"][0]["message"], dict):

                    ai_message_content = ai_response_json["choices"][0]["message"].get("content")
                    if ai_message_content:
                        ai_raw_response_for_history = ai_message_content.strip()
                        self.root.after(0, self.add_to_history, f"AI Raw: {ai_raw_response_for_history}", "ai_raw")
                        parsed_command, argument = parse_ai_response_to_command(ai_raw_response_for_history)
                    else:
                        ai_raw_response_for_history = "AI: Received no content in message from OpenRouter."
                        self.root.after(0, self.add_to_history, ai_raw_response_for_history, "ai_error")
                elif ai_response_json.get("error"):
                    error_details = ai_response_json["error"].get("message", "Unknown error")
                    ai_raw_response_for_history = f"AI Error: {error_details}"
                    self.root.after(0, self.add_to_history, ai_raw_response_for_history, "ai_error")
                else: # Fallback for unexpected JSON structure
                    ai_raw_response_for_history = f"AI: Unexpected response structure: {str(ai_response_json)[:200]}..."
                    self.root.after(0, self.add_to_history, ai_raw_response_for_history, "ai_error")
            else: # No JSON response at all
                ai_raw_response_for_history = "AI: Failed to get any response from OpenRouter."
                self.root.after(0, self.add_to_history, ai_raw_response_for_history, "ai_error")

            if parsed_command:
                self.root.after(0, self.add_to_history, f"AI Interpreted: '{parsed_command}' with argument: '{argument}'", "ai_interpreted")
                # Execute command using CommandExecutor
                # Note: CommandExecutor methods (like webbrowser.open or os.listdir) might also benefit from
                # being run in their own sub-threads if they are blocking, but for now, keeping it simpler.
                # If executor methods are very slow, GUI might still lag during their execution.
                execution_result = self.executor.execute_command(parsed_command, argument)
                self.root.after(0, self.add_to_history, f"System: {execution_result}", "ai_result")
            else:
                self.root.after(0, self.add_to_history, "AI: Could not determine a valid command from your request based on its response. Please try rephrasing.", "ai_error")

        except requests.exceptions.RequestException as e: # Handle network errors specifically
            error_msg = f"Network Error: Could not connect to OpenRouter: {e}"
            self.root.after(0, self.add_to_history, error_msg, "system_error")
            self.root.after(0, messagebox.showerror, "Network Error", error_msg)
        except Exception as e:
            error_msg = f"Error during command processing: {e}"
            self.root.after(0, self.add_to_history, error_msg, "system_error")
            # Show a popup for unexpected errors too
            self.root.after(0, messagebox.showerror, "Processing Error", error_msg)
        finally:
            # Re-enable button and entry after processing (must be done via root.after for thread safety)
            self.root.after(0, self._finalize_command_processing)

    def _finalize_command_processing(self):
        self.update_status("Ready")
        self.submit_button.config(state=tk.NORMAL)
        self.command_entry.config(state=tk.NORMAL)
        self.command_entry.focus_set() # Put cursor back in entry

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit AI Control Application?"):
            self.root.destroy()

def start_gui():
    root = tk.Tk()
    app = AppGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing) # Handle window close button
    root.mainloop()

if __name__ == '__main__':
    # This allows running the GUI standalone for দেখতে (seeing) and basic interaction.
    # Full functionality requires integrating the logic from main.py
    start_gui()
