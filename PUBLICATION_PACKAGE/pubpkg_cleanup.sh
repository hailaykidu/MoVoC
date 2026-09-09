#!/bin/bash
set -e

echo "🧹 PUBLICATION_PACKAGE Cleanup for Paper Publication"
echo "===================================================="
echo ""

PUBPKG="/homes/neumann/teklehaymanot/marianmt-tokenizer-comparison/PUBLICATION_PACKAGE"
cd "$PUBPKG" || exit 1

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Phase 1: Dry Run
echo "${YELLOW}PHASE 1: DRY-RUN (Preview what will be deleted)${NC}"
echo "=================================================="
echo ""

echo "Files to be DELETED:"
echo "---"

FILES_TO_DELETE=(
    "5_RESULTS/TABLE_3_FINAL.md"
    "5_RESULTS/TABLE_3_FINAL_CLEAN.md"
    "5_RESULTS/TABLE_3_COMPLETE_WITH_ZEROSHOT.md"
    "5_RESULTS/TABLE_3_MULTISEED_CURRENT.md"
    "5_RESULTS/MASTER_STATUS_2026_09_09.md"
    "5_RESULTS/QUICK_STATUS_SUMMARY.md"
    "5_RESULTS/ZERO_SHOT_RESULTS.md"
)

TOTAL_SIZE=0
FILE_COUNT=0

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        echo "  ❌ $(basename "$file") ($SIZE)"
        ((FILE_COUNT++))
    fi
done

echo ""
echo "Files to be KEPT:"
echo "---"
echo "  ✅ TABLE_3_UPDATED_STATUS.md (main results)"
echo "  ✅ EVALUATION_FRAMEWORK_MOVOCTOK_ZEROSHOT.md (methods)"
echo "  ✅ MOVOCTOK_ZEROSHOT_ANALYSIS.md (analysis)"
echo "  ✅ 00_INDEX.md (index)"
echo "  ✅ README.md (guide)"
echo "  ✅ FINAL_STATUS_REPORT.md (status)"
echo "  ✅ validation_results/ (raw data - 34+ JSON files)"

echo ""
echo "${YELLOW}Total files to remove: $FILE_COUNT (~61 KB)${NC}"
echo ""

# Phase 2: User Confirmation
echo "${YELLOW}PHASE 2: Confirmation${NC}"
echo "====================="
read -p "Proceed with cleanup? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "${RED}❌ Cleanup cancelled${NC}"
    exit 0
fi

# Phase 3: Backup (Optional)
echo ""
echo "${YELLOW}PHASE 3: Creating Backup${NC}"
echo "========================="

mkdir -p .cleanup_backup_results
echo "Backing up files to .cleanup_backup_results/"

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" .cleanup_backup_results/
        echo "  📦 $(basename "$file")"
    fi
done

echo "${GREEN}✅ Backup complete${NC}"

# Phase 4: Execute Cleanup
echo ""
echo "${YELLOW}PHASE 4: Executing Cleanup${NC}"
echo "==========================="

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  🗑️  $(basename "$file") deleted"
    fi
done

echo "${GREEN}✅ Cleanup complete${NC}"

# Phase 5: Verification
echo ""
echo "${YELLOW}PHASE 5: Verification${NC}"
echo "====================="

echo ""
echo "Remaining 5_RESULTS/ markdown files:"
ls -lh 5_RESULTS/*.md 2>/dev/null | awk '{print "  ✅", $9, "(" $5 ")"}' | head -10

echo ""
echo "Validation data files:"
RESULT_COUNT=$(ls 5_RESULTS/validation_results/*.json 2>/dev/null | wc -l)
echo "  ✅ $RESULT_COUNT validation result files present"

if [ "$RESULT_COUNT" -ge 34 ]; then
    echo "${GREEN}✅ Verification passed - 34+ experiment results preserved${NC}"
else
    echo "${RED}❌ Warning: Expected 34+ result files, found $RESULT_COUNT${NC}"
fi

echo ""
echo "${GREEN}🎉 PUBLICATION_PACKAGE cleanup complete!${NC}"
echo ""
echo "Repository is now ready for paper publication:"
echo "  ✅ Non-essential files removed"
echo "  ✅ Essential results files preserved"
echo "  ✅ Raw validation data intact"
echo "  ✅ All code and documentation preserved"

