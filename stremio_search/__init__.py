"""Stremio Search plugin package.

The entry module lives in a package so its module name is unique. The Wox
Python host derives the module name from `Entry` in plugin.json and imports
it while every plugin's directory is on one shared sys.path, so a bare
"main.py" resolves to the module "main" for every plugin that declares it.
"""
