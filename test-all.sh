#!/bin/bash
#!/bin/bash
# Test frame system on multiple platforms

echo "Frame System Cross-Platform Test"
echo "================================"

# Detect current platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "freebsd"* ]]; then
    PLATFORM="FreeBSD"
else
    PLATFORM="Unknown"
fi

echo "Current platform: $PLATFORM"
echo "Python version: $(python3 --version)"
echo ""

# Run tests
echo "Running test suite..."
python3 test_frames.py

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo -e "\nTesting in Docker (Alpine)..."
    docker run --rm -v $(pwd):/app -w /app alpine:latest sh -c \
        "apk add --no-cache python3 > /dev/null 2>&1 && python3 test_frames.py"
else
    echo -e "\nDocker not available, skipping container test"
fi

echo -e "\nTest complete!"
