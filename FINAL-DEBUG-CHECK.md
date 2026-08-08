# Final Debug Check - Step by Step

## The Issue
No console logs appearing means the code isn't running or data isn't flowing.

## Step-by-Step Verification

### Step 1: Verify Frontend Code is Loaded
1. Open browser DevTools (F12)
2. Go to Sources tab (or Network → find the main JS file)
3. Search for: `[RESPONSE-MESSAGE]` or `[CITATIONS-COMPONENT]`
4. If NOT found → Frontend code changes aren't loaded
   - **Fix:** Restart frontend dev server completely

### Step 2: Check if Component Renders
1. In Console, type: `document.querySelectorAll('[class*="citation"]').length`
2. Should return a number > 0 if Citations component exists
3. If 0 → Component isn't rendering

### Step 3: Check Message Object
1. In Console, find the message object
2. Type: `$0` (if you selected the message element)
3. Or check: `window.__message__` (if we add it)
4. Look for `sources` property

### Step 4: Check Network Response
1. Network tab → Find chat completion request
2. Response tab → Look for `sources` in the response
3. **Critical:** Check if `sources` is:
   - An array of strings? (wrong - should be objects)
   - An array of objects? (correct)
   - Missing entirely? (backend issue)

### Step 5: Backend Verification
```bash
# Check backend logs
sudo journalctl -u open-webui -f --lines=50

# Look for:
# [TOOL-RESULT] Adding source with tool_result=True
```

## Quick Test Script

Run this in browser console after sending a message:
```javascript
// Find all message elements
const messages = document.querySelectorAll('[role="listitem"]');
console.log('Total messages:', messages.length);

// Check last message
const lastMessage = messages[messages.length - 1];
console.log('Last message:', lastMessage);

// Try to find sources
const sourcesButton = lastMessage.querySelector('[class*="Source"]');
console.log('Sources button found:', !!sourcesButton);
```

## Most Likely Issues

1. **Frontend not restarted** → Code changes not loaded
2. **Browser cache** → Old code still running
3. **Sources is string array** → Backend returning wrong format
4. **Component not rendering** → Conditional not met

## Nuclear Option

If nothing works:
1. **Stop everything:**
   ```bash
   pkill -f "vite"
   pkill -f "uvicorn"
   sudo systemctl stop open-webui
   ```

2. **Clear all caches:**
   ```bash
   cd /home/suspect/.n8n/tehuti-lab-webui
   rm -rf node_modules/.vite
   rm -rf .svelte-kit
   ```

3. **Restart fresh:**
   ```bash
   npm run dev
   # In another terminal
   sudo systemctl start open-webui
   ```

4. **Browser:**
   - Close all tabs
   - Clear all data
   - Open fresh: http://localhost:3000

## What We Need

After restart, send: `List the contents of /home/suspect/.n8n`

**Report:**
1. Do you see `[RESPONSE-MESSAGE]` logs? (Yes/No)
2. Do you see `[CITATIONS-COMPONENT]` logs? (Yes/No)
3. In Network tab → Response → What does `sources` look like? (Copy it)

This will tell us exactly where the problem is.

