#!/bin/bash
# Frontend development server startup script
# Starts Vite dev server with hot reload

cd /home/suspect/.n8n/tehuti-lab-webui

echo "🎨 Starting Frontend Development Server (Vite)"
echo ""
echo "📋 This will:"
echo "   - Start Vite dev server with hot reload"
echo "   - Serve frontend from source (not build)"
echo "   - Proxy /api/* requests to backend on port 3000"
echo ""
echo "🌐 Access the app at: http://localhost:8080 (or port shown below)"
echo ""
echo "ℹ️  Note: pyodide:fetch is skipped (optional dependency)"
echo ""

npm run dev

