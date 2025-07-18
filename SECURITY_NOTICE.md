# 🚨 SECURITY NOTICE 🚨

## API Key Exposure Incident

**Date**: July 18, 2025  
**Status**: RESOLVED - Environment variables implemented

### What Happened
- OpenRouter API key was accidentally hardcoded in scripts
- Key was exposed in git commits: `suggest_clip.py` and `romanize_subtitles.py`
- Exposed key: `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`

### Actions Taken
✅ Moved API keys to `.env` file  
✅ Updated scripts to use `python-dotenv`  
✅ Enhanced `.gitignore` to prevent future exposure  
✅ Committed security fixes  

### CRITICAL ACTIONS REQUIRED
🔴 **IMMEDIATELY REVOKE** the exposed API key on OpenRouter dashboard  
🔴 **GENERATE NEW** API key  
🔴 **UPDATE** `.env` file with new key  

### Prevention Measures
- All API keys now in `.env` file (gitignored)
- Scripts validate environment variables on startup
- Enhanced `.gitignore` for sensitive files

### Files Affected
- `scripts/suggest_clip.py` - ✅ Fixed
- `scripts/romanize_subtitles.py` - ✅ Fixed
- `.env` - ✅ Created (contains old key - needs update)
- `.gitignore` - ✅ Enhanced

---
**Next Steps**: Revoke old key → Generate new key → Update .env → Test scripts
