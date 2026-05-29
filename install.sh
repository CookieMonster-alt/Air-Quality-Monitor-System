#!/bin/bash

# =============================================================================
# AILO - AI Local Operator
# One-Click Setup & Deployment Script
# Architecture: Raspberry Pi 5 (ARM64)
# Internal Logging: English-only
# =============================================================================

set -e  # Exit immediately if a command exits with a non-zero status

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root (script location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}🚀 AILO Edge Ecosystem: Setup & Deployment${NC}"
echo -e "${BLUE}====================================================${NC}"

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
    echo -e "${YELLOW}⚠️  WARNING: This script is heavily optimized for ARM64 (Raspberry Pi 5).${NC}"
    echo -e "${YELLOW}   Detected: $ARCH. Continuing anyway...${NC}"
fi

# =============================================================================
# STEP 1: SYSTEM DEPENDENCIES
# =============================================================================
echo -e "\n${BLUE}[1/7] Checking/Installing system dependencies...${NC}"

if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt-get"
else
    echo -e "${RED}❌ ERROR: 'apt-get' not found. This script requires a Debian/Ubuntu based OS.${NC}"
    exit 1
fi

SYSTEM_PACKAGES=(
    "build-essential" "pkg-config"
    "libopenblas-dev" "liblapack-dev" "libgomp1"
    "libsqlite3-dev" "curl" "wget" "git" "htop" "jq"
)

for pkg in "${SYSTEM_PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $pkg "; then
        echo -e "   ✓ $pkg is already installed."
    else
        echo -e "   Installing $pkg..."
        sudo $PKG_MANAGER install -y "$pkg" 2>/dev/null || \
        echo -e "   ${YELLOW}⚠️  $pkg installation skipped or failed. Continuing...${NC}"
    fi
done
echo -e "${GREEN}   ✓ System dependencies ready${NC}"

# =============================================================================
# STEP 2: FOLDER STRUCTURE
# =============================================================================
echo -e "\n${BLUE}[2/7] Preparing secure folder structure...${NC}"
mkdir -p data/vector_db
mkdir -p data/memory
mkdir -p models/llm
mkdir -p models/embedder
mkdir -p scripts
mkdir -p src
echo -e "${GREEN}   ✓ Core directories verified${NC}"

# =============================================================================
# STEP 3: VIRTUAL ENVIRONMENT
# =============================================================================
echo -e "\n${BLUE}[3/7] Initializing Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "   Created new virtual environment."
fi
source venv/bin/activate
pip install --upgrade pip --quiet
echo -e "${GREEN}   ✓ Virtual environment active${NC}"

# =============================================================================
# STEP 4: PYTHON DEPENDENCIES
# =============================================================================
echo -e "\n${BLUE}[4/7] Installing Python packages from requirements.txt...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ ERROR: requirements.txt not found! Please create it before running setup.${NC}"
    exit 1
fi

# Multi-tier installation for better cache management and stability on ARM
pip install --quiet numpy scipy pandas scikit-learn || { echo -e "${RED}❌ Tier 1 Failed${NC}"; exit 1; }
pip install --quiet llama-cpp-python sentence-transformers || { echo -e "${RED}❌ Tier 2 Failed${NC}"; exit 1; }
pip install --quiet chromadb || { echo -e "${RED}❌ Tier 3 Failed${NC}"; exit 1; }
pip install --quiet prompt-toolkit jinja2 pyyaml rich || { echo -e "${RED}❌ Tier 4 Failed${NC}"; exit 1; }
pip install --quiet -r requirements.txt || echo -e "${YELLOW}⚠️  Some minor requirements might need manual checks.${NC}"
echo -e "${GREEN}   ✓ Python dependencies securely installed${NC}"

# =============================================================================
# STEP 5: STRICT DATABASE SEEDING
# =============================================================================
echo -e "\n${BLUE}[5/7] Seeding strictly defined SQLite database...${NC}"
if [ -f "scripts/seed_db.py" ]; then
    python scripts/seed_db.py
    echo -e "${GREEN}   ✓ Database seeded via scripts/seed_db.py${NC}"
else
    echo -e "${RED}❌ CRITICAL ERROR: scripts/seed_db.py not found!${NC}"
    echo -e "${RED}   AILO requires its specific 'air_quality' schema (with NOCASE collation) to function.${NC}"
    echo -e "${RED}   Fallback database creation is disabled to prevent schema corruption. Halting.${NC}"
    exit 1
fi

# =============================================================================
# STEP 6: CHROMADB INITIALIZATION
# =============================================================================
echo -e "\n${BLUE}[6/7] Initializing ChromaDB vector space...${NC}"
python - << 'PYTHON_EOF'
from pathlib import Path
import chromadb
from chromadb.config import Settings

try:
    client = chromadb.PersistentClient(path="data/vector_db", settings=Settings(anonymized_telemetry=False))
    client.get_or_create_collection(name="ailo_intents", metadata={"hnsw:space": "cosine"})
    print("   ✓ ChromaDB initialized successfully with 'ailo_intents' collection.")
except Exception as e:
    print(f"   ⚠️  Warning: Initial vector db creation skipped. Will initialize on runtime. ({e})")
PYTHON_EOF

# =============================================================================
# STEP 7: MODEL DOWNLOADS
# =============================================================================
echo -e "\n${BLUE}[7/7] Verifying Edge AI Models...${NC}"

# Embedder Download
if [ -f "scripts/download_embedder.py" ]; then
    python scripts/download_embedder.py
else
    echo -e "${YELLOW}   ⚠️  scripts/download_embedder.py missing. You may need to download 'all-MiniLM-L6-v2' manually.${NC}"
fi

# Qwen LLM Check
if [ -d "models/llm" ] && [ "$(ls -A models/llm 2>/dev/null | grep -i gguf)" ]; then
    echo -e "${GREEN}   ✓ Local LLM (.gguf) found in models/llm/${NC}"
else
    echo -e "${YELLOW}   ⚠️  LLM (.gguf) model NOT found in models/llm/.${NC}"
    echo -e "${YELLOW}   Please manually drop the Qwen GGUF file into the models/llm/ directory.${NC}"
fi

# =============================================================================
# FINAL VERIFICATION PROTOCOL
# =============================================================================
echo -e "\n${BLUE}====================================================${NC}"
echo -e "${BLUE}🔍 POST-INSTALLATION SYSTEM VERIFICATION${NC}"
echo -e "${BLUE}====================================================${NC}"

python - << 'PYTHON_EOF'
import sys
import sqlite3

checks = []

# 1. Database Check
try:
    db = sqlite3.connect("data/ailo_db.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM air_quality")
    checks.append(("SQLite Data", True, f"air_quality table exists"))
    db.close()
except Exception as e:
    checks.append(("SQLite Data", False, str(e)))

# 2. Rich Library Check
try:
    import rich
    checks.append(("Rich UI Logic", True, "Successfully imported"))
except Exception as e:
    checks.append(("Rich UI Logic", False, str(e)))

# 3. Vector DB Check
try:
    import chromadb
    checks.append(("ChromaDB", True, "Successfully imported"))
except Exception as e:
    checks.append(("ChromaDB", False, str(e)))

all_pass = True
for name, passed, detail in checks:
    status = f"{chr(0x2713)} PASS" if passed else f"{chr(0x2717)} FAIL"
    color = "\033[0;32m" if passed else "\033[0;31m"
    print(f"   {color}{status}\033[0m {name}: {detail}")
    if not passed: all_pass = False

if not all_pass: sys.exit(1)
PYTHON_EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}🎉 AILO ECOSYSTEM DEPLOYED SUCCESSFULLY!${NC}"
    echo -e "   To start the engine, run:"
    echo -e "   ${YELLOW}source venv/bin/activate && python ailo_engine.py${NC}"
else
    echo -e "\n${RED}⚠️  DEPLOYMENT COMPLETED WITH WARNINGS. Please check the logs above.${NC}"
fi
echo -e "${BLUE}====================================================${NC}"