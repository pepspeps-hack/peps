# Main application file

from utils.voice_parser import VoiceParser
from utils.command_executor import CommandExecutor
# from utils.openrouter_client import OpenRouterClient # Will be used more directly later

def main_cli():
    print("AI Control Application - CLI Mode")
    print("Type your command, or 'exit' to quit.")

    parser = VoiceParser()
    executor = CommandExecutor()
    # client = OpenRouterClient() # Initialize if needed for direct AI interaction step

    command_history = []

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting application.")
                break

            command_history.append({"user": user_input, "ai_response": ""})

            # Step 1: Parse the command from user input (simulating voice recognition)
            parsed_command, argument = parser.parse_command(user_input)

            if not parsed_command:
                response = "AI: I didn't understand that command. Try 'Search for [query]', 'Sort files', or 'Use my browser to [task]'."
                print(response)
                command_history[-1]["ai_response"] = response
                continue

            # Step 2: (Future) Send to OpenRouter for interpretation or refinement.
            # For now, we directly use the parsed command.
            # Example (conceptual):
            # messages = [{"role": "user", "content": f"Interpret this command: {user_input}"}]
            # ai_interpretation = client.send_chat_completion("chosen_model_name", messages)
            # if ai_interpretation and ai_interpretation.get("choices"):
            #     # Process ai_interpretation to get refined command and args
            #     # This is where 'tool_calling' would be handled if the AI suggests a function call.
            #     refined_command_info = ai_interpretation["choices"][0]["message"].get("tool_calls") # Example
            #     if refined_command_info:
            #          # Extract command and args from tool_calls
            #          pass # Placeholder for actual parsing
            #     else:
            #          # Fallback or direct execution
            #          pass


            # Step 3: Execute the command
            print(f"AI: Interpreted command: '{parsed_command}' with argument: '{argument}'")
            execution_result = executor.execute_command(parsed_command, argument)

            response = f"AI: {execution_result}"
            print(response)
            command_history[-1]["ai_response"] = execution_result

        except KeyboardInterrupt:
            print("\nExiting application via Ctrl+C.")
            break
        except Exception as e:
            error_message = f"An unexpected error occurred in the main loop: {e}"
            print(error_message)
            # Log this error appropriately in a real application
            command_history.append({"user": "ERROR", "ai_response": error_message})


if __name__ == "__main__":
    main_cli()
