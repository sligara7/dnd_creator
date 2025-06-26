# Technical Issues Log - D&D Character Creator
**Session**: June 26, 2025 - LLM Integration Fix

## 🔧 TECHNICAL ISSUES DISCOVERED & STATUS

### 1. ASYNC/AWAIT METHOD MIGRATION ✅ FIXED
**Issue**: All LLM service calls were using sync `llm_service.generate()` 
**Error**: `'OllamaLLMService' object has no attribute 'generate'`
**Fix Applied**: 
- Updated all methods in `generators.py` to use `await llm_service.generate_content()`
- Made all LLM-calling methods async
- Updated call sites to await the async methods

**Files Modified**:
- `/backend/generators.py` - 8+ methods made async
- `/backend/character_creation.py` - Updated to await async calls

### 2. CUSTOM ARMOR PARAMETER MISMATCH ✅ FIXED
**Issue**: Constructor parameter name mismatch
**Error**: `CustomArmor.__init__() got an unexpected keyword argument 'base_ac'`
**Problem**: Generator passing `base_ac`, constructor expects `ac_base`
**Fix Applied**: 
- Updated parameter mapping in armor generator
- Added helper method `_map_dex_modifier_to_bonus_type()`

### 3. MISSING CHARACTER SHEET METHOD ✅ FIXED
**Issue**: CharacterSheet missing journal functionality
**Error**: `'CharacterSheet' object has no attribute 'add_journal_entry'`
**Fix Applied**:
- Added `journal_entries` list to CharacterState.__init__()
- Added `add_journal_entry()` method to CharacterSheet class

### 4. MISSING GENERATOR METHOD ⚠️ PARTIALLY FIXED
**Issue**: Missing helper method in CustomContentGenerator
**Error**: `'CustomContentGenerator' object has no attribute '_extract_simple_themes'`
**Status**: Added basic implementation, needs verification

## 🚫 REMAINING ISSUES TO INVESTIGATE

### 1. CHARACTER DATA STRUCTURE MISMATCH ❌ NEEDS FIX
**Current Problem**: Generated character data has wrong types
```python
# Wrong structure from LLM generation:
{
    'species': [],  # Should be string like "Human"
    'classes': [],  # Should be dict like {"Wizard": 3}
    'ability_score': {...},  # Should be 'ability_scores' (plural)
    'armors': [...],  # Should be 'armor' (singular)
    'equipments': [...],  # Should be 'equipment' (singular)
}
```
**Location**: `shared_character_generation.py` around line 180-200
**Impact**: Character creation completes but with fallback/empty data

### 2. JSON PARSING ERRORS ❌ ONGOING
**Issues**:
- `Extra data: line 1 column 159 (char 158)` - Malformed JSON from LLM
- `No JSON found in response` - LLM returning non-JSON content
**Location**: `_clean_json_response()` method in generators.py
**Impact**: Custom content generation fails, falls back to defaults

### 3. FIELD NAME MISMATCHES ❌ POTENTIAL ISSUES
**Observed**: Various field name mismatches in logs
```python
'ability_score' vs 'ability_scores'
'charismas' vs 'charisma' 
'idea_ls' vs 'ideals'
'armors' vs 'armor'
```
**Likely Cause**: LLM prompt/response parsing inconsistencies

## 🔍 DEBUGGING INFORMATION

### Current Backend Status
- **Server**: Starts cleanly with tinyllama
- **LLM Service**: Working with 5-minute timeout
- **Endpoints**: 33/35 passing in test suite
- **Character Generation**: Running end-to-end but producing fallback data

### Log Patterns to Watch
```bash
# Good signs:
INFO:llm_service:Ollama generated XXX characters
INFO:shared_character_generation:Character generation successful

# Problem signs:
ERROR:shared_character_generation:Unexpected error on attempt X: No JSON found in response
ERROR:generators:Failed to generate custom X: Extra data
WARNING:generators:Backstory generation failed: No JSON found in response
```

### Test Commands for Verification
```bash
# Test character generation
curl -X POST "http://localhost:8000/api/v1/characters/generate?prompt=Create%20a%20wise%20wizard" --max-time 300

# Test individual LLM endpoints
curl -X POST "http://localhost:8000/api/v1/generate/backstory" -H "Content-Type: application/json" -d '{"character_concept": "wise wizard"}' --max-time 300

# Run comprehensive test suite
./test_api_endpoints_refactored.sh
```

## 🎯 PRIORITY FIXES NEEDED

### Priority 1: Character Data Structure
**File**: `/backend/shared_character_generation.py`
**Method**: `generate_character_data()` around line 160-200
**Action**: Fix field name mapping between LLM response and character model

### Priority 2: JSON Response Cleaning
**File**: `/backend/generators.py`
**Method**: `_clean_json_response()`
**Action**: Improve JSON extraction and error handling

### Priority 3: Prompt Engineering
**Files**: All prompt generation methods
**Action**: Ensure prompts request correct field names matching models

## 📋 VERIFICATION CHECKLIST

When resuming work, verify:
- [ ] Backend starts without errors
- [ ] Character generation returns populated (not fallback) data
- [ ] LLM-generated content appears in character fields
- [ ] No JSON parsing errors in logs
- [ ] Character data structure matches model expectations
- [ ] All field names are consistent between prompts and models

## 🔧 QUICK FIX COMMANDS

```bash
# Start backend
cd /home/ajs7/dnd_tools/dnd_char_creator/backend && uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Test LLM endpoints only
cd /home/ajs7/dnd_tools/dnd_char_creator && ./test_llm_with_long_timeout.sh

# Test single character generation
curl -X POST "http://localhost:8000/api/v1/characters/generate?prompt=Create%20a%20wise%20wizard%20character" --max-time 300 | jq .

# View detailed logs
tail -f /tmp/backend.log  # If logging to file
```

---
**Last Updated**: June 26, 2025  
**Next Session**: Focus on character data structure fixes in shared_character_generation.py
