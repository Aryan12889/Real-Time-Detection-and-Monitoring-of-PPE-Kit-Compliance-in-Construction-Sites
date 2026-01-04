# PPE Kit Detection Dashboard

An advanced computer vision dashboard for monitoring Personal Protective Equipment (PPE) compliance and fire hazards in real-time. This application provides a centralized interface for managing surveillance cameras, configuring employee access, and viewing real-time alerts.

This project is a part of the final project required for passing the degree at SRM University. The submission of this project is mandatory and is required to be submitted by the end of the academic year. The code base was submitted via ZIP file to the panel members in May of 2025.

## Technical Documentation
For a detailed analysis of the system architecture, methodology, and compliance standards, please refer to the [PPE Compliance Technical Report SRMIST 2025](PPE%20Compliance%20Technical%20Report%20SRMIST%202025.pdf) included in this repository.

## Features

-   **Dashboard Overview**: Real-time monitoring of camera feeds with detection status.
-   **Camera Management**: Add, edit, and delete camera checkpoints. Supports RTSP and playback URLs.
-   **Employee Configuration**: Manage authorized personnel with secure role-based access.
-   **Real-time Alerts**: Instant notifications for PPE violations (e.g., missing helmet/vest) and fire hazards.
-   **Model Mapping**: Dynamically map specific AI models (PPE Detection, Fire Detection) to individual cameras.
-   **Secure Deletion**: Critical actions like deletion require explicit text confirmation.

## Tech Stack

-   **Frontend**: HTML5, Tailwind CSS, JavaScript (Vanilla)
-   **Backend**: Python, Flask
-   **Data Storage**: JSON-based persistence (`cameras.json`, `employees.json`)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Install Dependencies:**
    Ensure you have Python installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python app.py
    ```

4.  **Access the Dashboard:**
    Open your browser and navigate to: `http://127.0.0.1:5000`

## Usage Notes

-   **Admin Access**: The dashboard is designed for administrative use (Super Admin).
-   **Simulation Data**: Please note that for demonstration purposes, the video feeds used in this repository (`static/videos/`) are simulated recordings to showcase the detection capabilities without requiring live camera hardware.
-   **Data Persistence**: Configuration changes (adding cameras/employees) are saved locally to `.json` files.

## Project Structure

-   `app.py`: Main Flask application entry point.
-   `templates/`: HTML frontend templates.
-   `static/`: CSS, JavaScript, and media assets.
-   `cameras.json` & `employees.json`: Local database files.

---