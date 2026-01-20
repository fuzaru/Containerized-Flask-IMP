# Convenience Store Inventory Management System (CSIMS)

A Flask-based web application for managing inventory in a convenience store, featuring custom data structures like linked lists, stacks, and queues.

## Features

- Product and customer management with linked lists
- Undo/redo functionality using stacks
- Restock queue for inventory replenishment
- Search capabilities for products and customers
- Web interface with responsive design

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Convenience-Store-Storage-System
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python archive_v2_final.py
   ```

   The app will be available at `http://localhost:5000`.

## Containerization with Docker

1. Build the Docker image:
   ```
   docker build -t csims .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 csims
   ```

   Access the app at `http://localhost:5000`.

## Deployment to Heroku

1. Install the Heroku CLI and log in.

2. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```

3. Deploy:
   ```
   git push heroku main
   ```

   The app will be live at `https://your-app-name.herokuapp.com`.

## Technologies Used

- Flask
- HTML/CSS
- Docker
- Heroku