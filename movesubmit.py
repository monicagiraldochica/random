#!/usr/bin/env python3
__author__ = "Monica Keith"
__status__ = "Production"
__purpose__ = "Install R packages"

import tkinter as tk
from tkinter import filedialog

input_files = []
slurm_script = ""

def selectFiles(root):
    global input_files
    files = filedialog.askopenfilenames(parent=root,title='Choose files')
    if files:
        for f in files:
            input_files.append(f)

def selectScript(root):
    global slurm_script
    slurm_script = filedialog.askopenfilename(parent=root,title='Choose SLURM script')

def selectFolder():
    global input_files
    dirpath = filedialog.askdirectory(title="Select a folder")
    if dirpath:
        input_files.append(dirpath)

def printFiles():
    for f in input_files:
         print(f)

def printScript():
    print(f"*{slurm_script}*")

root = tk.Tk()
root.title("File selection example")
selectButton = tk.Button(root, text="Select Files", command=lambda:selectFiles(root))
selectButton.pack(pady=20)
selectButton2 = tk.Button(root, text="Select Folder", command=selectFolder)
selectButton2.pack(pady=20)
selectButton3 = tk.Button(root, text="Select Script", command=lambda:selectScript(root))
selectButton3.pack(pady=20)

printFilesButton = tk.Button(root, text="Print input files", command=printFiles)
printFilesButton.pack(pady=20)
printScriptButton = tk.Button(root, text="Print script", command=printScript)
printScriptButton.pack(pady=20)
root.mainloop()