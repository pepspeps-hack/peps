# LuxeWatch Emporium - Luxury E-Commerce Website

Welcome to LuxeWatch Emporium, a sophisticated e-commerce platform for showcasing and selling high-end luxury watches. This project is built using Python with the Flask web framework.

## Project Structure

-   `/app`: Contains the core Flask application.
    -   `main.py`: The main Flask application file with route definitions, product data, and business logic.
    -   `/static`: Contains static assets.
        -   `/css`: Stylesheets (e.g., `style.css`).
        -   `/js`: JavaScript files (e.g., `main.js`).
        -   `/images`: Placeholder for product images and other site imagery (currently uses styled div placeholders).
    -   `/templates`: HTML templates used by Flask to render pages.
-   `run_server.bat`: A batch script to easily start the server on Windows.
-   `run_server.sh`: A shell script to easily start the server on Linux/macOS.
-   `README.md`: This file.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   **Python:** Ensure you have Python installed (Python 3.7+ recommended). You can download it from [python.org](https://www.python.org/downloads/).
-   **pip:** Python's package installer, usually comes with Python.

### Installation

1.  **Clone the repository (or download the files):**
    If this were a Git repository, you would clone it. For now, ensure you have all the project files in a local directory.

2.  **Install Dependencies:**
    The primary dependency for this project is Flask. Open your terminal or command prompt and run:
    ```bash
    pip install Flask
    ```
    It's highly recommended to use a virtual environment for Python projects to manage dependencies effectively:
    ```bash
    # Create a virtual environment (e.g., named 'venv')
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    # venv\Scripts\activate
    # On Linux/macOS:
    # source venv/bin/activate

    # Then install Flask within the activated environment
    pip install Flask
    ```

### Running the Application

Once Flask is installed (and your virtual environment is activated, if you're using one), you can run the application using the provided scripts:

**On Windows:**

1.  Simply double-click the `run_server.bat` file located in the project's root directory.
2.  Alternatively, open a command prompt in the project's root directory and run:
    ```bash
    run_server.bat
    ```

**On Linux/macOS:**

1.  Open your terminal in the project's root directory.
2.  Make the script executable (you only need to do this once):
    ```bash
    chmod +x run_server.sh
    ```
3.  Run the script:
    ```bash
    ./run_server.sh
    ```

**Accessing the Website:**

After running the script, the terminal/command prompt will indicate that the Flask development server is running. It will typically be available at:

`http://127.0.0.1:5000/`

Open this URL in your web browser to view the LuxeWatch Emporium website.

To stop the server, go back to the terminal/command prompt where it's running and press `Ctrl+C`.

## Features

-   **Homepage:** Displays a hero section and featured luxury watches.
-   **Product Detail Pages:** Shows detailed information about each watch, including specifications.
-   **Shopping Cart:** Allows users to add, update, and remove products from their cart using session-based storage.
-   **Checkout Process:** A conceptual checkout page with forms for shipping, billing, and (mock) payment information.
-   **Luxury Design:** Styled with a sophisticated color palette (deep charcoal, muted gold, white) and elegant typography (Playfair Display and Lato).
-   **Responsive Layout:** Basic responsiveness for various screen sizes.
-   **Image Placeholders:** Uses styled `div` elements as placeholders for product images, ensuring layout integrity.

## Further Development (Conceptual)

-   Database integration for products, users, and orders.
-   User authentication and accounts.
-   Payment gateway integration.
-   Advanced search and filtering.
-   Admin panel for managing products and orders.
-   Actual image hosting and management.
-   More comprehensive JavaScript interactions and animations.

---

Thank you for exploring LuxeWatch Emporium!
