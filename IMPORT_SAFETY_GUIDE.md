# Import Safety Guide

## 🎯 Core Principle

**The YAML taxonomy file is a MANUAL CONFIG file, not an auto-generated file.**

## ✅ How It Works Now

### Normal Usage (Recommended)
```bash
# Edit the file directly
vim data/config/skill_normalization.yaml
```

The YAML file is now protected from accidental overwrites.

### When You Need to Refresh
```bash
# Step 1: Read the warning
python3 scripts/import_skills_to_taxonomy.py

# Step 2: If you really want to overwrite, set the flag
export FORCE_IMPORT=1
python3 scripts/import_skills_to_taxonomy.py

# Step 3: Turn off the flag
unset FORCE_IMPORT
```

The script will:
1. ✅ Warn you that it will overwrite
2. ✅ Create an automatic backup
3. ✅ Then proceed (ONLY if FORCE_IMPORT=1)

## 🔐 Safety Features Added

1. **Automatic backups** before overwriting
2. **Warning prompt** if file exists
3. **Force flag required** to proceed
4. **Manual edits are safe** by default

## 📝 Workflow Recommendation

### Day-to-Day Usage
```bash
# Just edit the YAML file
code data/config/skill_normalization.yaml
```

Add:
- New skills
- Aliases
- Acronyms to fuzzy_rules
- Category changes

### Monthly Refresh (Optional)
```bash
# If you want to pull in new skills from source files
export FORCE_IMPORT=1
python3 scripts/import_skills_to_taxonomy.py
unset FORCE_IMPORT

# Then manually review and merge any changes
```

## 🚫 What Won't Happen Again

❌ Script won't silently overwrite your manual edits  
❌ You won't lose 2 hours of work  
❌ No accidental deletions  

## ✅ What Will Happen

✅ Script warns you before overwriting  
✅ Automatic backups are created  
✅ Manual edits are protected  
✅ You control when imports happen  

---

**Bottom Line:** The taxonomy YAML is YOUR file. Edit it freely. The import script is now a helper tool, not a replacement.




