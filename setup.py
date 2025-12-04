"""
Setup file for stegochess package
Install with: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="stegochess",
    version="0.1.0",
    description="Chess Endgame Steganography Solver - YOLO + STRIPS",
    author="Anthony Wood",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        "Pillow>=9.0.0",
        "chess>=1.9.0",
        "ultralytics>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'stegostripsus=stegoSTRIPSus:main',
        ],
    },
)
