import os

from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd

class FileSelect(ttk.Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(self, text="File Select", justify="center").pack(side='top', fill='x')
        ttk.Button(self, text="select files", command=self._file_button_pressed).pack(side='top', fill='x')
    
    def _file_button_pressed(self):
        self.filenames = fd.askopenfilenames(
            title="Select interviews",
            initialdir=os.getcwd(),
            filetypes=(("Raw Interviews", ["*.txt", "*.docx"]), ("Processed Data", ["*.jsonl"]), ("All files", "*.*"))
        )
        self.event_generate("<<Files-Selected>>", data=self.filenames)