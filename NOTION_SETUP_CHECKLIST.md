# ✅ Notion Integration Setup Checklist

## What's Been Completed

### Code Changes
- ✅ **Webhook Integration** (`src/api/webhooks.py:78-83`)
  - Automatically syncs new WhatsApp users to Notion
  - Happens on first user message
  - Non-blocking (errors don't crash the bot)

- ✅ **Function Executor** (`src/ai/function_executor.py`)
  - Added `mark_onboarded()` function
  - Added `check_onboarding_status()` function
  - Both ready for AI to call during conversations

- ✅ **Function Definitions** (`src/ai/function_definitions.py`)
  - Added 2 new Notion functions for AI to use
  - Properly formatted for Groq LLM

- ✅ **Integration Manager** (`src/integrations/notion_users.py`)
  - Complete NotionUserManager class
  - Methods: sync_user_to_notion, mark_onboarding_complete, get_onboarding_status, get_user_by_phone
  - Ready to use with correct property names

### Documentation
- ✅ **Integration Guide** (`NOTION_INTEGRATION_GUIDE.md`)
  - Step-by-step setup instructions
  - Architecture overview
  - Troubleshooting guide
  - Example conversations

---

## What You Need To Do Now

### Step 1: Discover Your Database Structure (5 minutes)

Run the discovery script to find your exact Notion property names:

```bash
export NOTION_API_KEY="your_notion_api_key_here"
export NOTION_USERS_DATABASE_ID="your_database_id_here"
python scripts/discover_notion_structure.py
```

**Copy the output** - note the exact property names shown (e.g., "Phone", "Onboarded", "Status")

### Step 2: Update Property Names (2-5 minutes)

If your Notion database uses different column names than the defaults, update `src/integrations/notion_users.py`:

**Example 1: Different phone property name**
```python
# Line 42: Change "Phone" to your actual property name
filter={"property": "Telefone", "phone_number": {"equals": phone_number}}
```

**Example 2: Different onboarding fields**
```python
# Lines 83-94: Update property names
properties={
    "Status Onboarding": {"checkbox": True},
    "Data Onboarding": {"date": {"start": datetime.utcnow().isoformat()}},
    "Situacao": {"select": {"name": "Active"}}
}
```

**Properties to check:**
- `get_user_by_phone()` - "Phone" property (line 42)
- `mark_onboarding_complete()` - "Onboarded", "Onboarded At", "Status" (lines 83-94)
- `sync_user_to_notion()` - "Name", "Phone", "Joined" (lines 152-170)
- `get_onboarding_status()` - "Onboarded" property (line 126)

### Step 3: Configure Render Environment (2-3 minutes)

Add to Render dashboard:

1. Go to https://dashboard.render.com
2. Select your service: **pangeia-bot-final**
3. Go to **Settings → Environment**
4. Add these variables:
   ```
   NOTION_API_KEY=your_notion_api_key_here
   NOTION_USERS_DATABASE_ID=your_database_id_here
   ```
5. Click **Save**
6. Service will automatically restart

### Step 4: Test the Integration (5-10 minutes)

1. **Send a WhatsApp message from a new phone number**
   - The bot should respond as normal
   - Check logs for: `"User {phone} synced to Notion"`

2. **Check Notion database**
   - New entry should appear with name and phone
   - "Joined" date should show current date

3. **Test onboarding functions**
   - Message something like: "vou fazer onboarding agora"
   - If AI calls `mark_onboarded`, Notion should update:
     - Onboarded: ✅
     - Onboarded At: Today's date
     - Status: Active

---

## Quick Reference

### What Happens Automatically

1. **New User First Message**
   ```
   WhatsApp → Bot receives message → Creates local user →
   Syncs to Notion → AI processes request
   ```

2. **Onboarding Completion**
   ```
   User says "pronto, já fiz tudo" →
   AI decides to call mark_onboarded →
   Function updates Notion → User marked as onboarded
   ```

### Environment Variables Required

| Variable | Value | Where to Get |
|----------|-------|-------------|
| `NOTION_API_KEY` | Your API key | https://notion.so/my-integrations |
| `NOTION_USERS_DATABASE_ID` | Database ID from URL | Your Notion database URL |

### New Bot Functions

| Function | AI Can Call | Purpose |
|----------|------------|---------|
| `mark_onboarded` | Yes | Mark user onboarding complete |
| `check_onboarding_status` | Yes | Check if user onboarded |

---

## File Summary

| File | Purpose | Status |
|------|---------|--------|
| `src/integrations/notion_users.py` | Notion API client | ✅ Created |
| `scripts/discover_notion_structure.py` | Property discovery | ✅ Created |
| `src/api/webhooks.py` | Auto-sync on first message | ✅ Modified |
| `src/ai/function_executor.py` | Onboarding functions | ✅ Modified |
| `src/ai/function_definitions.py` | Function schemas | ✅ Modified |
| `NOTION_INTEGRATION_GUIDE.md` | Full documentation | ✅ Created |
| `NOTION_SETUP_CHECKLIST.md` | This file | ✅ Created |

---

## Estimated Timeline

- **Discovery Script**: 5 min
- **Property Name Updates** (if needed): 5-10 min
- **Render Configuration**: 3-5 min
- **Testing**: 5-10 min
- **Total**: ~20-30 minutes

---

## Success Criteria

✅ All checklist items complete when:
1. Discovery script runs without errors
2. Property names in code match your Notion database
3. Environment variables set in Render
4. New WhatsApp user appears in Notion automatically
5. Onboarding marks user as complete in Notion

---

## Support Resources

- **Full Guide**: `NOTION_INTEGRATION_GUIDE.md`
- **Discovery Tool**: `scripts/discover_notion_structure.py`
- **Main Code**: `src/integrations/notion_users.py`
- **Webhook Hook Point**: `src/api/webhooks.py` lines 78-83
- **AI Function Calls**: `src/ai/function_executor.py` lines 296-372

---

**Status**: Ready for deployment ✅

The integration is fully coded and documented. Just run the discovery script and update property names if needed!
