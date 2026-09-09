#!/bin/bash

################################################################################
# REPOSITORY CLEANUP SCRIPT
# Purpose: Remove obsolete documentation, old reports, and temporary files
# Safety: Preserves running tasks and publication materials
# Date: 2026-09-09
################################################################################

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="${REPO_ROOT}/.cleanup_backup_2026_09_09"
DELETED_LOG="${REPO_ROOT}/.cleanup_log_2026_09_09.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Repository Cleanup Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo -e "${YELLOW}Creating backup directory: $BACKUP_DIR${NC}"

# Track deleted files
touch "$DELETED_LOG"
echo "Cleanup Log - $(date)" > "$DELETED_LOG"
echo "Repository: $REPO_ROOT" >> "$DELETED_LOG"
echo "" >> "$DELETED_LOG"

# Function to backup and remove files
backup_and_remove() {
    local file="$1"
    local description="$2"

    if [ -f "$file" ]; then
        echo -e "${YELLOW}Removing:${NC} $file ($description)"
        cp "$file" "$BACKUP_DIR/$(basename "$file")" 2>/dev/null || true
        rm "$file"
        echo "Removed: $file - $description" >> "$DELETED_LOG"
    fi
}

# Function to backup and remove directories
backup_and_remove_dir() {
    local dir="$1"
    local description="$2"

    if [ -d "$dir" ]; then
        echo -e "${YELLOW}Removing directory:${NC} $dir ($description)"
        cp -r "$dir" "$BACKUP_DIR/$(basename "$dir")" 2>/dev/null || true
        rm -rf "$dir"
        echo "Removed directory: $dir - $description" >> "$DELETED_LOG"
    fi
}

# Function to remove by pattern
remove_by_pattern() {
    local pattern="$1"
    local description="$2"

    echo -e "${YELLOW}Searching for pattern:${NC} $pattern ($description)"
    find "$REPO_ROOT" -maxdepth 1 -type f -name "$pattern" | while read file; do
        if [ -f "$file" ]; then
            echo -e "  → Removing: $(basename "$file")"
            cp "$file" "$BACKUP_DIR/$(basename "$file")" 2>/dev/null || true
            rm "$file"
            echo "Removed: $file - $description" >> "$DELETED_LOG"
        fi
    done
}

echo -e "${GREEN}Stage 1: Removing Old Audit Reports${NC}"
backup_and_remove_dir "$REPO_ROOT/AUDIT_COMPLETION_SUMMARY.md" "Audit report"
remove_by_pattern "AUDIT_*.md" "Audit reports"

echo ""
echo -e "${GREEN}Stage 2: Removing Old Phase Reports${NC}"
remove_by_pattern "PHASE_*.md" "Phase reports"
remove_by_pattern "PHASE_*.txt" "Phase status files"

echo ""
echo -e "${GREEN}Stage 3: Removing GitHub Migration Guides${NC}"
remove_by_pattern "GITHUB_*.md" "GitHub guides"

echo ""
echo -e "${GREEN}Stage 4: Removing Pre-Push Reports${NC}"
remove_by_pattern "PRE_PUSH_*.md" "Pre-push reports"

echo ""
echo -e "${GREEN}Stage 5: Removing Redaction Reports${NC}"
remove_by_pattern "REDACTION_*.md" "Redaction documentation"

echo ""
echo -e "${GREEN}Stage 6: Removing Consistency Check Files${NC}"
backup_and_remove "$REPO_ROOT/CONSISTENCY_CHECK_vs_MoVoC_v2.md" "Consistency check"

echo ""
echo -e "${GREEN}Stage 7: Removing Storage Inventory Files${NC}"
remove_by_pattern "FILE_STORAGE_*.md" "Storage inventory"
remove_by_pattern "STORAGE_INVENTORY.md" "Storage inventory"

echo ""
echo -e "${GREEN}Stage 8: Removing Old Final Reports${NC}"
backup_and_remove "$REPO_ROOT/FINAL_PUBLICATION_DECISION.md" "Old publication decision"
backup_and_remove "$REPO_ROOT/FINAL_PUBLICATION_READINESS_REPORT.md" "Old readiness report"
backup_and_remove "$REPO_ROOT/FINAL_PUBLICATION_STRUCTURE.md" "Old structure report"
backup_and_remove "$REPO_ROOT/FINAL_PUBLISH_CHECKLIST.md" "Old checklist"
backup_and_remove "$REPO_ROOT/FINAL_STRUCTURE_REPORT.md" "Old structure report"
backup_and_remove "$REPO_ROOT/FINAL_REPOSITORY_TREE.txt" "Old repository tree"
backup_and_remove "$REPO_ROOT/FINAL_VERIFICATION_REPORT.md" "Old verification report"

echo ""
echo -e "${GREEN}Stage 9: Removing Old Publication Readiness Reports${NC}"
backup_and_remove "$REPO_ROOT/PUBLICATION_READY_REPORT.md" "Old readiness report"

echo ""
echo -e "${GREEN}Stage 10: Removing Old Index Files${NC}"
backup_and_remove "$REPO_ROOT/INDEX_GITHUB_PUBLICATION.md" "Old GitHub index"
backup_and_remove "$REPO_ROOT/INDEX_OF_REDACTION_REPORTS.md" "Old redaction index"

echo ""
echo -e "${GREEN}Stage 11: Removing Obsolete Corrections${NC}"
backup_and_remove "$REPO_ROOT/CORRECTED_PRE_PUSH_RECONCILIATION.md" "Obsolete correction"

echo ""
echo -e "${GREEN}Stage 12: Removing Obsolete Documentation${NC}"
backup_and_remove "$REPO_ROOT/CLEAN_FILE_PATHS.md" "Obsolete file paths"
backup_and_remove "$REPO_ROOT/README_INDEPENDENT.md" "Old independent repo doc"
backup_and_remove "$REPO_ROOT/QUICK_PUSH_GUIDE.md" "Old push guide"

echo ""
echo -e "${GREEN}Stage 13: Removing Old Scripts${NC}"
backup_and_remove "$REPO_ROOT/EXECUTE_PUSH.sh" "Old push execution script"

echo ""
echo -e "${GREEN}Stage 14: Removing Build Logs${NC}"
remove_by_pattern "FILES_CREATED_*.md" "Build logs"

echo ""
echo -e "${GREEN}Stage 15: Removing Old Inventories${NC}"
backup_and_remove "$REPO_ROOT/PUBLICATION_PACKAGE_INVENTORY.md" "Old package inventory"

echo ""
echo -e "${GREEN}Stage 16: Removing Incomplete Scripts${NC}"
backup_and_remove "$REPO_ROOT/migrate_experiments.sh" "Incomplete migration script"
backup_and_remove "$REPO_ROOT/upload_models_to_hf.sh" "Incomplete upload script"

echo ""
echo -e "${GREEN}Stage 17: Removing Old Results Summaries${NC}"
backup_and_remove "$REPO_ROOT/COMPLETE_RESULTS_SUMMARY.md" "Old results summary"

echo ""
echo -e "${GREEN}Stage 18: Removing Other Obsolete Files${NC}"
backup_and_remove "$REPO_ROOT/PUBLICATION_SUMMARY.md" "Old publication summary"
backup_and_remove "$REPO_ROOT/MANIFEST_PUBLICATION_CHECKLIST.md" "Old manifest checklist"
backup_and_remove "$REPO_ROOT/EXPERIMENT_PATHS_ANALYSIS.md" "Old experiment paths"
backup_and_remove "$REPO_ROOT/COMMIT_MESSAGE_NO_AI.txt" "Obsolete commit message"
backup_and_remove "$REPO_ROOT/PUBLICATION_PACKAGE/RECONSTRUCTION_V2_README.md" "Old reconstruction doc"

echo ""
echo -e "${GREEN}Stage 19: Cleaning Python Cache${NC}"
find "$REPO_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -type f -name "*.pyc" -delete
find "$REPO_ROOT" -type f -name "*.pyo" -delete
echo "Cleaned Python cache" >> "$DELETED_LOG"

echo ""
echo -e "${GREEN}Stage 20: Cleaning Temporary Files${NC}"
find "$REPO_ROOT" -maxdepth 1 -type f \( -name "*.swp" -o -name "*.swo" -o -name "*~" -o -name "*.bak" \) -delete 2>/dev/null || true
echo "Cleaned temporary files" >> "$DELETED_LOG"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Summary
echo -e "${YELLOW}Summary:${NC}"
echo "  Backup location: $BACKUP_DIR"
echo "  Cleanup log: $DELETED_LOG"
echo ""
echo -e "${GREEN}Preserved files:${NC}"
echo "  ✅ README.md - Main documentation"
echo "  ✅ CITATION.md - Citation info"
echo "  ✅ requirements.txt - Dependencies"
echo "  ✅ MODEL_MANIFEST.md - Model inventory"
echo "  ✅ DATA_MANIFEST.md - Data inventory"
echo "  ✅ DOCUMENTATION_UPDATE_2026_09_09.md - Update record"
echo "  ✅ experiments/ - All training results"
echo "  ✅ PUBLICATION_PACKAGE/ - Publication materials"
echo "  ✅ docs/ - Documentation"
echo "  ✅ slurm/ - Active job scripts"
echo "  ✅ scripts/ - Training/evaluation scripts"
echo "  ✅ data/ - Training data"
echo ""

# Count remaining files
echo -e "${YELLOW}Repository Statistics:${NC}"
echo -n "  Total markdown files: "
find "$REPO_ROOT" -maxdepth 1 -type f -name "*.md" | wc -l
echo -n "  Total shell scripts: "
find "$REPO_ROOT" -maxdepth 1 -type f -name "*.sh" | wc -l
echo -n "  Total text files: "
find "$REPO_ROOT" -maxdepth 1 -type f -name "*.txt" | wc -l

echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Review cleanup log: $DELETED_LOG"
echo "  2. Review backup: $BACKUP_DIR"
echo "  3. Run: git status  (to verify no critical files removed)"
echo "  4. Run: git add -A  (to stage cleanup)"
echo "  5. Run: git commit -m 'Clean: Remove obsolete documentation and temp files'"
echo ""

echo -e "${GREEN}✅ Cleanup script completed successfully!${NC}"
