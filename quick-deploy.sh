#!/bin/bash
# Quick Start Deployment Script
# This script combines all deployment steps into one command

echo "🚀 Todoapp Quick Deployment"
echo "============================="
echo "This script will:"
echo "1. Pull latest code from GitHub"
echo "2. Build Docker images"
echo "3. Deploy to Kubernetes"
echo ""

read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting deployment..."
    ./deploy.sh
else
    echo ""
    echo "Deployment cancelled."
    echo "To deploy manually, run: ./deploy.sh"
fi