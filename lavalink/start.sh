#!/bin/bash

echo "Starting Lavalink server..."

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed or not in PATH. Lavalink requires Java 11 or higher."
    echo "Please install Java before continuing."
    exit 1
fi

# Check Java version (need 11+)
java_version=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
if [[ "$(echo $java_version | cut -d'.' -f1)" -lt 11 ]]; then
    echo "Error: Java 11 or higher is required. Current version: $java_version"
    echo "Please install a compatible Java version."
    exit 1
fi

# Check if Lavalink.jar exists
if [ ! -f "Lavalink.jar" ]; then
    echo "Lavalink.jar not found. Downloading Lavalink..."
    
    if command -v curl &> /dev/null; then
        curl -L "https://github.com/lavalink-devs/Lavalink/releases/download/3.7.9/Lavalink.jar" -o "Lavalink.jar"
    elif command -v wget &> /dev/null; then
        wget "https://github.com/lavalink-devs/Lavalink/releases/download/3.7.9/Lavalink.jar" -O "Lavalink.jar"
    else
        echo "Error: Neither curl nor wget is installed. Cannot download Lavalink.jar."
        exit 1
    fi
    
    if [ ! -f "Lavalink.jar" ]; then
        echo "Failed to download Lavalink.jar"
        exit 1
    fi
    echo "Lavalink.jar downloaded successfully."
fi

# Check if application.yml exists
if [ ! -f "application.yml" ]; then
    echo "application.yml not found. Make sure you have the configuration file."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo "Starting Lavalink with 1GB memory..."
java -Xmx1G -jar Lavalink.jar

echo "Lavalink server has stopped." 