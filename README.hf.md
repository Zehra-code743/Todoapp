# Todoapp on Hugging Face Spaces

This repository contains the Todoapp application ready to be deployed on Hugging Face Spaces.

## About This App

Todoapp is a modern task management application built with FastAPI, featuring:
- RESTful API endpoints
- PostgreSQL database integration
- Real-time notifications
- Authentication and user management
- Task scheduling and recurring tasks

## Deployment on Hugging Face Spaces

This app can be deployed on Hugging Face Spaces using Docker. The deployment includes:

- Backend API server (FastAPI)
- Database connectivity
- All required dependencies

## How to Deploy

1. Fork this repository
2. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
3. Select "Docker" as the SDK
4. Connect to your forked repository
5. The app will automatically build and deploy

## Configuration

The application expects the following environment variables (set in Space settings):
- `DATABASE_URL`: PostgreSQL connection string
- `DB_HOST`: Database host (defaults to localhost)
- `DB_PORT`: Database port (defaults to 5432)
- `DB_NAME`: Database name (defaults to todoapp)
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `BETTER_AUTH_SECRET`: Authentication secret
- `KAFKA_BROKERS`: Kafka broker addresses (optional)

## Ports

- Main application: Port 7860 (Hugging Face default) or 8000

## Resources

This application is optimized to run within Hugging Face Spaces' resource constraints. For optimal performance, consider selecting a GPU or high-CPU space if your usage demands it.

## Support

For issues with the application functionality, please check the original repository. For deployment-specific issues, consult the [Hugging Face documentation](https://huggingface.co/docs/hub/spaces).