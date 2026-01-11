#!/usr/bin/env python3
"""
Setup script for building Dino Tamagotchi macOS app bundle
"""

from setuptools import setup
import py2app

APP = ['supabase_dino.py']
DATA_FILES = []

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,  # Makes it a menu bar app (no dock icon)
        'CFBundleName': 'Dino Tamagotchi',
        'CFBundleDisplayName': 'Dino Tamagotchi',
        'CFBundleGetInfoString': "A productivity companion with a virtual dinosaur pet",
        'CFBundleIdentifier': 'com.dinotamagotchi.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': u"Copyright © 2025, Dino Tamagotchi Contributors, All Rights Reserved"
    },
    'packages': ['rumps', 'supabase', 'tkinter'],
    'includes': [
        'rumps',
        'supabase', 
        'postgrest',
        'httpx',
        'tkinter',
        'urllib3',
        'datetime',
        'json',
        'os',
        'threading',
        'subprocess',
        'time',
        'random',
        'hashlib',
        're',
        'uuid',
        'getpass'
    ],
    'excludes': [
        'matplotlib',
        'numpy', 
        'scipy',
        'pandas',
        'jupyter'
    ],
    'iconfile': None,  # We'll add this later
    'resources': [],
    'frameworks': [],
    'arch': 'universal2',  # Support both Intel and Apple Silicon
}

setup(
    name="Dino Tamagotchi",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)