#!/usr/bin/env bash

# cleanup_old_files.sh
# This script removes old/conflicting files from the eranos-project restructuring
# Run from the project root: bash cleanup_old_files.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Eranos Project Cleanup Script ===${NC}"
echo -e "${YELLOW}This will remove old/conflicting files for security restructuring${NC}"
echo ""

# Confirm before proceeding
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Aborted."
    exit 1
fi

# Track what's deleted
DELETED_COUNT=0

# Function to safely remove file/directory
safe_remove() {
    local path=$1
    if [ -e "$path" ]; then
        echo -e "${YELLOW}Removing: $path${NC}"
        rm -rf "$path"
        ((DELETED_COUNT++))
    fi
}

echo ""
echo -e "${GREEN}=== Phase 1: Old Database Files ===${NC}"
# Remove old SQLite database
safe_remove "backend/erano.db"
safe_remove "backend/erano.db-shm"
safe_remove "backend/erano.db-wal"

echo ""
echo -e "${GREEN}=== Phase 2: Duplicate/Old Model Files ===${NC}"
# Remove old monolithic models file (we now use models/ directory)
safe_remove "backend/app/models.py"
safe_remove "backend/app/db_models.py"

# Remove old alembic directory if it exists (we use migrations/)
safe_remove "backend/alembic"

echo ""
echo -e "${GREEN}=== Phase 3: Old Database Configuration ===${NC}"
# Remove old db.py if app/core/database.py exists
if [ -f "backend/app/core/database.py" ]; then
    safe_remove "backend/app/db.py"
fi

echo ""
echo -e "${GREEN}=== Phase 4: Old Migration Files ===${NC}"
# Remove placeholder migration
safe_remove "backend/migrations/versions/5fbcca76a667_add_messages_table.py"

echo ""
echo -e "${GREEN}=== Phase 5: Old API Files ===${NC}"
# Remove old onboarding.py if it conflicts with new structure
if [ -f "backend/app/api/v1/onboarding.py" ]; then
    safe_remove "backend/app/api/onboarding.py"
fi

# Remove old messages.py if not using it
safe_remove "backend/app/api/messages.py"

echo ""
echo -e "${GREEN}=== Phase 6: Python Cache Files ===${NC}"
# Remove all __pycache__ directories
find backend/app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find backend/migrations -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
((DELETED_COUNT++))

# Remove .pyc files
find backend/app -name "*.pyc" -delete 2>/dev/null || true
find backend/migrations -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo -e "${GREEN}=== Phase 7: Old Config Files ===${NC}"
# Backup old .env if it exists
if [ -f "backend/.env" ] && [ -f "backend/.env.example" ]; then
    if ! cmp -s "backend/.env" "backend/.env.example"; then
        echo -e "${YELLOW}Backing up backend/.env to backend/.env.backup${NC}"
        cp "backend/.env" "backend/.env.backup"
    fi
fi

echo ""
echo -e "${GREEN}=== Phase 8: Temporary/Upload Files ===${NC}"
# Remove uploads directory (will be recreated)
safe_remove "backend/uploads"

# Remove SSL certificates (will be regenerated if needed)
safe_remove "backend/eranoconsulting.local+3-key.pem"
safe_remove "backend/eranoconsulting.local+3.pem"

echo ""
echo -e "${GREEN}=== Phase 9: Old Scripts ===${NC}"
# Remove old init script if exists
safe_remove "scripts/init_db.sql"

echo ""
echo -e "${GREEN}=== Phase 10: Checking for Conflicting Dependencies ===${NC}"
# Remove old crud directory if app/repositories exists
if [ -d "backend/app/repositories" ]; then
    safe_remove "backend/app/crud"
fi

# Remove old dependencies.py if app/core/deps.py exists
if [ -f "backend/app/core/deps.py" ]; then
    safe_remove "backend/app/dependencies.py"
fi

echo ""
echo -e "${GREEN}=== Cleanup Summary ===${NC}"
echo -e "Removed/cleaned: ${GREEN}${DELETED_COUNT}${NC} items"
echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Create the new model files in backend/app/models/"
echo "2. Update backend/.env with PostgreSQL connection"
echo "3. Install asyncpg: pip install asyncpg"
echo "4. Run: alembic revision --autogenerate -m 'Initial migration'"
echo "5. Run: alembic upgrade head"
echo ""
echo -e "${YELLOW}Note: A backup of your .env was created at backend/.env.backup${NC}"
