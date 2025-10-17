#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Eranos Project Cleanup Script ===${NC}\n"

# Counter for deleted items
deleted_count=0

# Function to safely remove items
safe_remove() {
    if [ -e "$1" ]; then
        rm -rf "$1"
        echo -e "${GREEN}✓ Removed:${NC} $1"
        ((deleted_count++))
    fi
}

echo -e "${YELLOW}Cleaning node_modules...${NC}"
find . -name "node_modules" -type d -prune -exec rm -rf '{}' + 2>/dev/null
echo -e "${GREEN}✓ Removed all node_modules${NC}\n"

echo -e "${YELLOW}Cleaning Python cache files...${NC}"
find . -type d -name "__pycache__" -exec rm -rf '{}' + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf '{}' + 2>/dev/null
echo -e "${GREEN}✓ Removed Python cache files${NC}\n"

echo -e "${YELLOW}Cleaning build artifacts...${NC}"
find . -type d -name "dist" -exec rm -rf '{}' + 2>/dev/null
find . -type d -name "build" -exec rm -rf '{}' + 2>/dev/null
find . -type d -name ".next" -exec rm -rf '{}' + 2>/dev/null
find . -type d -name ".turbo" -exec rm -rf '{}' + 2>/dev/null
echo -e "${GREEN}✓ Removed build artifacts${NC}\n"

echo -e "${YELLOW}Cleaning lock files (keeping root package-lock.json)...${NC}"
find ./frontend/packages -name "package-lock.json" -type f -delete 2>/dev/null
find . -name "yarn.lock" -type f -delete 2>/dev/null
echo -e "${GREEN}✓ Cleaned lock files${NC}\n"

echo -e "${YELLOW}Cleaning log files...${NC}"
find . -type f -name "*.log" -delete 2>/dev/null
find . -type f -name "npm-debug.log*" -delete 2>/dev/null
echo -e "${GREEN}✓ Removed log files${NC}\n"

echo -e "${YELLOW}Cleaning coverage and test files...${NC}"
find . -type d -name "coverage" -exec rm -rf '{}' + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf '{}' + 2>/dev/null
find . -type d -name ".coverage" -exec rm -rf '{}' + 2>/dev/null
echo -e "${GREEN}✓ Removed test artifacts${NC}\n"

echo -e "${YELLOW}Cleaning backup files...${NC}"
find . -type f -name "*.backup" -delete 2>/dev/null
find . -type f -name "*.bak" -delete 2>/dev/null
find . -type f -name "*~" -delete 2>/dev/null
echo -e "${GREEN}✓ Removed backup files${NC}\n"

echo -e "${YELLOW}Cleaning OS-specific files...${NC}"
find . -type f -name ".DS_Store" -delete 2>/dev/null
find . -type f -name "Thumbs.db" -delete 2>/dev/null
find . -type f -name "desktop.ini" -delete 2>/dev/null
echo -e "${GREEN}✓ Removed OS files${NC}\n"

echo -e "${YELLOW}Cleaning IDE files...${NC}"
safe_remove ".vscode"
safe_remove ".idea"
find . -type f -name "*.swp" -delete 2>/dev/null
find . -type f -name "*.swo" -delete 2>/dev/null
echo -e "${GREEN}✓ Removed IDE files${NC}\n"

echo -e "${YELLOW}Cleaning temporary files...${NC}"
find . -type d -name "tmp" -exec rm -rf '{}' + 2>/dev/null
find . -type d -name "temp" -exec rm -rf '{}' + 2>/dev/null
find . -type f -name "*.tmp" -delete 2>/dev/null
echo -e "${GREEN}✓ Removed temporary files${NC}\n"

echo -e "${GREEN}=== Cleanup Complete! ===${NC}\n"
echo -e "Run ${YELLOW}npm install${NC} in frontend directories to restore node_modules"
echo -e "Virtual environments (.venv) were preserved"
