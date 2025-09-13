#!/bin/bash

# CostWatch Development Stop Script

echo " Stopping CostWatch development environment..."

# Stop all services
docker-compose down

# Optional: Remove volumes (uncomment if you want to reset data)
# docker-compose down -v

echo " CostWatch development environment stopped"
echo ""
echo " To remove all data, run: docker-compose down -v"