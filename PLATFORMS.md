# Platform-Specific Notes

## FreeBSD

No special requirements. Python 3.6+ should work out of the box:

```bash
pkg install python3
python3 frame_system.py
```

## Linux (Debian/Ubuntu/Raspberry Pi OS)

```bash
apt-get update
apt-get install python3
python3 frame_system.py
```

## Alpine Linux (Docker)

```dockerfile
FROM alpine:latest
RUN apk add --no-cache python3
COPY *.py /app/
WORKDIR /app
CMD ["python3", "examples.py"]
```

## macOS

Use system Python or Homebrew:

```bash
brew install python3
python3 frame_system.py
```

## Windows

Use WSL or native Python:

```powershell
python frame_system.py
```

## Common Issues

1. **Import errors**: Make sure all .py files are in the same directory
2. **Python version**: Requires Python 3.6+ (for f-strings and type hints)
3. **File permissions**: Ensure .py files are readable

## Minimal Requirements

- Python 3.6+
- No external dependencies
- ~100KB disk space
- Works on ARM, x86, x64 architectures
