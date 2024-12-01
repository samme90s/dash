#!/bin/bash

# Define color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Centralized variables for repeated strings
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
ERROR_PREFIX="Error:"
WARNING_PREFIX="Warning:"

# Custom echo function to handle colored output
echo_color() {
    local COLOR=$1
    shift
    echo -e "${COLOR}$@${NC}"
}

# Function to handle errors and stop the script
handle_error() {
    echo_color $RED "$ERROR_PREFIX $1"
    return 1 # Stop the script without exiting the terminal
}

# Function to check if a command exists
check_command() {
    local CMD=$1
    local ERROR_MSG=$2

    if ! command -v "$CMD" &>/dev/null; then
        handle_error "$ERROR_MSG"
    fi
}

# Step 1: Deactivate any existing virtual environment
echo_color $CYAN "Step 1: Deactivate any existing virtual environment"

if [ -n "$VIRTUAL_ENV" ]; then
    deactivate &&
        echo_color $GREEN "Deactivated existing virtual environment." ||
        handle_error "Failed to deactivate the virtual environment."
else
    echo_color $YELLOW "No active virtual environment found."
fi

# Step 2: Remove existing virtual environment (if any)
echo_color $CYAN "\nStep 2: Remove existing virtual environment (if any)"

if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR" &&
        echo_color $GREEN "Existing virtual environment removed." ||
        handle_error "Failed to remove the existing virtual environment."
else
    echo_color $YELLOW "No existing virtual environment found."
fi

# Step 3: Check Python and pip versions
echo_color $CYAN "\nStep 3: Check Python and pip versions"

check_command "python3" \
    "Python3 is not installed. Please install it and try again."

PYTHON_VERSION=$(python3 --version)
echo_color $GREEN "Python version: $PYTHON_VERSION"

if ! python3 -m pip --version &>/dev/null; then
    handle_error "pip is not installed. Please install it with your package manager."
else
    PIP_VERSION=$(python3 -m pip --version)
    echo_color $GREEN "pip version: $PIP_VERSION"
fi

# Step 4: Create a new virtual environment
echo_color $CYAN "\nStep 4: Create a new virtual environment"

if ! python3 -m venv "$VENV_DIR"; then
    handle_error "Failed to create the virtual environment."
else
    echo_color $GREEN "Virtual environment created at $VENV_DIR."
fi

# Step 5: Activate the virtual environment
echo_color $CYAN "\nStep 5: Activate the virtual environment"

if ! source "$VENV_DIR/bin/activate"; then
    handle_error "Failed to activate the virtual environment."
else
    echo_color $GREEN "Virtual environment activated."
fi

# Step 6: Upgrade pip inside the virtual environment
echo_color $CYAN "\nStep 6: Upgrade pip inside the virtual environment"

if ! python3 -m pip install --upgrade pip; then
    handle_error "Failed to upgrade pip in the virtual environment."
else
    echo_color $GREEN "pip upgraded successfully."
fi

# Step 7: Install dependencies from requirements-dev.txt
echo_color $CYAN "\nStep 7: Install dependencies from ${REQUIREMENTS_FILE}"

if [ -f "$REQUIREMENTS_FILE" ]; then
    if ! pip install -r "$REQUIREMENTS_FILE"; then
        handle_error \
            "Failed to install dependencies from ${REQUIREMENTS_FILE}."
    else
        echo_color $GREEN "Dependencies installed successfully."
    fi
else
    echo_color $YELLOW \
        "$WARNING_PREFIX ${REQUIREMENTS_FILE} not found. Skipping dependency installation."
fi

# Final step: Setup complete message
echo_color $CYAN "\nSetup Complete"
