from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "images" / "input"
OUTPUT_DIR = ROOT / "images" / "output"
MAGIC = b"LSB1"


def bytes_to_bits(data: bytes) -> list[int]:
    return [(byte >> shift) & 1 for byte in data for shift in range(7, -1, -1)]


def encode_message(image_path: Path, message: str, output_path: Path) -> None:
    if not image_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = Image.open(image_path).convert("RGB")
    pixels = list(image.getdata())

    message_bytes = message.encode("utf-8")
    payload = MAGIC + len(message_bytes).to_bytes(4, "big") + message_bytes
    bits = bytes_to_bits(payload)
    capacity = len(pixels) * 3

    if len(bits) > capacity:
        raise ValueError(
            f"Message is too large for this image. Need {len(bits)} bits, "
            f"but image capacity is {capacity} bits."
        )

    encoded_pixels = []
    bit_index = 0
    for pixel in pixels:
        channels = list(pixel)
        for channel_index in range(3):
            if bit_index < len(bits):
                channels[channel_index] = (channels[channel_index] & 0xFE) | bits[bit_index]
                bit_index += 1
        encoded_pixels.append(tuple(channels))

    result = Image.new("RGB", image.size)
    result.putdata(encoded_pixels)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path, format="PNG")

    print(f"Message embedded successfully: {output_path}")
    print(f"Payload size: {len(message_bytes)} bytes")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hide a text message inside an image using LSB steganography.")
    parser.add_argument("image", nargs="?", help="Source image path (default: choose from images/input)")
    parser.add_argument("-m", "--message", help="Secret message to hide")
    parser.add_argument("-o", "--output", default=str(OUTPUT_DIR / "encoded.png"), help="Output PNG path")
    args = parser.parse_args()

    image_value = args.image or input("Image filename in images/input (e.g. photo.png): ").strip()
    image_path = Path(image_value)
    if not image_path.is_absolute() and not image_path.exists():
        image_path = INPUT_DIR / image_value

    message = args.message if args.message is not None else input("Enter the secret message: ")
    if not message:
        raise ValueError("The secret message cannot be empty.")

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    encode_message(image_path, message, output_path)


if __name__ == "__main__":
    main()
