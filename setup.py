#!/usr/bin/env python3
"""
Setup script for the PrintPal Python client.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="printpal",
    version="1.0.2",
    author="PrintPal",
    author_email="support@printpal.io",
    description="Python client for the PrintPal 3D Generation API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/printpal-io/printpal-python",
    project_urls={
        "Documentation": "https://printpal.io/api/documentation",
        "API Dashboard": "https://printpal.io/api-keys",
        "Bug Reports": "https://github.com/printpal-io/printpal-python/issues",
        "Source": "https://github.com/printpal-io/printpal-python",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "printpal",
        "3d",
        "3d-generation",
        "3d-printing",
        "ai",
        "machine-learning",
        "image-to-3d",
        "text-to-3d",
        "stl",
        "glb",
        "obj",
    ],
)
