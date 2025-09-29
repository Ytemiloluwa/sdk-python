from packaging import version


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    
    This mimics the compare-versions JavaScript library behavior.
    """
    try:
        v1 = version.parse(version1)
        v2 = version.parse(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except Exception:
        # If parsing fails, treat as equal
        return 0


__all__ = ["compare_versions"] 