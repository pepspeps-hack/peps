#!/bin/bash
echo "Starting LuxeWatch Emporium Server..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change directory to the 'app' folder relative to the script's location
cd "$SCRIPT_DIR/app" || exit

echo "Launching Flask application (main.py)..."
# Run the Flask application
# Try python3 first, then python if python3 is not available
if command -v python3 &>/dev/null; then
    python3 main.py
elif command -v python &>/dev/null; then
    python main.py
else
    echo "Error: Python interpreter not found. Please install Python."
    exit 1
fi

echo "Server stopped."
