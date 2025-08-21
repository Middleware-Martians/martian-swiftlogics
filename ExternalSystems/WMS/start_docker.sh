#!/bin/bash

# Script to start or stop WMS mock system docker container

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/mock-wms"

function show_help() {
    echo "Usage: $0 [start|stop|restart|status|logs|build]"
    echo ""
    echo "Commands:"
    echo "  start      Start the WMS mock system"
    echo "  stop       Stop the WMS mock system"
    echo "  restart    Restart the WMS mock system"
    echo "  status     Check the status of the WMS mock system"
    echo "  logs       Show logs from the WMS mock system"
    echo "  build      Build the Docker image"
}

function start_service() {
    echo "Starting WMS mock system..."
    docker-compose up -d
    echo "WMS mock system started."
    echo "TCP server listening on port 5000"
    echo "HTTP API available at http://localhost:5001"
}

function stop_service() {
    echo "Stopping WMS mock system..."
    docker-compose down
    echo "WMS mock system stopped."
}

function show_status() {
    echo "WMS mock system status:"
    docker-compose ps
}

function show_logs() {
    echo "WMS mock system logs:"
    docker-compose logs -f
}

function build_service() {
    echo "Building WMS mock system..."
    docker-compose build
    echo "WMS mock system build completed."
}

# Main logic
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        start_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    build)
        build_service
        ;;
    *)
        show_help
        exit 1
        ;;
esac

exit 0
