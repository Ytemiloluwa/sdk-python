#!/bin/bash
# Python SDK proto compiler using betterproto (equivalent to TypeScript version)

set -e

# Ensure we're in the correct directory
cd "$(dirname "$0")/.."

# Create output directory
mkdir -p src/core/encoders/proto/generated

# Use poetry run python3 to ensure we use the root environment with betterproto
PYTHON_CMD="poetry run python3"

# Step 1: Compile .proto files using betterproto (equivalent to protoc + ts-proto)
protoc --python_betterproto_out=./src/core/encoders/proto/generated \
    --proto_path="../../submodules/common/proto" \
    ../../submodules/common/proto/common.proto \
    ../../submodules/common/proto/core.proto \
    ../../submodules/common/proto/error.proto \
    ../../submodules/common/proto/session.proto \
    ../../submodules/common/proto/version.proto

# Step 2: Extract and consolidate types (equivalent to extractTypes/index.js)
$PYTHON_CMD ../../scripts/extract_types/__init__.py ./src/core/encoders/proto/generated ./src/core/encoders/proto/generated/types.py
