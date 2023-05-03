#!/usr/bin/env python3
from pathlib import Path

import fire
from .stretch import stretch_wav

def cli():
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(stretch_wav)

if __name__ == "__main__":
    cli()
    