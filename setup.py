"""Setup script for the Speech Transcriber package."""

from setuptools import find_packages, setup

setup(
    name="speech-transcriber",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pynput>=1.7.6",
        "pyaudio>=0.2.13",
        "openai>=1.3.0",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "speech-transcriber=speech_transcriber.__main__:main",
        ],
    },
    python_requires=">=3.8",
)
