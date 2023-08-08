#!/usr/bin/sh

poetry run pyinstaller -F -n conci -w --collect-all tk --collect-all customtkinter --collect-all pillow --collect-all CTkMessagebox --hidden-import='PIL._tkinter_finder' src/main.py
