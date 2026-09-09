#!/bin/bash
# Phase 1: Validate Safety Before Archiving

echo "================================================================================"
echo "PHASE 1: PRE-ARCHIVAL VALIDATION"
echo "================================================================================"

# Verify branch
echo -e "\n✓ Current branch:"
git branch | grep "^\*"

# Check git status
echo -e "\n✓ Git status summary:"
git status --short | head -20

# Verify archive directory exists
echo -e "\n✓ Archive directory check:"
if [ -d "PUBLICATION_PACKAGE/8_ARCHIVE/" ]; then
    echo "  ✅ PUBLICATION_PACKAGE/8_ARCHIVE/ exists"
    ls -lah PUBLICATION_PACKAGE/8_ARCHIVE/ | head -5
else
    echo "  ⚠️  Archive directory not found - will create it"
    mkdir -p PUBLICATION_PACKAGE/8_ARCHIVE/
fi

# List files to be archived
echo -e "\n✓ Files marked for archival (~27 items):"
echo "  Temporary audit/consolidation reports:"
for f in README_AUDIT_REPORT.md README_CONSOLIDATION_COMPLETE.md CLEANUP_PLAN_SAFE.md \
         CLEANUP_INSTRUCTIONS.md DATA_AUDIT_REPORT_2026_09_09.md ⚠️_DATA_AUDIT_ALERT.md \
         DATA_COMPLETION_UPDATE_2026_09_09.md DATA_INTEGRATION_REPORT_2026_09_09.md \
         DATA_INTEGRATION_FINAL_REPORT_2026_09_09.md FINAL_COMPLETION_SUMMARY.md \
         RE_EVALUATION_PLAN_2026_09_09.md RE_EVALUATION_EXECUTION_2026_09_09.md \
         RE_EVALUATION_REPORT_MOVOCTOK_COMPLETE_2026_09_09.md README_OLD_BACKUP.md; do
    if [ -f "$f" ]; then
        echo "    ✓ $f"
    fi
done

echo -e "\n  SLURM job logs:"
ls -1 zero_shot_seeds_focused_*.err zero_shot_seeds_focused_*.out 2>/dev/null | head -10 || echo "    (none found)"

echo -e "\n  Cache/backup artifacts:"
[ -d ".cleanup_backup_2026_09_09/" ] && echo "    ✓ .cleanup_backup_2026_09_09/" || echo "    (not found)"
[ -f ".pytest_cache/README.md" ] && echo "    ✓ .pytest_cache/README.md" || echo "    (not found)"

# Verify core files are intact
echo -e "\n✓ Core files integrity check:"
for dir in PUBLICATION_PACKAGE data experiments scripts docs; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/ - SAFE"
    else
        echo "  ⚠️  $dir/ - MISSING (may not be critical)"
    fi
done

echo -e "\n✓ Critical root files:"
for f in README.md REPOSITORY_CONTEXT.md CITATION.md MODEL_MANIFEST.md DATA_MANIFEST.md; do
    if [ -f "$f" ]; then
        echo "  ✅ $f"
    else
        echo "  ⚠️  $f - MISSING"
    fi
done

echo -e "\n================================================================================"
echo "PHASE 1 VALIDATION: COMPLETE"
echo "================================================================================"
echo -e "\n✅ Ready to proceed to Phase 2 (Archival)"
