# Frame System Makefile

.PHONY: all test clean docker tangle init images

# Default target
all: test

# Initialize development environment
init:
	uv venv
	uv pip install pytest mypy ruff
	@echo "Development environment initialized. Activate with: source .venv/bin/activate"

# Tangle from org file (requires Emacs)
tangle:
	emacs --batch -l org --eval "(org-babel-tangle-file \"kitchen-ops.org\")"

# Run tests
test:
	python3 test_frames.py

# Run examples
examples:
	python3 -i examples.py

# Clean generated files
clean:
	rm -f *.pyc __pycache__/* frames_backup.json frames_export.csv
	rmdir __pycache__ 2>/dev/null || true

# Docker operations
docker-build:
	docker build -t frame-workshop .

docker-run:
	docker run -it --rm frame-workshop

docker-test:
	docker run --rm frame-workshop python3 test_frames.py

# Platform-specific tests
test-all-platforms:
	@echo "Testing on current platform..."
	python3 test_frames.py
	@echo "\nTesting in Alpine container..."
	docker run --rm -v $(PWD):/app alpine:latest sh -c "apk add python3 && cd /app && python3 test_frames.py"
	@echo "\nAll platform tests completed!"

# Image conversions
images:
	@echo "Converting images to web-optimized formats..."
	for img in static/images/*.webp; do \
		base=$${img%.webp}; \
		convert $$img -resize 400x400 -depth 8 -colors 64 -background white -alpha remove -quality 50 $${base}_small.png; \
		echo "Converted $$img to $${base}_small.png"; \
	done
