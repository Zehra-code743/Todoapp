"""
Quickstart guide for the Advanced Todo application.
Contains initialization and setup code for getting started quickly.
"""
import os
import subprocess
from pathlib import Path


def setup_project():
    """
    Setup the project with initial configuration.
    """
    print("Setting up Advanced Todo application...")

    # Create necessary directories
    directories = [
        "backend/src/models",
        "backend/src/services",
        "backend/src/api/v1",
        "backend/src/api/middleware",
        "backend/src/utils",
        "backend/src/config",
        "backend/tests",
        "backend/tests/unit",
        "backend/tests/integration"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files to make them Python packages
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.touch()

    print("Directories created successfully.")


def setup_database():
    """
    Initialize the database with required tables.
    """
    print("Initializing database...")

    # Import and run database migrations
    try:
        from database_migrations import migrate_database
        success = migrate_database()
        if success:
            print("Database initialized successfully.")
        else:
            print("Database initialization failed.")
    except ImportError:
        print("Could not import database migrations. Please ensure all dependencies are installed.")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")


def install_dependencies():
    """
    Install required dependencies from requirements.txt.
    """
    print("Installing dependencies...")

    try:
        subprocess.run(["pip", "install", "-r", "backend/requirements.txt"], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {str(e)}")
    except FileNotFoundError:
        print("requirements.txt not found. Please ensure you're in the project root directory.")


def run_server():
    """
    Run the development server.
    """
    print("Starting the development server...")

    try:
        subprocess.run([
            "uvicorn",
            "src.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {str(e)}")
    except FileNotFoundError:
        print("uvicorn not found. Please install it using 'pip install uvicorn[standard]'")


def show_api_docs():
    """
    Show information about accessing API documentation.
    """
    print("\nAPI Documentation:")
    print("- Swagger UI: http://localhost:8000/docs")
    print("- ReDoc: http://localhost:8000/redoc")
    print("- Health check: http://localhost:8000/health")


def show_setup_complete():
    """
    Show completion message with next steps.
    """
    print("\n" + "="*60)
    print("🎉 Advanced Todo Application Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the configuration in backend/src/config/")
    print("2. Customize models in backend/src/models/ if needed")
    print("3. Add your business logic to backend/src/services/")
    print("4. Define additional API endpoints in backend/src/api/v1/")
    print("5. Run 'python src/quickstart.py run' to start the server")
    print("\nAPI Documentation will be available at:")
    print("- http://localhost:8000/docs (Swagger UI)")
    print("- http://localhost:8000/redoc (ReDoc)")


def main(command="setup"):
    """
    Main function to handle quickstart commands.

    Args:
        command: Command to execute ('setup', 'init-db', 'install', 'run', 'docs')
    """
    if command == "setup":
        setup_project()
        install_dependencies()
        setup_database()
        show_setup_complete()
    elif command == "init-db":
        setup_database()
    elif command == "install":
        install_dependencies()
    elif command == "run":
        run_server()
    elif command == "docs":
        show_api_docs()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: setup, init-db, install, run, docs")


if __name__ == "__main__":
    import sys

    # Get command from command line arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "setup"
    main(command)