from enum import Enum
from typing import Dict, Optional, TypedDict
from packaging import version
from packaging.version import InvalidVersion


class FeatureName(Enum):
    RawCommand = "RawCommand"
    ProtoCommand = "ProtoCommand"


class FeatureConfig(TypedDict):
    from_version: str
    to_version: Optional[str]


# from is inclusive and to is exclusive
FeatureMap: Dict[FeatureName, FeatureConfig] = {
    FeatureName.RawCommand: {"from_version": "2.0.0", "to_version": "3.0.0"},
    FeatureName.ProtoCommand: {"from_version": "3.0.0", "to_version": "4.0.0"},
}


def is_feature_enabled(feature_name: FeatureName, sdk_version: str) -> bool:
    """
    Check if a feature is enabled for the given SDK version.

    Args:
        feature_name: The feature to check
        sdk_version: The SDK version to check against

    Returns:
        True if the feature is enabled, False otherwise
    """
    if feature_name not in FeatureMap:
        return False

    feature_config = FeatureMap[feature_name]
    from_version = feature_config["from_version"]
    to_version = feature_config.get("to_version")

    try:
        # Check if sdk_version >= from_version (compareVersions(from, sdkVersion) < 1)
        enabled = version.parse(sdk_version) >= version.parse(from_version)

        # If to_version is specified, check if sdk_version < to_version (compareVersions(to, sdkVersion) > 0)
        if to_version:
            enabled = enabled and version.parse(sdk_version) < version.parse(to_version)

        return enabled
    except (InvalidVersion, TypeError, ValueError):
        # If version parsing fails due to invalid version format, return False
        return False
