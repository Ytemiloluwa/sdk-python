.PHONY: setup prebuild test lint format clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  setup     - Complete setup (install dependencies and run prebuild)"
	@echo "  prebuild  - Run prebuild for all packages"
	@echo "  test      - Run all tests"
	@echo "  lint      - Run linting checks"
	@echo "  format    - Format code with black"
	@echo "  clean     - Clean generated files"

# Complete setup process
setup:
	@echo "Setting up Cypherock SDK..."
	@echo "1. Installing dependencies..."
	poetry install
	@echo "2. Running prebuild..."
	$(MAKE) prebuild
	@echo "Setup complete!"

# Run prebuild for all packages
prebuild:
	@echo "Running prebuild for all packages..."
	@echo "Core package..."
	cd packages/core && chmod +x scripts/prebuild.sh && ./scripts/prebuild.sh
	@echo "App Manager package..."
	cd packages/app_manager && chmod +x scripts/prebuild.sh && ./scripts/prebuild.sh
	@echo "BTC App package..."
	cd packages/app_btc && chmod +x scripts/prebuild && ./scripts/prebuild
	@echo "Prebuild complete!"

# Run all tests
test:
	@echo "Running all tests..."
	poetry run pytest

# Run linting
lint:
	@echo "Running linting checks..."
	poetry run ruff check .

# Format code
format:
	@echo "Formatting code..."
	poetry run black .

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	find . -name "*.pyc" -not -path "./*/.git/*" -delete
	find . -name "__pycache__" -type d -not -path "./*/.git/*" -exec rm -rf {} +
	find . -name "*.egg-info" -type d -not -path "./*/.git/*" -exec rm -rf {} +
	find . -name "dist" -type d -not -path "./*/.git/*" -exec rm -rf {} +
	find . -name "build" -type d -not -path "./*/.git/*" -exec rm -rf {} +
	@echo "Clean complete!"
