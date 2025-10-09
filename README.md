# Cypherock SDK

This project is a Python SDK for communicating with the Cypherock X1 hardware wallet. It provides a Hardware Wallet Interface (HWI) implementation, allowing seamless integration of the X1 with software wallets such as Sparrow Wallet and others.

## Prerequisites

### System Dependencies

**macOS:**

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install dependencies
brew install protobuf libusb
```

**Linux (Ubuntu/Debian):**

```bash
# Install build tools and system libraries
sudo apt-get update
sudo apt-get install build-essential protobuf-compiler libusb-1.0-0-dev libudev-dev

# For HID support
sudo apt-get install libhidapi-dev
```

**Windows:**

```bash
# Install via Chocolatey
choco install protoc libusb

# Or download from:
# - Protocol Buffers: https://github.com/protocolbuffers/protobuf/releases
# - libusb: https://libusb.info/
```

### Python Requirements

- Python 3.11+
- Poetry: `pip install poetry`

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Cypherock/sdk-python.git
cd sdk-python
git submodule update --init --recursive

# Complete setup (install dependencies + prebuild)
make setup
```

## Available Commands

```bash
make help     # Show all available commands
make setup    # Complete setup (install dependencies + prebuild)
make prebuild # Run prebuild for all packages
make test     # Run all tests
make lint     # Run linting checks
make format   # Format code
make clean   # Clean generated files
```

## Development

The SDK uses Protocol Buffers for device communication. The prebuild process generates Python code from `.proto` files and is required before using the SDK.

## Contributing

Please consider making a contribution to the project. Contributions can include bug fixes, feature proposals, or optimizations to the current code.
