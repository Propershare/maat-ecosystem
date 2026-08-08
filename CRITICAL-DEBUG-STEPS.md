# Critical Debug Steps

## The Problem
Tool results are not showing with specialized renderers or timeline.

## What We Need to Verify

### Step 1: Check if Backend is Setting tool_result
1. **Check backend logs:**
   ```bash
   sudo journalctl -u open-webui -f --lines=100
   ```
   OR if running manually, check terminal output

2. **Look for these log lines:**
   ```
   [TOOL-RESULT] Adding source with tool_result=True, display_type=filesystem_list, tool_name=list_directory
   [TOOL-RESULT] tool_data keys: ['display_type', 'items', 'count', 'path']
   ```

3. **If you DON'T see these logs:**
   - Backend code changes aren't active
   - Backend needs restart
   - Check if file was saved correctly

### Step 2: Check Browser Console
After sending: `List the contents of /home/suspect/.n8n`

**Look for these logs (in order):**

1. `[CITATIONS] Sources received:` - Should show array with tool_result
2. `[CITATIONS] Sources with tool_result:` - Should show filtered array
3. `[CITATIONS] Source 0 tool_result:` - Should show metadata structure
4. `citations:` - Should show processed citations
5. `citations with tool_result:` - Should show citations with flag
6. `Citation 0:` - Should show detailed metadata
7. `[CITATION 0]` - Should show detection info
8. `[TOOL-RESULT] Rendering tool result:` - Should show when rendering

### Step 3: Check Network Tab
1. Open DevTools → Network tab
2. Find the chat completion request (filter by "chat" or "completion")
3. Click on it → Response tab
4. Look for `sources` array
5. Check `sources[0]`:
   - Should have `tool_result: true`
   - Should have `metadata[0].display_type: "filesystem_list"`
   - Should have `metadata[0].tool_data` with items array

### Step 4: If Logs Don't Appear

**Frontend logs not appearing:**
- Frontend not restarted
- Browser cache not cleared
- Component not rendering
- JavaScript error preventing execution

**Backend logs not appearing:**
- Backend not restarted
- Log level too high (check log level)
- Code not saved correctly

## Quick Test

1. **Restart backend:**
   ```bash
   sudo systemctl restart open-webui
   ```

2. **Restart frontend:**
   ```bash
   cd /home/suspect/.n8n/tehuti-lab-webui
   # Kill existing process
   pkill -f "vite dev"
   npm run dev
   ```

3. **Clear browser completely:**
   - Close all browser tabs
   - Clear cache and cookies
   - Hard refresh: Ctrl+Shift+R

4. **Test:**
   - Send: `List the contents of /home/suspect/.n8n`
   - Open console immediately
   - Check for ALL the logs listed above

## What to Report

If still not working, report:

1. **Backend logs:** Do you see `[TOOL-RESULT]` logs? (Yes/No)
2. **Frontend logs:** Which of the 8 logs above do you see? (List them)
3. **Network response:** What does `sources[0]` look like? (Copy the object)
4. **Console errors:** Any red errors in console? (List them)

This will tell us exactly where the problem is.

