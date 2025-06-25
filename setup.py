"""
Setup file for audiostretchy.
Use setup.cfg to configure your project.

This file was generated with PyScaffold 4.4.1.
PyScaffold helps you to put up the scaffold of your new Python project.
Learn more under: https://pyscaffold.org/
"""

from setuptools import setup, Extension

# Dummy extension to make the wheel platform-specific as we include pre-compiled binaries.
# The location of dummy.c should be relative to pyproject.toml or setup.py.
# If dummy.c is in src/audiostretchy/, the name might need to reflect that path
# or sources path adjusted. For simplicity, let's assume it's at root or discoverable.
# Let's put it in src/audiostretchy/ for now.
dummy_ext = Extension(
    "audiostretchy._dummy_platform",
    sources=["src/audiostretchy/dummy.c"],
    optional=False,  # Ensure build fails if dummy.c is missing or can't compile
)

if __name__ == "__main__":
    try:
        setup(
            use_scm_version={"version_scheme": "no-guess-dev"}, ext_modules=[dummy_ext]
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
