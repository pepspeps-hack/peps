# utils/voice_parser.py

import re

class VoiceParser:
    def __init__(self):
        # Define command patterns using regular expressions
        # These can be expanded and made more sophisticated
        self.command_patterns = {
            "search": re.compile(r"search for (.+)", re.IGNORECASE),
            "sort_files": re.compile(r"sort files(?: in this folder)?", re.IGNORECASE),
            "browse": re.compile(r"use my browser to (.+)", re.IGNORECASE),
            # Add more commands here
        }

    def parse_command(self, text_input: str):
        """
        Parses the text input to identify a command and its arguments.

        Args:
            text_input (str): The simulated voice input (as text).

        Returns:
            tuple: (command_name, argument) or (None, None) if no command matches.
                   'command_name' is a string like "search", "sort_files", "browse".
                   'argument' is the extracted query or task.
        """
        for command_name, pattern in self.command_patterns.items():
            match = pattern.match(text_input)
            if match:
                # If the pattern has groups, the first group is usually the argument.
                # For patterns without groups (like sort_files), there's no specific argument extracted here.
                argument = match.group(1) if len(match.groups()) > 0 else None
                return command_name, argument

        return None, None

if __name__ == '__main__':
    parser = VoiceParser()

    # Test cases
    commands_to_test = [
        "Search for cute cat videos",
        "search for latest AI news",
        "Sort files in this folder",
        "sort files",
        "Use my browser to check emails",
        "use my browser to find python tutorials",
        "Open calculator", # Should not match
        "What's the weather?", # Should not match
    ]

    for cmd_text in commands_to_test:
        command, arg = parser.parse_command(cmd_text)
        if command:
            print(f"Input: '{cmd_text}' -> Command: '{command}', Argument: '{arg}'")
        else:
            print(f"Input: '{cmd_text}' -> No command recognized.")
