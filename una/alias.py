from functools import reduce
from typing import cast


def _to_key_with_values(acc: dict[str, list[str]], alias: str) -> dict[str, list[str]]:
    k, v = str.split(alias, "=")
    values = [str.strip(val) for val in str.split(v, ",")]
    return {**acc, **{k: values}}


def parse(aliases: list[str]) -> dict[str, list[str]]:
    """Parse a list of aliases defined as key=value(s) into a dictionary"""
    return reduce(_to_key_with_values, aliases, {})


def pick(aliases: dict[str, list[str]], keys: set[str]) -> set[str]:
    matrix = [v for k, v in aliases.items() if k in keys]
    flattened = sum(matrix, cast(list[str], []))
    return set(flattened)


KNOWN_ALIASES = {
    "beautifulsoup4": ["bs4"],
    "pillow": ["PIL"],
    "scikit-learn": ["sklearn"],
    "scikit-image": ["skimage"],
    "opencv-python": ["cv2"],
    "python-ffmpeg": ["ffmpeg"],
    "pycryptodome": ["Crypto"],
    "pycryptodomex": ["Cryptodome"],
    "pyserial": ["serial"],
    "python-multipart": ["multipart"],
    "pyusb": ["usb"],
    "pyyaml": ["yaml"],
}
