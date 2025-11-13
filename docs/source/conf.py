# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MATS-2'
copyright = '2025, K.R. Rajesh, Jacob Mahto'
author = 'K.R. Rajesh, Jacob Mahto'
release = 'v8.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser"]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_css_files = ["search-fix.css"]
html_theme_options = {
    "logo": {
        "text": "MATS-2 v8.1",
    },
    "icon_links": [
        {"name": "GitHub", "url": "https://www.eternallyobsessed.com", "icon": "fab fa-github"},
    ],
}

html_search_summary = True
html_search_options = {
    "type": "default",
    "preload": True,
    "limit": 20,
    "short_title": True,
}


