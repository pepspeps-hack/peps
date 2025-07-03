# AI Control Application

This application allows you to control computer functions using text commands, interpreted by an AI model via the OpenRouter API. It currently features a Graphical User Interface (GUI).

## Features

-   **AI-Powered Command Interpretation:** Uses an AI model (configurable, defaults to `openrouter/cypher-alpha:free`) to understand user commands.
-   **Supported Commands:**
    -   `Search for [query]`: Opens a web browser to search for the query.
    -   `Sort files in this folder`: Lists files in the current directory (simulates sorting).
    -   `Use my browser to [task/URL]`: Opens a web browser for a specific task or URL.
-   **Graphical User Interface (GUI):** Provides a user-friendly interface for command input and viewing history/responses.
-   **Command History:** Displays a log of user commands, AI interpretations, and system actions.

## Setup and Installation

1.  **Prerequisites:**
    *   Python 3.7+
    *   `pip` (Python package installer)

2.  **Clone the Repository (if applicable):**
    ```bash
    # git clone [repository-url]
    # cd [repository-directory]
    ```

3.  **Install Dependencies:**
    The application uses the `requests` library for API calls and Tkinter (usually included with Python) for the GUI.
    ```bash
    pip install requests
    ```

4.  **API Key Configuration:**
    The application requires an OpenRouter API key.

    **!!! IMPORTANT SECURITY NOTE !!!**
    The current version of `utils/openrouter_client.py` has a placeholder for an API key (`PROVIDED_API_KEY`). For the purpose of a guided development session, an API key might have been temporarily hardcoded by the user.

    **For secure and proper usage, you should ALWAYS manage your API keys securely:**
    *   **Recommended Method: Environment Variables:**
        1.  It is strongly advised to modify `utils/openrouter_client.py` to fetch the API key from an environment variable.
            *   Change `PROVIDED_API_KEY = "sk-or-v1-..."` to `OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")` (ensure `import os` is present).
            *   In the `__init__` method of `OpenRouterClient`, change `self.api_key = api_key or PROVIDED_API_KEY` to `self.api_key = api_key or OPENROUTER_API_KEY`.
            *   Ensure the `ValueError` for a missing key is appropriately handled if `OPENROUTER_API_KEY` is `None`.
        2.  Set the `OPENROUTER_API_KEY` environment variable in your system before running the application:
            *   On Linux/macOS: `export OPENROUTER_API_KEY="your_actual_api_key"`
            *   On Windows (cmd.exe): `set OPENROUTER_API_KEY="your_actual_api_key"`
            *   On Windows (PowerShell): `$env:OPENROUTER_API_KEY="your_actual_api_key"`
    *   **Alternative (less secure for shared environments):** Configuration files that are *not* committed to version control.

    Failure to properly secure your API key can lead to unauthorized use and potential charges to your account. The developer/user is responsible for API key security.

## Running the Application

Once the setup is complete and the API key is configured (preferably via environment variables):

```bash
python main.py
```

This will launch the GUI. Type your commands into the input field and press Enter or click "Submit".

## How It Works

1.  You type a command into the GUI (e.g., "search for cute puppies").
2.  The command is sent to the configured OpenRouter AI model.
3.  A system prompt guides the AI to interpret your command and identify one of the known actions (`search`, `sort_files`, `browse`) and any associated arguments.
4.  The AI is instructed to respond in a specific format: `COMMAND: [action] ARGUMENT: [details]`.
5.  The application parses this structured response from the AI.
6.  If a known command is identified, the corresponding function in `CommandExecutor` is called (e.g., opening a browser for a search).
7.  All interactions (your input, AI's raw response, interpreted command, execution result) are displayed in the GUI's history panel.

## Project Structure

-   `main.py`: Entry point to launch the GUI application.
-   `gui/app_gui.py`: Contains the Tkinter GUI code and integrates the application logic.
-   `utils/openrouter_client.py`: Manages communication with the OpenRouter API. **(Modify for secure API key handling!)**
-   `utils/command_executor.py`: Handles the execution of recognized commands (e.g., web search, file sorting simulation).
-   `utils/voice_parser.py`: (Currently unused by default in GUI mode) Contains regex-based parsing, kept for potential future use or simpler command modes.
-   `tests/`: Contains unit tests for various components.
-   `README.md`: This file.

## Future Enhancements (Stretch Goals)

-   **Voice Recognition:** Integrate a voice recognition library to allow voice commands.
-   **Refined Tool Calling:** If the AI model supports it robustly, implement proper tool/function calling for more reliable command execution.
-   **Customizable Commands:** Allow users to define or map new commands.
-   **Improved Error Handling:** More granular error messages and recovery options.
-   **Configuration File:** For settings like default model, API key (if not using env vars), etc.

## Troubleshooting

-   **API Errors / "Could not connect to OpenRouter":**
    *   Verify your API key is correct and active.
    *   Check if the `OPENROUTER_API_KEY` environment variable is correctly set and exported to the terminal session where you run the app (if using environment variables).
    *   Ensure you have a stable internet connection.
    *   Check the OpenRouter dashboard for any issues with your account or the specific model being used (e.g., rate limits for free models).
-   **GUI Not Launching / Tkinter Errors:**
    *   Ensure Tkinter is properly installed with your Python distribution. For some Linux systems, you might need to install it separately (e.g., `sudo apt-get install python3-tk`).
-   **Command Not Understood:**
    *   The AI (`openrouter/cypher-alpha:free` by default) tries its best, but complex or ambiguous phrasing might not be interpreted correctly. Try rephrasing your command to be more direct and align with the examples (search for X, sort files, browse Y).
    *   The system prompt in `gui/app_gui.py` (variable `SYSTEM_PROMPT`) defines how the AI is instructed. Modifying this might improve or change interpretation.

---
This README provides a basic guide. Remember to handle your API keys securely.
