# Multi-platform Dockerfile for Frame System
FROM python:3.9-alpine

WORKDIR /app

# Copy frame system files
COPY *.py ./
COPY README.md ./

# No dependencies needed!
RUN python3 -m py_compile *.py

# Run tests on build to verify
RUN python3 test_frames.py

# Interactive Python with frame system loaded
CMD ["python3", "-i", "frame_system.py"]
