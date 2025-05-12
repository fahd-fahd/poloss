@echo off
echo Starting Lavalink server...

rem Check if Java is installed
java -version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Java is not installed or not in PATH. Lavalink requires Java 11 or higher.
    echo Please install Java from https://adoptium.net/
    pause
    exit /b 1
)

rem Check if Lavalink.jar exists
if not exist Lavalink.jar (
    echo Lavalink.jar not found. Downloading Lavalink...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/lavalink-devs/Lavalink/releases/download/3.7.9/Lavalink.jar' -OutFile 'Lavalink.jar'"
    
    if not exist Lavalink.jar (
        echo Failed to download Lavalink.jar
        pause
        exit /b 1
    )
    echo Lavalink.jar downloaded successfully.
)

rem Check if application.yml exists
if not exist application.yml (
    echo application.yml not found. Make sure you have the configuration file.
    pause
    exit /b 1
)

echo Starting Lavalink with 1GB memory...
java -Xmx1G -jar Lavalink.jar

pause 