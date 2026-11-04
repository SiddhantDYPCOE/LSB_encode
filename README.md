# LSB Steganography

Hide a secret text message inside an image using Least Significant Bit (LSB) steganography.

## Project structure

```
LSB_encode/
├── images/
│   ├── input/       # Put original images here
│   └── output/      # Encoded images are saved here
├── encode.py
├── decode.py
├── requirements.txt
└── README.md
```

## 1. Install dependencies

Python 3.9+ is recommended.

```bash
python -m pip install -r requirements.txt
```

## 2. Add an image

Copy an image into `images/input/`, for example `images/input/photo.png`. The encoder accepts formats supported by Pillow; the encoded output is always PNG.

## 3. Hide a message

Run:

```bash
python encode.py
```

Enter the image filename (for example, `photo.png`) and your secret message. The result is saved as `images/output/encoded.png`.

You can also use command-line arguments:

```bash
python encode.py images/input/photo.png --message "Meet me at 5"
python encode.py images/input/photo.png --message "Meet me at 5" --output images/output/my_secret.png
```

## 4. Extract the message

```bash
python decode.py
```

Or specify an encoded image:

```bash
python decode.py images/output/encoded.png
```

## How it works

The encoder converts the message to UTF-8 bytes, adds a header containing a signature and message length, then stores each bit in the least significant bit of successive RGB channel values. The decoder reads the bits, validates the header, and reconstructs the message.

## Important notes

- Keep the encoded image as PNG. JPEG compression can destroy hidden LSB data.
- Do not resize, edit, or recompress the encoded image before decoding.
- LSB steganography hides a message but does **not** encrypt it.
- The image must have enough RGB channel capacity for the message.
