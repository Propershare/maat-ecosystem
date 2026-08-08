# Quick Debug Check

## What to Look For in Console

After sending: `List the contents of /home/suspect/.n8n`

### Expected Console Logs:

1. **Citations Processing:**
   ```
   citations: Array(1)
   citations with tool_result: Array(1)
   Citation 0: {tool_result: true, metadata: [...], ...}
   ```

2. **Tool Result Rendering:**
   ```
   [TOOL-RESULT] Rendering tool result: {isToolResult: true, displayType: "filesystem_list", ...}
   ```

3. **Timeline Check:**
   ```
   [TIMELINE] Checking for tool results: {hasSources: true, hasToolResults: true, ...}
   ```

## If You DON'T See These Logs:

1. **Frontend not restarted** - Stop and restart `npm run dev`
2. **Browser cache** - Hard refresh (Ctrl+Shift+R)
3. **Component not loading** - Check for JavaScript errors in console

## If You See Logs But No Visual:

1. Check if `displayType` is present in logs
2. Check if `toolData` is present and structured
3. Check for CSS/styling issues (inspect element)

## Critical Check:

In Network tab → Find chat completion request → Response:
- Look for `sources` array
- Check if `sources[0].tool_result === true`
- Check if `sources[0].metadata[0].display_type` exists
- Check if `sources[0].metadata[0].tool_data` exists

If these are missing, **backend needs restart**.

