import os

from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches

import numpy as np
import pandas as pd
import umap
from sklearn.cluster import KMeans

def on_point_click(row: pd.Series):
    """Stub: called when a scatter point is clicked. row contains the point's data."""
    print(row)
    target_label
    pass

def graph(master : ttk.Frame, data, ids=None) -> None:
    if len(data) < 10:
        raise ValueError(f"Data frame of length {len(data)} is too short. Must be >=10 entries long.")
        return
    if ids is not None and len(ids) != len(data):
        raise ValueError(f"Data and Ids must match length. {len(data)} != {len(ids)}.")
    
    # --- Dimensionality reduction + clustering (unchanged) ---
    reducer = umap.UMAP(n_neighbors=5, min_dist=0.3, init='random', random_state=10)
    embeddings_2d = reducer.fit_transform(data)
    df = pd.DataFrame({"x": embeddings_2d[:, 0], "y": embeddings_2d[:, 1]})

    kmeans = KMeans()
    labels = kmeans.fit_predict(embeddings_2d)
    centroids = kmeans.cluster_centers_

    df["cluster"] = labels.astype(str)
    if ids is not None:
        df["id"] = ids

    # --- Tkinter window ---
    frame = ttk.Frame(master)
    frame.pack(fill='both', expand=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#1e1e1e")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444")

    # --- Per-cluster colored scatter (layered) ---
    unique_clusters = sorted(df["cluster"].unique(), key=int)
    cmap = plt.colormaps.get_cmap("tab10")
    cluster_colors = {c: cmap(i) for i, c in enumerate(unique_clusters)}

    scatter_objects = []   # (PathCollection, cluster_df) per cluster
    for cluster_id in unique_clusters:
        mask = df["cluster"] == cluster_id
        sub = df[mask]
        sc = ax.scatter(
            sub["x"], sub["y"],
            color=cluster_colors[cluster_id],
            s=30, alpha=0.8,
            label=f"Cluster {cluster_id}",
            zorder=2,
        )
        scatter_objects.append((sc, sub.reset_index(drop=True)))

    # --- Centroid layer ---
    ax.scatter(
        centroids[:, 0], centroids[:, 1],
        marker="x", s=120, color="white",
        linewidths=2, label="Centroids", zorder=3,
    )

    # --- Legend ---
    legend_patches = [
        mpatches.Patch(color=cluster_colors[c], label=f"Cluster {c}")
        for c in unique_clusters
    ]
    legend_patches.append(
        plt.Line2D([0], [0], marker="x", color="white", linestyle="None",
                   markersize=10, markeredgewidth=2, label="Centroids")
    )
    ax.legend(handles=legend_patches, facecolor="#2e2e2e", labelcolor="white",
              edgecolor="#555", loc="best")

    # --- Hover tooltip ---
    tooltip = ax.annotate(
        "", xy=(0, 0), xytext=(12, 12),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.4", fc="#2e2e2e", ec="#888", alpha=0.95),
        color="white", fontsize=9, zorder=5,
    )
    tooltip.set_visible(False)

    def on_hover(event):
        if event.inaxes != ax:
            tooltip.set_visible(False)
            fig.canvas.draw_idle()
            return

        hit_any = False
        for sc, sub in scatter_objects:
            cont, ind = sc.contains(event)
            if cont:
                i = ind["ind"][0]
                row = sub.iloc[i]
                if ids is not None:
                    text = f"ID: {row['id']}\nCluster: {row['cluster']}"
                else:
                    text = f"Cluster: {row['cluster']}"
                tooltip.set_text(text)
                tooltip.xy = (event.xdata, event.ydata)
                tooltip.set_visible(True)
                hit_any = True
                break

        if not hit_any:
            tooltip.set_visible(False)
        fig.canvas.draw_idle()
    
    def on_click(event):
        if event.inaxes != ax or event.button != 1:  # left click only
            return
        for sc, sub in scatter_objects:
            cont, ind = sc.contains(event)
            if cont:
                on_point_click(sub.iloc[ind["ind"][0]])
                break

    def on_close():                        
        plt.close(fig)
        master.winfo_toplevel().destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    canvas.mpl_connect("motion_notify_event", on_hover)
    canvas.mpl_connect("button_press_event", on_click)

    master.winfo_toplevel().protocol("WM_DELETE_WINDOW", on_close)

def select_file():
    # Opens the OS native file dialog
    filename = fd.askopenfilenames(
        title="Select interviews",
        initialdir=os.getcwd(),
        filetypes=(("Valid files", ["*.txt", "*.docx"]), ("All files", "*.*"))
    )
    if filename:
        print(f"Selected: {filename}")

def filter():
    pass

root = Tk()
root.title("InterViewer")

mainframe = ttk.Frame(root, padding=[3, 3, 12, 12])
mainframe.grid(column=0, row=0, sticky=['N', 'W', 'E', 'S'])

ttk.Label(mainframe, text="Interview Viewer", justify="center", font=("Arial", 30, "bold")).grid(column=0, columnspan=3, row=0, sticky=['N'])

fileframe = ttk.Frame(mainframe, padding=[5, 5, 5, 5], borderwidth=4, relief='sunken')
fileframe.grid(column=0, row=1, rowspan=2, sticky=['N', 'S', 'E','W'])
ttk.Label(fileframe, text="File Select", justify="center").pack(side='top', fill='x')
ttk.Button(fileframe, text="select files", command=select_file).pack(side='top', fill='x')

metaframe = ttk.Frame(fileframe, padding=[1, 1, 1, 1], borderwidth=1, relief='solid')
metaframe.pack(side='bottom', fill='both')

id_filter = StringVar()


ttk.Label(metaframe, text="ID filter:", justify="right").grid(column=0, row=0, sticky=['E', 'W'])
ttk.Entry(metaframe, width=20, textvariable=id_filter).grid(column=1, row=0, sticky=['E', 'W'])
ttk.Button(metaframe, text="Filter", command=lambda: filter(id_filter)).grid(column=2, row=0, sticky=['E', 'W'])

metadata = StringVar()

ttk.Label(metaframe, text="Interview:", justify="right").grid(column=0, row=0, sticky=['E', 'W'])
interviewcb = ttk.Combobox(metaframe, values=["interview1", "interview2"])
interviewcb.grid(column=1, row=0, sticky=['E', 'W'])
ttk.Label(metaframe, text="Metadata:", justify="right").grid(column=0, row=1, sticky=['E', 'W'])
metacb = ttk.Combobox(metaframe, values=["meta1", "meta2"])
metacb.grid(column=1, row=1, sticky=['E', 'W'])
ttk.Entry(metaframe, width=40, textvariable=metadata).grid(column=0, columnspan=2, row=2, sticky=['E', 'W'])


graphframe = ttk.Frame(mainframe, padding=[2, 2, 2, 2], borderwidth=2, relief='solid')
graphframe.grid(column=1, row=1, rowspan=2, sticky=['N', 'E', 'S', 'W'])
graph(graphframe, [
    [1, 2, 3], [9, 4, 6], [3, 4, 4], [2, 2, 5], [4, 8, 10], [12, 3, 4], [3, 3, 3], [678, 67, 5], [2, 1, 0], [4, 5, 10]
    ], ids=range(10))

infoframe = ttk.Frame(mainframe, padding = [5, 5, 5, 5], borderwidth=4, relief='sunken')
infoframe.grid(column=2, row=1, rowspan=2, sticky=['N', 'S', 'E', 'W'])
infoframe.columnconfigure(0, minsize=200)
infoframe.rowconfigure(0, weight=1)

target_label = ttk.Label(infoframe, borderwidth='2', relief='solid', wraplength=200)
target_label.grid(column=0, row=0, sticky=['N', 'E', 'W', 'S'])



root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(2, weight=1)
for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

root.mainloop()