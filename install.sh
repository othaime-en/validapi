#!/bin/bash

echo "Installing validAPI..."

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

if [[ $(echo "$python_version < 3.8" | bc -l) ]]; then
    echo " Python 3.8+ is required. Please upgrade Python."
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "⬆ Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "📁 Creating directories..."
mkdir -p reports examples tests/fixtures

# Copy example files
echo "Creating example files..."
if [ ! -f "examples/test_data.json" ]; then
    cat > examples/test_data.json << 'EOF'
{
  "/posts": {
    "post": {
      "json": {
        "title": "Test Post",
        "body": "This is a test post created by the API validator",
        "userId": 1
      }
    }
  },
  "/posts/{id}": {
    "get": {
      "path_params": {
        "id": 1
      }
    }
  },
  "/users": {
    "get": {
      "params": {
        "limit": 5
      }
    }
  }
}
EOF
fi

# Make CLI executable
chmod +x src/main.py

echo "   Installation complete!"
echo ""
echo "   Quick start:"
echo "   source venv/bin/activate"
echo "   python src/main.py validate specs/example_spec.yaml"
echo ""
echo "   For more help:"
echo "   python src/main.py --help"