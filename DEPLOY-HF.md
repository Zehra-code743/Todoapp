# Deploying Todoapp on Hugging Face Spaces

This guide explains how to deploy the Todoapp application on Hugging Face Spaces using Docker.

## About Hugging Face Spaces

[Hugging Face Spaces](https://huggingface.co/spaces) is a free platform for hosting machine learning demos and applications. You can deploy your application using various SDKs, including Docker for full customization.

## Prerequisites

- GitHub account
- Hugging Face account
- Git installed on your local machine

## Deployment Steps

### 1. Prepare Your Repository

Run the Hugging Face preparation script:

**Linux/macOS:**
```bash
./deploy-hf.sh
```

**Windows (PowerShell):**
```powershell
.\deploy-hf.ps1
```

**Windows (Command Prompt):**
```cmd
deploy-hf.bat
```

This script will:
- Pull the latest changes from GitHub
- Copy the appropriate Dockerfile to the root
- Verify all required files exist

### 2. Create a Hugging Face Space

1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create New Space"
3. Fill in the details:
   - **Space name**: Choose a unique name
   - **SDK**: Select "Docker"
   - **Hardware**: Choose appropriate hardware (CPU, GPU, etc.)
   - **Repository**: Connect to your GitHub repository containing the Todoapp code
4. Click "Create Space"

### 3. Configure Environment Variables (Optional)

In your Space settings, you can add environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `DB_HOST`: Database host
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: todoapp)
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `BETTER_AUTH_SECRET`: Authentication secret
- `KAFKA_BROKERS`: Kafka broker addresses (optional)

### 4. Monitor the Build

The first build may take several minutes as it:
- Clones your repository
- Builds the Docker image
- Starts the application

You can monitor the build logs in the Space's "Logs" tab.

## Files Included for Hugging Face Deployment

- `Dockerfile.huggingface`: Optimized Dockerfile for Hugging Face Spaces
- `app.yml`: Hugging Face Space configuration
- `README.hf.md`: Documentation for Hugging Face users

## Accessing Your Application

Once the build completes successfully, your application will be accessible at:
`https://[your-username]-[space-name].hf.space`

## Troubleshooting

### Build Failures
- Check the build logs in the Space's "Logs" tab
- Ensure all dependencies in `requirements.txt` are compatible with the Hugging Face environment
- Verify that the Dockerfile exposes the correct port (7860 or 8000)

### Runtime Issues
- Check runtime logs in the Space's "Logs" tab
- Verify environment variables are set correctly
- Ensure the application binds to the correct host (0.0.0.0) and port

### Resource Constraints
- Hugging Face Spaces have limited resources
- Optimize your application for the available CPU/RAM
- Consider upgrading to a paid Space for more resources

## Updating Your Application

To update your deployed application:

1. Make changes to your local repository
2. Commit and push changes to GitHub
3. The Space will automatically rebuild with the latest code
4. Monitor the build logs to ensure successful deployment

## Limitations

- Hugging Face Spaces have resource constraints compared to cloud platforms
- Some services (like persistent databases) may need external providers
- Free Spaces may have limited uptime and performance

## Alternative: Direct Docker Approach

If you prefer to build and push to a container registry:

1. Build the image: `docker build -f Dockerfile.huggingface -t your-image-name .`
2. Tag and push to a registry
3. Configure your Space to use the external image

Your Todoapp is now ready to be deployed on Hugging Face Spaces! Follow the steps above to create your Space and start sharing your application with the world.