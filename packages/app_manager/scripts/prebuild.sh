#!/bin/bash

set -e

# Ensure we're in the correct directory
cd "$(dirname "$0")/.."

rm -rf ./src/app_manager/proto/generated/*.py || true
rm -rf ./src/app_manager/proto/generated/manager || true

mkdir -p src/app_manager/proto/generated

# Use poetry run python3 to ensure we use the root environment with betterproto
PYTHON_CMD="poetry run python3"

protoc --python_betterproto_out=./src/app_manager/proto/generated \
    --proto_path="../../submodules/common/proto" \
    ../../submodules/common/proto/manager/common.proto \
    ../../submodules/common/proto/manager/core.proto \
    ../../submodules/common/proto/manager/firmware_update.proto \
    ../../submodules/common/proto/manager/get_device_info.proto \
    ../../submodules/common/proto/manager/get_logs.proto \
    ../../submodules/common/proto/manager/get_wallets.proto \
    ../../submodules/common/proto/manager/train_card.proto \
    ../../submodules/common/proto/manager/train_joystick.proto \
    ../../submodules/common/proto/manager/wallet_selector.proto

$PYTHON_CMD ../../scripts/extract_types/__init__.py ./src/app_manager/proto/generated ./src/app_manager/proto/generated/types.py