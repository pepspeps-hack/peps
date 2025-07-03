# utils/command_executor.py

import os
import subprocess # For running shell commands
import webbrowser # For opening web browser
import urllib.parse # For URL encoding

class CommandExecutor:
    def execute_search(self, query: str):
        """
        Simulates executing a search command.
        For now, it just prints the query.
        In a real application, this could open a search engine in a browser.
        """
        print(f"Executing search for: '{query}'")
        try:
            # Construct a Google search URL. User can change this to their preferred engine.
            # We should URL-encode the query.
            # import urllib.parse # Moved to top of file
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"

            webbrowser.open(search_url, new=2) # new=2 attempts to open in a new tab
            print(f"Attempted to open browser for search: {query} at {search_url}")
            return f"Search for '{query}' opened in browser."
        except Exception as e:
            print(f"Error opening browser for search '{query}': {e}")
            return f"Error opening browser for search '{query}': {e}. Check if a browser is available."

    def execute_sort_files(self, folder_path: str = "."):
        """
        Sorts files in the specified folder.
        This is a placeholder. Actual implementation would depend on sorting criteria.
        For now, it lists files and simulates sorting.
        """
        abs_folder_path = os.path.abspath(folder_path)
        print(f"Attempting to sort files in: '{abs_folder_path}'")
        try:
            if not os.path.isdir(abs_folder_path):
                return f"Error: Folder '{abs_folder_path}' not found."

            files = [f for f in os.listdir(abs_folder_path) if os.path.isfile(os.path.join(abs_folder_path, f))]
            # Simulate sorting (e.g., by name)
            files.sort()
            print(f"Files in '{abs_folder_path}' (simulated sort by name): {files}")
            return f"Files in '{abs_folder_path}' have been conceptually sorted."
        except Exception as e:
            print(f"Error sorting files in '{abs_folder_path}': {e}")
            return f"Error sorting files: {e}"

    def execute_browse(self, task_or_url: str):
        """
        Opens a web browser for a given task or URL.
        If it's a URL, it opens it directly.
        If it's a task, it could perform a search or navigate to a predefined site.
        """
        print(f"Executing browser task: '{task_or_url}'")
        try:
            # Basic check if it's a URL
            if task_or_url.startswith("http://") or task_or_url.startswith("https://"):
                webbrowser.open(task_or_url, new=2) # new=2 attempts to open in a new tab
                print(f"Attempted to open URL: {task_or_url}")
                return f"Opened URL: {task_or_url}"
            else:
                # For a general task, perform a search (similar to execute_search)
                encoded_task = urllib.parse.quote_plus(task_or_url)
                search_url = f"https://www.google.com/search?q={encoded_task}"
                webbrowser.open(search_url, new=2) # new=2 attempts to open in a new tab
                print(f"Attempted to open browser to search for: {task_or_url} at {search_url}")
                return f"Opened browser to search for: {task_or_url}"
        except Exception as e:
            # webbrowser.open might not work in all environments (e.g. headless server)
            print(f"Error opening browser for task '{task_or_url}': {e}")
            return f"Could not open browser for task '{task_or_url}'. This might be due to environment limitations (e.g., no GUI browser available)."


    def execute_command(self, command_name: str, argument: str = None):
        """
        Executes the given command with its argument.

        Args:
            command_name (str): The name of the command (e.g., "search").
            argument (str, optional): The argument for the command (e.g., search query).

        Returns:
            str: A message indicating the result of the execution.
        """
        if command_name == "search":
            if argument:
                return self.execute_search(argument)
            else:
                return "Error: Search query is missing."
        elif command_name == "sort_files":
            # For simplicity, sorting current directory if no specific path given by AI
            return self.execute_sort_files(".")
        elif command_name == "browse":
            if argument:
                return self.execute_browse(argument)
            else:
                return "Error: Browser task or URL is missing."
        else:
            return f"Error: Unknown command '{command_name}'."

if __name__ == '__main__':
    executor = CommandExecutor()

    # Test cases
    print("\n--- Testing CommandExecutor ---")

    result = executor.execute_command("search", "python programming tutorials")
    print(f"Result: {result}\n")

    result = executor.execute_command("sort_files") # No argument, defaults to current dir
    print(f"Result: {result}\n")

    # This will attempt to open a browser, which might not be visible in a sandbox
    # but we can check the print statements and return value.
    result = executor.execute_command("browse", "check current weather")
    print(f"Result: {result}\n")

    result = executor.execute_command("browse", "https://www.openrouter.ai")
    print(f"Result: {result}\n")

    result = executor.execute_command("unknown_command", "some argument")
    print(f"Result: {result}\n")

    result = executor.execute_command("search") # Missing argument
    print(f"Result: {result}\n")
