#!/usr/bin/env bash

# verify_structure.sh
# Verifies the project structure before cleanup
# Run from project root: bash verify_structure.sh

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Eranos Project Structure Verification ===${NC}"
echo ""

# Check if required directories exist
echo -e "${GREEN}Checking directory structure...${NC}"

check_dir() {
    if [ -d "$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 missing"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "  ${YELLOW}⚠${NC} $1 missing (will need to create)"
        return 1
    fi
}

# Check new structure
echo ""
echo "New Structure (should exist):"
check_dir "backend/app/core"
check_dir "backend/app/models"
check_dir "backend/app/api"
check_dir "backend/migrations"

echo ""
echo "Required files:"
check_file "backend/app/core/config.py"
check_file "backend/app/core/database.py"
check_file "backend/app/core/security.py"
check_file "backend/app/models/base.py"
check_file "backend/app/models/user.py"
check_file "backend/migrations/env.py"
check_file "backend/alembic.ini"

# Check for old/conflicting files
echo ""
echo -e "${YELLOW}Old/Conflicting files (will be removed):${NC}"

conflict_count=0

check_conflict() {
    if [ -e "$1" ]; then
        echo -e "  ${YELLOW}!${NC} $1 (WILL BE DELETED)"
        ((conflict_count++))
    fi
}

check_conflict "backend/app/models.py"
check_conflict "backend/app/db_models.py"
check_conflict "backend/app/db.py"
check_conflict "backend/alembic"
check_conflict "backend/erano.db"
check_conflict "backend/app/dependencies.py"
check_conflict "backend/app/crud"

echo ""
echo -e "${GREEN}=== Summary ===${NC}"
echo "Conflicting files found: ${YELLOW}${conflict_count}${NC}"

if [ $conflict_count -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Run cleanup_old_files.sh to remove these files${NC}"
else
    echo -e "${GREEN}No conflicts found!${NC}"
fi

echo ""
echo -e "${GREEN}=== Files that will be CREATED (not deleted) ===${NC}"
echo "These need to be created manually:"
[ ! -f "backend/app/models/__init__.py" ] && echo "  - backend/app/models/__init__.py"
[ ! -f "backend/app/models/refresh_token.py" ] && echo "  - backend/app/models/refresh_token.py"
[ ! -f "backend/app/models/message.py" ] && echo "  - backend/app/models/message.py"
[ ! -f "backend/app/models/uploaded_file.py" ] && echo "  - backend/app/models/uploaded_file.py"
[ ! -f "backend/app/models/client.py" ] && echo "  - backend/app/models/client.py"
