import importlib_metadata

try:
    version = importlib_metadata.version("mishikallm")
except Exception:
    version = "unknown"
