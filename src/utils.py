def clamp(n: float, minn: float, maxn: float) -> float:
    """Clamps a number between two values"""
    return max(min(maxn, n), minn)
