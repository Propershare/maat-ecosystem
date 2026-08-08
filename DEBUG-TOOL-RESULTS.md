# Debug Tool Results - Quick Guide

## Issue
Tool results are not showing with specialized renderers or timeline.

## Debug Steps

### 1. Check Browser Console
Open DevTools (F12) → Console tab, look for:
- `citations` - should show array of citations
- `citations with tool_result:` - should show citations with tool_result flag
- `Citation X:` - should show metadata with display_type and tool_data

### 2. Check Network Tab
1. Open DevTools → Network tab
2. Find the chat completion request
3. Check Response → `sources` array
4. Look for:
   - `tool_result: true`
   - `metadata[0].display_type: "filesystem_list"`
   - `metadata[0].tool_data` with structured data

### 3. Check Backend Logs
```bash
# If using systemd
sudo journalctl -u open-webui -f

# Look for:
# - "Error parsing tool_result" messages
# - Any exceptions during tool execution
```

### 4. Verify Frontend Detection
In browser console, run:
```javascript
// Check if citations are being processed
document.querySelectorAll('[class*="citation"]').length

// Check if tool_result flag is present
// (This will be logged automatically now)
```

## Expected Console Output

After the fix, you should see in console:
```
citations: Array(1)
citations with tool_result: Array(1)
Citation 0: {
  tool_result: true,
  metadata: [{display_type: "filesystem_list", tool_data: {...}}],
  ...
}
```

## If Still Not Working

1. **Clear browser cache completely**
2. **Restart backend**: `sudo systemctl restart open-webui`
3. **Restart frontend**: Stop and restart `npm run dev`
4. **Check that all files were saved**
5. **Verify imports are correct** (no TypeScript errors)

## Quick Test

After restart, try:
```
List the contents of /home/suspect/.n8n
```

Check console for the debug logs - they will show exactly what's being detected.

