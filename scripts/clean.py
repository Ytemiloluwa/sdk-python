#!/usr/bin/env python3
import asyncio
import os
import shutil
from pathlib import Path
from typing import List

# Common Python folders to clean
common_py_folders = [
    "__pycache__",
    "*.egg-info",
    "dist",
    "build",
    ".pytest_cache",
    ".coverage",
]

# Package-specific folders to clean
packages = {
    "packages/core": common_py_folders + ["src/encoders/proto/generated"],
    "packages/app_manager": common_py_folders + ["src/proto/generated"],
    "packages/hw_hid": common_py_folders,
    "packages/hw_serialport": common_py_folders,
    "packages/hw_webusb": common_py_folders,
    "packages/interfaces": common_py_folders,
    "packages/util": common_py_folders,
}


async def confirm_from_user(
    question: str, positive_response: List[str], negative_response: List[str]
) -> bool:
    """Ask user for confirmation."""
    while True:
        response = input(f"{question}: ").lower().strip()

        if response in negative_response:
            return False
        elif response in positive_response:
            return True


def folder_exists(folder_path: Path) -> bool:
    """Check if folder exists."""
    return folder_path.exists()


async def remove_folders(parent_directory: Path, folders: List[str]) -> None:
    """Remove specified folders."""
    for folder in folders:
        folder_path = parent_directory / folder

        if folder_exists(folder_path):
            print(f"Deleting: {folder_path}")
            if folder_path.is_file():
                folder_path.unlink()
            else:
                shutil.rmtree(folder_path, ignore_errors=True)


async def run() -> None:
    """Main clean function."""
    parent_dir = Path(__file__).parent.parent
    all_folders_to_delete = []

    # Check for force flag
    is_force = "--force" in os.sys.argv or "-f" in os.sys.argv

    # Collect all folders to delete
    for pkg_name, folders in packages.items():
        for folder in folders:
            all_folders_to_delete.append(f"{pkg_name}/{folder}")

    print("Folders to be deleted:")
    for folder in all_folders_to_delete:
        print(f"  {folder}")

    if not is_force:
        confirmed = await confirm_from_user(
            "Do you want to delete all the above folders? (y/n)",
            ["y", "yes"],
            ["n", "no"],
        )
        if not confirmed:
            print("Clean operation cancelled.")
            return

    print(f"\nWorking dir: {parent_dir}")

    if not is_force:
        confirmed = await confirm_from_user(
            f"Please type the parent directory to confirm: ({parent_dir.name}/n)",
            [parent_dir.name],
            ["n", "no"],
        )
        if not confirmed:
            print("Clean operation cancelled.")
            return

    await remove_folders(parent_dir, all_folders_to_delete)
    print("Clean operation completed.")


if __name__ == "__main__":
    asyncio.run(run())
