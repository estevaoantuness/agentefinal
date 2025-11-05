# 📚 Notion Integration Guide

## Overview

This guide explains how to set up and use the Notion integration for the Pangeia WhatsApp Task Manager. The integration enables:

- **Automatic User Profile Sync**: New WhatsApp users are automatically added to your Notion employees database
- **Onboarding Tracking**: Track which employees have completed their WhatsApp onboarding
- **User Linking**: Phone numbers are used to match WhatsApp users to existing employee records in Notion

---

## Prerequisites

You need:
1. A Notion workspace with an employees database
2. A Notion integration token (API key)
3. Your database ID
4. Access to update the bot's environment variables

---

## Step 1: Discover Your Notion Database Structure

Your Notion database has specific column names (properties) that we need to find. We'll use the discovery script to extract them.

### 1.1 Get Your Notion API Key

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration or use existing one
3. Copy your API key (starts with `ntn_`)
4. Save it securely - do not commit to version control

### 1.2 Get Your Database ID

From your database URL: `https://www.notion.so/29ea53b3e53c805c88dde0e2ab9e58b9`

Extract the ID: `29ea53b3e53c805c88dde0e2ab9e58b9`

### 1.3 Run the Discovery Script

```bash
# Set environment variables
export NOTION_API_KEY="your_notion_api_key_here"
export NOTION_USERS_DATABASE_ID="your_database_id_here"

# Run the discovery script
python scripts/discover_notion_structure.py
```

This will output something like:

```
============================================================
📊 NOTION DATABASE STRUCTURE
============================================================

Database ID: 29ea53b3e53c805c88dde0e2ab9e58b9

📋 PROPERTIES (Columns):
----

✓ Property Name: 'Name'
  Type: title

✓ Property Name: 'Phone'
  Type: phone_number

✓ Property Name: 'Email'
  Type: email

✓ Property Name: 'Onboarded'
  Type: checkbox

✓ Property Name: 'Onboarded At'
  Type: date

✓ Property Name: 'Status'
  Type: select
  Options: ['Active', 'Inactive', 'Pending']

============================================================
```

**Copy the exact property names from the output** - these might differ from what's hardcoded in `notion_users.py`

---

## Step 2: Update Property Names in Code

Based on the discovery output, update `src/integrations/notion_users.py`:

### Example: If your database uses different column names

**Before** (default placeholders):
```python
filter={"property": "Phone", "phone_number": {"equals": phone_number}}
```

**After** (if your property is "Telefone"):
```python
filter={"property": "Telefone", "phone_number": {"equals": phone_number}}
```

Look for these methods and update property names as needed:
- `get_user_by_phone()` - change `"Phone"` property name
- `mark_onboarding_complete()` - change `"Onboarded"`, `"Onboarded At"`, `"Status"` property names
- `sync_user_to_notion()` - change `"Name"`, `"Phone"`, `"Joined"` property names

---

## Step 3: Configure Environment Variables

Add to your Render environment (or local .env):

```
NOTION_API_KEY=your_notion_api_key_here
NOTION_USERS_DATABASE_ID=your_database_id_here
```

---

## How It Works

### On First User Message

When a new WhatsApp user messages the bot:

1. ✅ User is created in local database
2. ✅ `notion_user_manager.sync_user_to_notion(user)` is called
3. ✅ User profile is created in Notion with:
   - Name (from WhatsApp contact name)
   - Phone (normalized phone number)
   - Joined date (current timestamp)
4. ✅ User is now linked to Notion

### When User Completes Onboarding

If the AI calls the `mark_onboarded` function:

```python
# The AI might say something like:
# "Great! Let me record your onboarding completion..."

# This triggers:
notion_user_manager.mark_onboarding_complete(phone_number)

# Which updates in Notion:
# - Onboarded: ✅ (checked)
# - Onboarded At: 2025-11-05 (current date)
# - Status: Active (select option)
```

### Checking Onboarding Status

The `check_onboarding_status` function can verify if a user has already completed onboarding:

```python
is_onboarded = notion_user_manager.get_onboarding_status(phone_number)
# Returns: True/False
```

---

## Available Functions

### 1. `sync_user_to_notion(user: User) -> Optional[str]`

**Purpose**: Create or update user profile in Notion

**Called by**: Webhook when new user first messages

**Updates in Notion**:
- Name
- Phone number
- Joined date

**Returns**: Notion page ID or None

### 2. `mark_onboarding_complete(phone_number: str) -> bool`

**Purpose**: Mark user as completed onboarding

**Called by**: `mark_onboarded` function (AI can call this)

**Updates in Notion**:
- Onboarded: ✅
- Onboarded At: Current date
- Status: Active

**Returns**: Success boolean

### 3. `get_onboarding_status(phone_number: str) -> bool`

**Purpose**: Check if user completed onboarding

**Called by**: `check_onboarding_status` function

**Returns**: True if onboarded, False otherwise

### 4. `get_user_by_phone(phone_number: str) -> Optional[Dict]`

**Purpose**: Find employee in Notion by phone number

**Used internally by**: Other methods for user lookup

**Returns**: Notion page data or None

---

## Example: AI Conversation Flow

```
User: Olá, vou configurar minha conta
(User is automatically synced to Notion)

Bot: Bem-vindo! Para completar sua configuração,
     posso marcar você como onboarded no nosso sistema?

User: Sim, pode marcar

Bot: [Calls mark_onboarded function]
     ✅ Onboarding completed and recorded in Notion!

     (In Notion, the status now shows: ✅ Onboarded)
```

---

## Testing the Integration

### Test 1: Verify Discovery Works

```bash
export NOTION_API_KEY="your_key"
export NOTION_USERS_DATABASE_ID="your_id"
python scripts/discover_notion_structure.py
```

Expected: See all properties and their types

### Test 2: Check Webhook Sync

1. Send a WhatsApp message from a new number
2. Check logs for: `"User {phone} synced to Notion"`
3. Look in Notion database - new entry should appear

### Test 3: Test Onboarding Functions

When the system is live, the AI can call:
- `check_onboarding_status` - asks the LLM to check if user is onboarded
- `mark_onboarded` - asks the LLM to record completion

---

## Troubleshooting

### Issue: "NOTION_USERS_DATABASE_ID not configured"

**Solution**: Set the environment variable:
```bash
export NOTION_USERS_DATABASE_ID="29ea53b3e53c805c88dde0e2ab9e58b9"
```

### Issue: "property not found" error

**Solution**: Run discovery script to find exact property names:
```bash
python scripts/discover_notion_structure.py
```

Then update `notion_users.py` with correct names.

### Issue: User not appearing in Notion

**Solution**:
1. Check logs for sync errors: `"Could not sync user..."`
2. Verify API key is valid
3. Verify database ID is correct
4. Check that Notion integration has database access

### Issue: Phone number doesn't match

**Solution**: Check phone normalization in:
- `src/utils/helpers.py` - `normalize_phone_number()`
- Ensure your Notion database phone format matches

---

## Architecture

```
WhatsApp Message
    ↓
Evolution API Webhook
    ↓
process_incoming_message()
    ├─ Create user in local DB
    └─ Call notion_user_manager.sync_user_to_notion()
         ↓
    Create/Update in Notion

AI Function Call: mark_onboarded
    ↓
function_executor.execute()
    ↓
notion_user_manager.mark_onboarding_complete()
    ↓
Update in Notion: mark onboarding fields
```

---

## Next Steps

1. ✅ Run `discover_notion_structure.py` with your credentials
2. ✅ Update property names in `src/integrations/notion_users.py` if needed
3. ✅ Deploy to Render with `NOTION_API_KEY` and `NOTION_USERS_DATABASE_ID` env vars
4. ✅ Test with a new WhatsApp user
5. ✅ Verify sync happens automatically

---

## Notes

- Phone number normalization is important - ensure consistent format
- The integration is read/write for user profiles
- Notion API rate limits: 3 requests per second (the integration respects this)
- All Notion operations are logged in the application logs
- Failed Notion operations don't block the bot - graceful fallback

---

## Support

For issues or questions about the integration, check:
- `src/integrations/notion_users.py` - Main implementation
- `scripts/discover_notion_structure.py` - Discovery tool
- `src/api/webhooks.py:78-83` - Sync trigger point
- Application logs for detailed error messages
