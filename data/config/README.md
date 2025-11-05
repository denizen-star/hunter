# Skill Normalization Configuration

## ⚠️ IMPORTANT: Manual Edits

The `skill_normalization.yaml` file **CAN be edited manually**, but be aware:

### 🔴 DANGER: Import Script Overwrites Manual Edits

The `scripts/import_skills_to_taxonomy.py` script will **OVERWRITE** any manual changes you make to this file!

**Before re-running the import script:**
1. Make sure you've saved your manual edits
2. Consider creating a backup first
3. Or add your manual edits to the source files instead

### 📝 Where to Add Manual Edits

If you want your changes to persist, add them to:

1. **For acronyms/word replacements**: Add to `fuzzy_rules.word_replacements` in the YAML file
2. **For new skills**: Add to `app/utils/simple_tech_extractor.py` TECHNOLOGIES dict
3. **For aliases**: Add to `data/resumes/skills.yaml` variations_found lists

### 🎯 Quick Fix: Add Acronyms Here

Instead of manually adding to the generated file, you can add them to this README first:

```yaml
# Acronyms to add:
- ai → artificial intelligence
- aws → amazon web services
- bi → business intelligence
```

Then we can create a merge script to preserve your manual edits.

---

**Last updated:** 2025-11-01  
**File size:** ~86KB  
**Skills:** 499  
**Aliases:** 325




