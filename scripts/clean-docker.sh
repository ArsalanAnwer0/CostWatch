#!/bin/bash

# Docker Cleanup Script for CostWatch
# Removes all CostWatch containers, images, and volumes

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}CostWatch Docker Cleanup Script${NC}"
echo ""
echo "This will remove:"
echo "  - All CostWatch containers"
echo "  - All CostWatch images"
echo "  - All CostWatch volumes (database data will be lost!)"
echo ""

read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Stopping and removing containers..."
docker-compose down -v 2>/dev/null || echo "No running containers"

echo "Removing CostWatch images..."
docker images | grep costwatch | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || echo "No CostWatch images found"
docker images | grep youthful-rubin | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || echo "No youthful-rubin images found"

echo "Removing dangling images..."
docker image prune -f

echo "Removing unused volumes..."
docker volume prune -f

echo ""
echo -e "${GREEN}✓ Cleanup complete!${NC}"
echo ""
echo "To rebuild and start:"
echo "  docker-compose build"
echo "  docker-compose up -d"
