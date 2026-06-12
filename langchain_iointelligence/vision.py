"""Vision (multimodal) helpers for io Intelligence vision-enabled models.

io Intelligence exposes OpenAI-compatible vision models through the same
``/chat/completions`` endpoint. Images are passed as structured content
blocks inside a message, e.g.::

    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What is in this image?"},
            {"type": "image_url", "image_url": {"url": "https://..."}},
        ],
    }

This module provides small helpers to build such multimodal
``HumanMessage`` objects from remote URLs, local files, raw bytes or
pre-built data URLs, so callers don't have to assemble the content blocks
by hand.

See: https://io.net/docs/reference/ai-models/uploading-images
"""

import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from langchain_core.messages import HumanMessage

# Known vision-capable model identifiers on io Intelligence.
# Source: https://io.net/docs (Exploring AI Models / Uploading Images).
# This list is a convenience hint only; always treat the live
# ``list_available_models()`` output as the source of truth.
VISION_MODELS: List[str] = [
    "meta-llama/Llama-3.2-90B-Vision-Instruct",
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    "Qwen/Qwen2.5-VL-32B-Instruct",
    "Qwen/Qwen2-VL-7B-Instruct",
]

# Sensible default vision model for examples / quick starts.
DEFAULT_VISION_MODEL: str = "meta-llama/Llama-3.2-90B-Vision-Instruct"

# Per-request limits documented by io Intelligence.
MAX_IMAGES_PER_REQUEST: int = 10

# Anything that can be turned into an image content block.
ImageInput = Union[str, Path, bytes, bytearray, Dict[str, Any]]

_MIME_SIGNATURES = (
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),  # WEBP starts with RIFF....WEBP
    (b"BM", "image/bmp"),
)


# Generic MIME used only when neither magic bytes nor extension are conclusive.
_FALLBACK_MIME = "image/jpeg"

_EXT_MIME = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "bmp": "image/bmp",
}


def _sniff_mime(data: bytes) -> Optional[str]:
    """Detect an image MIME type from magic bytes, or ``None`` if unknown."""
    for signature, mime in _MIME_SIGNATURES:
        if data.startswith(signature):
            if mime == "image/webp" and data[8:12] != b"WEBP":
                continue
            return mime
    return None


def encode_image_to_data_url(
    image: Union[str, Path, bytes, bytearray],
    *,
    mime_type: Optional[str] = None,
) -> str:
    """Encode a local image file or raw bytes into a base64 ``data:`` URL.

    Args:
        image: Path to a local image file, or the raw image bytes.
        mime_type: Optional MIME type override (e.g. ``"image/png"``).
            When omitted the type is inferred from the image's magic bytes
            first, then the file extension, falling back to ``image/jpeg``.

    Returns:
        A ``data:<mime>;base64,<payload>`` URL string suitable for use as
        an ``image_url``.
    """
    if isinstance(image, (bytes, bytearray)):
        raw = bytes(image)
        # Magic bytes are authoritative for raw bytes (no filename to consult).
        mime = mime_type or _sniff_mime(raw) or _FALLBACK_MIME
    else:
        path = Path(image)
        raw = path.read_bytes()
        ext = path.suffix.lower().lstrip(".")
        # Trust the actual content over the (possibly wrong) filename
        # extension, e.g. a PNG renamed to ".jpg" or an extension-less temp file.
        mime = mime_type or _sniff_mime(raw) or _EXT_MIME.get(ext) or _FALLBACK_MIME

    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def image_content_block(
    image: ImageInput,
    *,
    detail: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a single ``image_url`` content block from a flexible input.

    Args:
        image: One of:
            * a remote ``http(s)://`` URL,
            * a pre-built ``data:`` URL,
            * a path to a local image file (``str`` or :class:`~pathlib.Path`),
            * raw image ``bytes``,
            * an already-built content block ``dict`` (passed through).
        detail: Optional OpenAI-style detail hint (e.g. ``"low"``/``"high"``).
            For a pre-built ``image_url`` block it is applied on top, unless the
            block already specifies its own ``detail``.
        mime_type: Optional MIME override used when encoding local files/bytes.

    Returns:
        A content block dict, e.g.
        ``{"type": "image_url", "image_url": {"url": ...}}``.
    """
    # Already a content block -> trust the caller, but still honour an
    # explicit ``detail`` hint so mixed inputs stay consistent.
    if isinstance(image, dict):
        if detail is None:
            return image
        inner = image.get("image_url")
        # Only inject into image_url blocks that don't already pin a detail.
        if isinstance(inner, dict) and "detail" not in inner:
            merged = dict(image)
            merged["image_url"] = {**inner, "detail": detail}
            return merged
        return image

    if isinstance(image, (bytes, bytearray)):
        url = encode_image_to_data_url(image, mime_type=mime_type)
    elif isinstance(image, Path):
        url = encode_image_to_data_url(image, mime_type=mime_type)
    elif isinstance(image, str):
        if image.startswith(("http://", "https://", "data:")):
            url = image
        else:
            # Treat as a local file path.
            url = encode_image_to_data_url(image, mime_type=mime_type)
    else:  # pragma: no cover - defensive
        raise TypeError(f"Unsupported image input type: {type(image)!r}")

    image_url: Dict[str, Any] = {"url": url}
    if detail is not None:
        image_url["detail"] = detail

    return {"type": "image_url", "image_url": image_url}


def vision_message(
    text: str,
    images: Union[ImageInput, Sequence[ImageInput]],
    *,
    detail: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> HumanMessage:
    """Build a multimodal ``HumanMessage`` combining text and image(s).

    Args:
        text: The text prompt accompanying the image(s).
        images: A single image input or a sequence of them. Each item may be
            a URL, data URL, local file path, raw bytes, or a content block
            dict (see :func:`image_content_block`).
        detail: Optional detail hint applied to every image.
        mime_type: Optional MIME override applied when encoding local
            files/bytes.

    Returns:
        A :class:`~langchain_core.messages.HumanMessage` whose ``content`` is a
        list of text + image content blocks, ready to pass to
        :class:`IOIntelligenceChatModel`.

    Raises:
        ValueError: If no images are provided or the documented per-request
            image limit is exceeded.
    """
    # Normalise to a list without splitting a lone str/bytes/dict.
    if isinstance(images, (str, Path, bytes, bytearray, dict)):
        image_list: List[ImageInput] = [images]
    else:
        image_list = list(images)

    if not image_list:
        raise ValueError("vision_message() requires at least one image")
    if len(image_list) > MAX_IMAGES_PER_REQUEST:
        raise ValueError(
            f"io Intelligence accepts at most {MAX_IMAGES_PER_REQUEST} images "
            f"per request, got {len(image_list)}"
        )

    content: List[Union[str, Dict[str, Any]]] = [{"type": "text", "text": text}]
    for img in image_list:
        content.append(
            image_content_block(img, detail=detail, mime_type=mime_type)
        )

    return HumanMessage(content=content)
