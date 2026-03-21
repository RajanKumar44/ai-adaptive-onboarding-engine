#!/bin/bash
# PHASE 2 Verification Script
# Verifies that all PHASE 2 components are properly set up

echo "=================================================="
echo "PHASE 2: DATABASE & PERSISTENCE - VERIFICATION"
echo "=================================================="
echo ""

PASSED=0
FAILED=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Checking PHASE 2 implementation..."
echo ""

# Check 1: Models exist
echo -n "✓ User model with audit fields... "
if grep -q "AuditedBase" backend/app/models/user.py; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 2: Analysis model
echo -n "✓ Analysis model with audit fields... "
if grep -q "AuditedBase" backend/app/models/analysis.py; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 3: Audit log model exists
echo -n "✓ AuditLog model... "
if [ -f "backend/app/models/audit_log.py" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 4: Base model with AuditedBase mixin
echo -n "✓ AuditedBase mixin... "
if [ -f "backend/app/models/base.py" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 5: Audit service
echo -n "✓ Audit logging service... "
if [ -f "backend/app/services/audit_service.py" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 6: Backup script
echo -n "✓ Database backup script... "
if [ -f "backend/scripts/backup.sh" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 7: Restore script
echo -n "✓ Database restore script... "
if [ -f "backend/scripts/restore.sh" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 8: db_utils script
echo -n "✓ Database utilities script... "
if [ -f "backend/scripts/db_utils.py" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 9: Dockerfile exists
echo -n "✓ Dockerfile... "
if [ -f "backend/Dockerfile" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 10: Docker-compose exists
echo -n "✓ Docker-compose.yml... "
if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 11: Entrypoint script
echo -n "✓ Entrypoint script... "
if [ -f "backend/entrypoint.sh" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 12: Init database script
echo -n "✓ Database init script... "
if [ -f "backend/scripts/init-db.sql" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 13: Requirements updated with Alembic
echo -n "✓ Requirements include Alembic... "
if grep -q "alembic" backend/requirements.txt; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 14: Documentation
echo -n "✓ Phase 2 documentation... "
if [ -f "PHASE_2_DATABASE.md" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 15: Docker quickstart
echo -n "✓ Docker quickstart guide... "
if [ -f "DOCKER_QUICKSTART.md" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 16: Docker setup guide
echo -n "✓ Docker setup guide... "
if [ -f "DOCKER_SETUP.md" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 17: Completion summary
echo -n "✓ Phase 2 completion summary... "
if [ -f "PHASE_2_COMPLETION_SUMMARY.md" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Check 18: Database indexes
echo -n "✓ Database indexes configured... "
if grep -q "Index(" backend/app/models/user.py && grep -q "Index(" backend/app/models/analysis.py; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

echo ""
echo "=================================================="
echo "Results: ${GREEN}${PASSED} PASSED${NC} / ${RED}${FAILED} FAILED${NC}"
echo "=================================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All PHASE 2 components verified!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
    echo "2. Run: docker-compose up -d"
    echo "3. Access: http://localhost:8000/docs"
    echo ""
    echo "For detailed info, see PHASE_2_COMPLETION_SUMMARY.md"
    exit 0
else
    echo -e "${RED}✗ Some components are missing!${NC}"
    exit 1
fi
