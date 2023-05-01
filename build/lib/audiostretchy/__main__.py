#!/usr/bin/env python3
from pathlib import Path

import fire
from .stretch import process_audio

def cli():
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(process_audio)

if __name__ == "__main__":
    cli()
    