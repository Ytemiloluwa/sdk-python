import semver
from typing import Dict


def string_to_version(version: str) -> Dict[str, int]:
    parsed_version = semver.VersionInfo.parse(version)
    if not parsed_version:
        raise ValueError(f"Invalid version: {version}")

    return {
        "major": parsed_version.major,
        "minor": parsed_version.minor,
        "patch": parsed_version.patch,
    }
