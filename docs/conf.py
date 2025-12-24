import os
import sys

# Add source directories to sys.path for autodoc
sys.path.insert(0, os.path.abspath('../enc-cli/src'))
sys.path.insert(0, os.path.abspath('../server/src'))

# -- Project information -----------------------------------------------------

project = 'ENC'
copyright = '2025, Pranjal Bhaskare'
author = 'Pranjal Bhaskare'
release = '0.1.3'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = "_static/enc_icon.png"
html_favicon = "_static/enc_icon.png"

# Custom CSS
html_css_files = [
    'custom.css',
]

html_context = {
    "display_github": True,
    "github_user": "Pranjalab",
    "github_repo": "enc",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

html_theme_options = {
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}
