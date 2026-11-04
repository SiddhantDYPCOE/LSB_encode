from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
DEFAULT_IMAGE = ROOT / "images" / "output" / "encoded.png"
MAGIC = b"LSB1"


def read_bits(image: Image.Image, count: int) -> list[int]:
    bits = []
    for pixel in image.convert("RGB").getdata():
        for channel in pixel:
            bits.append(channel & 1)
            if len(bits) == count:
                return bits
    if len(bits) < count:
        raise ValueError("Image does not contain enough data for the message header.")
    return bits


def bits_to_bytes(bits: list[int]) -> bytes:
    if len(bits) % 8:
        raise ValueError("Bit data length must be divisible by 8.")
    output = bytearray()
    for start in range(0, len(bits), 8):
        value = 0
        for bit in bits[start:start + 8]:
            value = (value << 1) | bit
        output.append(value)
    return bytes(output)


def decode_message(image_path: Path) -> str:
    if not image_path.is_file():
        raise FileNotFoundError(f"Encoded image not found: {image_path}")

    image = Image.open(image_path).convert("RGB")
    header = bits_to_bytes(read_bits(image, 64))
    if header[:4] != MAGIC:
        raise ValueError("No supported hidden message was found in this image.")

    message_length = int.from_bytes(header[4:8], "big")
    payload = bits_to_bytes(read_bits(image, (8 + message_length) * 8))
    try:
        return payload[8:].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Hidden data was found, but it is not valid UTF-8 text.") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract an LSB-hidden message from an image.")
    parser.add_argument("image", nargs="?", default=str(DEFAULT_IMAGE), help="Encoded PNG image path")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_absolute():
        image_path = ROOT / image_path

    print("\nHidden message:")
    print(decode_message(image_path))


if __name__ == "__main__":
    main()
