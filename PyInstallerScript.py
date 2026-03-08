#Thank you gemini
#This is so I can make a build on mac

import PyInstaller.__main__
import os

# Define the script you want to package
script_path = 'main.py' 

# Define other PyInstaller options as command-line arguments in a list
# For example: 
# '--onefile' creates a single executable file
# '--windowed' prevents a console window from opening (useful for GUI apps)
# '--name' sets the name of the executable
# 'your_script_name.py' is the path to your main Python script

args = [
    script_path,
    '--onefile',
    '--windowed', # Use '--noconsole' in newer versions or as an alternative
    '--name',
    'main' #Name of app
]

# Run PyInstaller
PyInstaller.__main__.run(args)

print(f"PyInstaller finished. Check the 'dist' folder for your executable.")
