#!/bin/bash

echo "Starting SwiftLogistics External Systems..."

# Build and start the services
docker-compose up --build -d

echo "Services are starting up..."
echo "PostgreSQL will be available on localhost:5432"
echo "CMS API will be available on localhost:8000"
echo ""
echo "To check logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs"