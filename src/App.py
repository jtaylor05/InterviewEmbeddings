from InterviewData import InterviewDataset, InterviewIterator

from Graph import Graph
from FileSelector import FileSelect
from embeddings import get_embeddings

from datetime import datetime
from tkinter import *
from tkinter import ttk

class App(Tk):

    def __init__(self):
        super().__init__()
        self.paragraphs : InterviewDataset = InterviewDataset()
        self.embeddings : InterviewDataset = InterviewDataset()

        self.title("InterViewer")
        
        self.id_filter = StringVar()
        self.new_interview_id = StringVar()
        self.new_meta_name = StringVar()
        self.metadata = StringVar()

        self._build_mainframe()
        self._build_fileframe()
        self._build_metaframe()
        self._build_graphframe()
        self._build_infoframe()
        self._configure_grid()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_mainframe(self):
        self.mainframe = ttk.Frame(self, padding=[3, 3, 12, 12])
        self.mainframe.grid(column=0, row=0, sticky=['N', 'W', 'E', 'S'])
        ttk.Label(self.mainframe, text="Interview Viewer", justify="center", font=("Arial", 30, "bold")).grid(
            column=0, columnspan=3, row=0, sticky=['N']
        )

    def _build_fileframe(self):
        self.fileframe = FileSelect(self.mainframe, padding=[5, 5, 5, 5], borderwidth=4, relief='sunken')
        self.fileframe.grid(column=0, row=1, rowspan=2, sticky=['N', 'S', 'E', 'W'])
        self.bind("<<Files-Selected>>", self._on_files_selected)
        # ttk.Label(self.fileframe, text="File Select", justify="center").pack(side='top', fill='x')
        # ttk.Button(self.fileframe, text="select files", command=self.select_file).pack(side='top', fill='x')

    def _build_metaframe(self):
        self.metaframe = ttk.Frame(self.fileframe, padding=[1, 1, 1, 1], borderwidth=1, relief='solid')
        self.metaframe.pack(side='bottom', fill='both')

        ttk.Label(self.metaframe, text="ID filter:", justify="right").grid(column=0, row=0, sticky=['E', 'W'])
        ttk.Entry(self.metaframe, width=20, textvariable=self.id_filter).grid(column=1, row=0, sticky=['E', 'W'])
        ttk.Button(self.metaframe, text="Filter", command=lambda: self.filter(self.id_filter.get())).grid(
            column=2, row=0, sticky=['E', 'W']
        )

        ttk.Label(self.metaframe, text="Interview:", justify="right").grid(column=0, row=1, sticky=['E', 'W'])
        self.interviewcb = ttk.Combobox(self.metaframe)
        self.interviewcb.bind('<<ComboboxSelected>>', self.update_available_metadata)
        self.interviewcb.grid(column=1, columnspan=2, row=1, sticky=['E', 'W'])
        ttk.Entry(self.metaframe, width=20, text=self.interviewcb.get(), textvariable=self.new_interview_id).grid(column=0, columnspan=3, row=2, sticky=['E', 'W'])
        
        ttk.Label(self.metaframe, text="New Metadata", justify="right").grid(column=0, row=3, sticky=['E', 'W'])
        ttk.Entry(self.metaframe, width=20, textvariable=self.new_meta_name).grid(column=1, row=3, sticky=['E', 'W'])
        ttk.Button(self.metaframe, text="Add", command=self.add_metadata_name).grid(
            column=2, row=3, sticky=['E', 'W']
        )

        ttk.Label(self.metaframe, text="Metadata:", justify="right").grid(column=0, row=4, sticky=['E', 'W'])
        self.metacb = ttk.Combobox(self.metaframe)
        self.metacb.bind('<<ComboboxSelected>>', self.select_metadata)
        self.metacb.grid(column=1, columnspan=2, row=4, sticky=['E', 'W'])

        ttk.Entry(self.metaframe, width=40, textvariable=self.metadata).grid(
            column=0, columnspan=2, row=5, sticky=['E', 'W']
        )
        ttk.Button(self.metaframe, text="Save", command=self.save_metadata).grid(column=2, row=5, sticky=['E', 'W'])

    def _build_graphframe(self):
        self.graphframe : Graph = Graph(
            self.mainframe, padding=[2, 2, 2, 2], borderwidth=2, relief='solid',
            data=[],
            ids=[],
            on_point_click=self.handle_click
        )
        self.graphframe.grid(column=1, row=1, rowspan=2, sticky=['N', 'E', 'S', 'W'])

    def _build_infoframe(self):
        self.infoframe = ttk.Frame(self.mainframe, padding=[5, 5, 5, 5], borderwidth=4, relief='sunken')
        self.infoframe.grid(column=2, row=1, rowspan=2, sticky=['N', 'S', 'E', 'W'])
        self.infoframe.columnconfigure(0, minsize=200)
        self.infoframe.rowconfigure(0, weight=1)

        self.target_label = ttk.Label(self.infoframe, borderwidth='2', relief='solid', wraplength=200, anchor='n')
        self.target_label.grid(column=0, row=0, sticky=['N', 'E', 'W', 'S'])

    def _configure_grid(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, minsize=800)
        self.mainframe.rowconfigure(1, minsize=600)
        self.mainframe.columnconfigure(2, weight=1)
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
    
    def _on_files_selected(self, event : Event):
        filenames = self.fileframe.filenames
        if filenames:
            if filenames[0].endswith((".txt", ".docx")):
                for file in filenames:
                    self.paragraphs.add_interviews(InterviewIterator(file))
            if filenames[0].endswith(".jsonl"):
                for file in filenames:
                    self.paragraphs += InterviewDataset.load(file)
            self.update_graph(self.paragraphs)
            self.update_available_interviews()
    
    def filter(self, id_filter : str):
        if id_filter == "":
            self.update_graph(self.paragraphs)
            return
        filtered = self.paragraphs.filter_data(id_filter)
        self.update_graph(filtered)

    def start(self):
        self.mainloop()
    
    def handle_click(self, id):
        self.target_label.config(text=self.paragraphs[id])
    
    def add_metadata_name(self):
        if self.interviewcb.get() == "":
            return
        if self.new_meta_name.get() == "":
            return
        self.paragraphs.assign_metadata(self.interviewcb.get(), self.new_meta_name.get(), "")
        self.update_available_metadata(None)
        
    def update_available_interviews(self):
        self.interviewcb.set("")
        self.interviewcb.config(values=self.paragraphs.interviews)
    
    def update_available_metadata(self, event):
        print("interviewcb: ", self.interviewcb.get(), list(self.paragraphs.metadata(self.interviewcb.get()).keys()))
        self.new_interview_id.set(self.interviewcb.get())
        self.metacb.set("")
        self.metacb.config(values=list(self.paragraphs.metadata(self.interviewcb.get()).keys()))
        self.metadata.set("")
    
    def select_metadata(self, event):
        if self.interviewcb.get() == "":
            return
        if self.metacb.get() == "":
            return
        self.metadata.set(self.paragraphs.metadata(self.interviewcb.get())[self.metacb.get()])
    
    def save_metadata(self):
        update_graph = False
        if self.interviewcb.get() != self.new_interview_id.get():
            print(f"{self.interviewcb.get()} != {self.new_interview_id.get()}")
            self.paragraphs.assign_interview_id(self.interviewcb.get(), self.new_interview_id.get())
            update_graph = True
        if self.metadata.get() != "":
            print(f"{self.metadata.get()} != ''")
            self.paragraphs.assign_metadata(self.new_interview_id.get(), self.metacb.get(), self.metadata.get())
        self.update_available_interviews()
        self.update_available_metadata(None)
        if update_graph:
            self.update_graph(self.paragraphs)
    
    def update_graph(self, new_data : InterviewDataset):
        self.embeddings = get_embeddings(new_data)
        self.graphframe.update(self.embeddings.data(), ids=self.embeddings.ids())
        print("done")
    
    def save(self):
        if len(self.paragraphs) > 0:
            now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            self.paragraphs.save(f"{now}.jsonl")
    
    def on_closing(self):
        print("closing")
        try:
            self.save()
            print("saved")
        finally:
            self.graphframe.close()
            self.destroy() 

if __name__ == "__main__":
    app = App()
    app.start()