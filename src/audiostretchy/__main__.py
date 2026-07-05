#!/usr/bin/env python3
# this_file: src/audiostretchy/__main__.py
"""
Command-line interface for AudioStretchy.
Provides CLI access to audio time-stretching functionality.
"""

import fire

from .core import stretch_audio


def main():
    """Main CLI entry point."""
    fire.Fire(stretch_audio)


if __name__ == "__main__":
    main()
