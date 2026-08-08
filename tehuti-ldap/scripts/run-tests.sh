#!/bin/bash
# Run LDAP test suite with coverage reporting
# Maat-Aligned Test Execution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$PROJECT_DIR/tests"
VENV_DIR="$PROJECT_DIR/venv"

echo "🧪 Running LDAP test suite..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/upgrade test requirements
echo "Installing test requirements..."
pip install -q --upgrade pip
pip install -q -r "$TESTS_DIR/requirements.txt"

# Set test environment variables
export LDAP_HOST="${LDAP_HOST:-127.0.0.1}"
export LDAP_PORT="${LDAP_PORT:-389}"
export LDAP_BASE="${LDAP_BASE:-dc=tehuti,dc=lab}"
export LDAP_ADMIN="${LDAP_ADMIN:-cn=admin,dc=tehuti,dc=lab}"

# Get password from secure file
PASSWORD_FILE="$PROJECT_DIR/.ldap_admin_password"
if [ -f "$PASSWORD_FILE" ]; then
    export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
else
    export LDAP_ADMIN_PASSWORD="${LDAP_ADMIN_PASSWORD:-changeme}"
fi

# Run tests with coverage
echo ""
echo "Running tests with coverage..."
cd "$TESTS_DIR"

# Discover and run all tests
python -m coverage run --source="$PROJECT_DIR" -m unittest discover -s . -p "test_*.py" -v

# Generate coverage report
echo ""
echo "Generating coverage report..."
python -m coverage report -m
python -m coverage html -d "$PROJECT_DIR/htmlcov"

# Generate XML report for CI/CD
python -m coverage xml -o "$PROJECT_DIR/coverage.xml"

echo ""
echo "✅ Test execution complete"
echo ""
echo "📋 Coverage report:"
echo "   HTML: $PROJECT_DIR/htmlcov/index.html"
echo "   XML:  $PROJECT_DIR/coverage.xml"
echo ""
echo "📋 Test results:"
echo "   All tests completed. Check output above for details."

