# Windows PowerShell Setup Script for Maat Memory
# Run this on Windows laptops (Imhotep, MacDaddy, Imhotepjr)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Maat Memory Setup - Windows" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Install Python first." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install psycopg2-binary pgvector langchain-huggingface
Write-Host ""

# Get database URL
Write-Host "Enter PostgreSQL database URL:" -ForegroundColor Yellow
Write-Host "Format: postgresql://user:password@host:port/database" -ForegroundColor Gray
Write-Host "Example: postgresql://suspect:<password>@192.168.4.21:5434/n8n_ai_starter" -ForegroundColor Gray
$dbUrl = Read-Host "Database URL"

if ($dbUrl) {
    $env:PGVECTOR_DB_URL = $dbUrl
    Write-Host "✅ Database URL set" -ForegroundColor Green
} else {
    Write-Host "⚠️  No database URL provided" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🧪 Testing connection..." -ForegroundColor Yellow

# Test Python import
try {
    python -c "from maat_memory import MaatMemory; m = MaatMemory(); print('✅ Maat Memory initialized')"
    Write-Host ""
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Run setup script:" -ForegroundColor Cyan
    Write-Host "  python scripts\setup_maat_memory.py" -ForegroundColor White
} catch {
    Write-Host "❌ Setup failed. Check errors above." -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

