import logging
import azure.core.rest._aiohttp as _aiohttp_mod

try:
    import brotli
except ImportError:
    brotli = None

logger = logging.getLogger(__name__)

# Capture original function
original_helper = _aiohttp_mod._aiohttp_body_helper

def patched_aiohttp_body_helper(response):
    """
    Patched helper to support 'br' (Brotli) encoding.
    """
    enc = response.headers.get("Content-Encoding")
    if enc and enc.lower() == "br":
        if not response._decompressed_content:
            if brotli:
                try:
                    response._content = brotli.decompress(response._content)
                    response._decompressed_content = True
                except brotli.error as e:
                    # Fallback or let it fail if it's not valid brotli
                    logger.error(f"Failed to decompress brotli content: {e}")
                    pass
            else:
                logger.warning("Brotli content received but brotli package not installed.")
        return response._content
    return original_helper(response)

def apply_patch():
    """
    Monkeypatch azure.core.rest._aiohttp._aiohttp_body_helper to support 'br' (Brotli) encoding.
    """
    if not brotli:
        logger.warning("Brotli not installed, cannot patch azure-core for brotli support.")
        return

    # Check if already patched
    if getattr(_aiohttp_mod._aiohttp_body_helper, "_is_patched_for_brotli", False):
        logger.info("azure-core already patched for brotli.")
        return

    logger.warning("Applying patch to azure.core.rest._aiohttp._aiohttp_body_helper")
    patched_aiohttp_body_helper._is_patched_for_brotli = True
    _aiohttp_mod._aiohttp_body_helper = patched_aiohttp_body_helper
