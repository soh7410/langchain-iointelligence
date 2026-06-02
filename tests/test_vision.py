"""Test cases for vision (multimodal) helpers."""

import base64
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage

from langchain_iointelligence import (
    DEFAULT_VISION_MODEL,
    MAX_IMAGES_PER_REQUEST,
    VISION_MODELS,
    encode_image_to_data_url,
    image_content_block,
    vision_message,
)
from langchain_iointelligence.chat import IOIntelligenceChatModel

# Smallest possible valid PNG (1x1 transparent pixel).
_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


class TestImageContentBlock:
    """Tests for image_content_block()."""

    def test_https_url_passthrough(self):
        block = image_content_block("https://example.com/a.jpg")
        assert block == {
            "type": "image_url",
            "image_url": {"url": "https://example.com/a.jpg"},
        }

    def test_data_url_passthrough(self):
        data_url = "data:image/png;base64,AAAA"
        block = image_content_block(data_url)
        assert block["image_url"]["url"] == data_url

    def test_detail_hint(self):
        block = image_content_block("https://example.com/a.jpg", detail="high")
        assert block["image_url"]["detail"] == "high"

    def test_dict_passthrough(self):
        raw = {"type": "image_url", "image_url": {"url": "https://x/y.png"}}
        assert image_content_block(raw) is raw

    def test_dict_detail_injected(self):
        raw = {"type": "image_url", "image_url": {"url": "https://x/y.png"}}
        block = image_content_block(raw, detail="low")
        assert block["image_url"]["detail"] == "low"
        # Caller's dict must not be mutated.
        assert "detail" not in raw["image_url"]

    def test_dict_existing_detail_preserved(self):
        raw = {"type": "image_url", "image_url": {"url": "https://x/y.png", "detail": "high"}}
        block = image_content_block(raw, detail="low")
        assert block["image_url"]["detail"] == "high"
        assert block is raw

    def test_bytes_encoded_as_data_url(self):
        block = image_content_block(_PNG_BYTES)
        url = block["image_url"]["url"]
        assert url.startswith("data:image/png;base64,")

    def test_local_file_path(self, tmp_path):
        p = tmp_path / "pixel.png"
        p.write_bytes(_PNG_BYTES)
        block = image_content_block(str(p))
        assert block["image_url"]["url"].startswith("data:image/png;base64,")


class TestEncodeImageToDataUrl:
    """Tests for encode_image_to_data_url()."""

    def test_bytes_png_sniffed(self):
        url = encode_image_to_data_url(_PNG_BYTES)
        assert url.startswith("data:image/png;base64,")
        payload = url.split(",", 1)[1]
        assert base64.b64decode(payload) == _PNG_BYTES

    def test_content_overrides_wrong_extension(self, tmp_path):
        # A PNG renamed to .jpg must be reported as PNG (content wins).
        p = tmp_path / "photo.jpg"
        p.write_bytes(_PNG_BYTES)
        url = encode_image_to_data_url(p)
        assert url.startswith("data:image/png;base64,")

    def test_extension_used_when_content_unknown(self, tmp_path):
        # Unrecognised bytes -> fall back to the filename extension.
        p = tmp_path / "mystery.webp"
        p.write_bytes(b"not a real image payload")
        url = encode_image_to_data_url(p)
        assert url.startswith("data:image/webp;base64,")

    def test_fallback_mime_when_all_unknown(self, tmp_path):
        p = tmp_path / "blob.bin"
        p.write_bytes(b"\x00\x01\x02\x03")
        url = encode_image_to_data_url(p)
        assert url.startswith("data:image/jpeg;base64,")

    def test_mime_override(self):
        url = encode_image_to_data_url(_PNG_BYTES, mime_type="image/webp")
        assert url.startswith("data:image/webp;base64,")


class TestVisionMessage:
    """Tests for vision_message()."""

    def test_single_url(self):
        msg = vision_message("What is this?", "https://example.com/a.jpg")
        assert isinstance(msg, HumanMessage)
        assert msg.content[0] == {"type": "text", "text": "What is this?"}
        assert msg.content[1]["image_url"]["url"] == "https://example.com/a.jpg"

    def test_multiple_images(self):
        msg = vision_message(
            "Compare",
            ["https://example.com/a.jpg", "https://example.com/b.jpg"],
        )
        # text + 2 images
        assert len(msg.content) == 3
        assert msg.content[1]["type"] == "image_url"
        assert msg.content[2]["type"] == "image_url"

    def test_requires_at_least_one_image(self):
        with pytest.raises(ValueError, match="at least one image"):
            vision_message("hi", [])

    def test_too_many_images(self):
        urls = [f"https://example.com/{i}.jpg" for i in range(MAX_IMAGES_PER_REQUEST + 1)]
        with pytest.raises(ValueError, match="at most"):
            vision_message("hi", urls)

    def test_detail_applied_to_all(self):
        msg = vision_message(
            "x",
            ["https://example.com/a.jpg", "https://example.com/b.jpg"],
            detail="low",
        )
        assert msg.content[1]["image_url"]["detail"] == "low"
        assert msg.content[2]["image_url"]["detail"] == "low"

    def test_detail_applied_to_mixed_dict_and_url(self):
        prebuilt = {"type": "image_url", "image_url": {"url": "https://example.com/a.jpg"}}
        msg = vision_message(
            "x",
            [prebuilt, "https://example.com/b.jpg"],
            detail="high",
        )
        # Both the prebuilt block and the URL input get the hint.
        assert msg.content[1]["image_url"]["detail"] == "high"
        assert msg.content[2]["image_url"]["detail"] == "high"


class TestVisionWithChatModel:
    """Vision messages flow through the chat model conversion unchanged."""

    def test_passthrough_to_api_format(self):
        chat = IOIntelligenceChatModel(
            api_key="k",
            api_url="https://test.api.com/v1/chat/completions",
            model=DEFAULT_VISION_MODEL,
        )
        msg = vision_message("What is this?", "https://example.com/a.jpg")
        api = chat._convert_messages_to_api_format([msg])
        assert api[0]["role"] == "user"
        assert api[0]["content"] == msg.content


def test_vision_model_constants():
    assert DEFAULT_VISION_MODEL in VISION_MODELS
    assert all(isinstance(m, str) and m for m in VISION_MODELS)
    assert MAX_IMAGES_PER_REQUEST == 10
