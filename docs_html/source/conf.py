# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "etl-addictions-graph"
copyright = "2025, MTUCI"
author = "MTUCI"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# extensions = []

templates_path = ["_templates"]
exclude_patterns = []

language = "ru"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_static_path = ["_static"]

# Добавьте расширение autodoc
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.graphviz",
    "sphinx.ext.napoleon",  # Поддержка Google-style docstrings
]

# Укажите путь к проекту
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

# Выберите тему (опционально)
html_theme = "sphinx_rtd_theme"

graphviz_dot = "D:/Graphviz/bin/dot.exe"
