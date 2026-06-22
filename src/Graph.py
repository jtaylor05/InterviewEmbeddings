from tkinter import *
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import umap
from sklearn.cluster import KMeans
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Graph(ttk.Frame):

    def __init__(self, master, data, ids=None, on_point_click=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_point_click = on_point_click  # optional callback: fn(row: pd.Series)
        
        self.data = data
        self.ids = ids
        
        self.fig = None
        
        if self._validate(data, ids):
            self._build_plot()

    # ------------------------------------------------------------------ #
    #  Validation                                                          #
    # ------------------------------------------------------------------ #

    def _validate(self, data, ids):
        if len(data) < 10:
            return False
        if ids is not None and len(ids) != len(data):
            return False
        return True

    # ------------------------------------------------------------------ #
    #  Data processing                                                     #
    # ------------------------------------------------------------------ #

    def _reduce_and_cluster(self):
        reducer = umap.UMAP(n_neighbors=5, min_dist=0.3, init='random', random_state=10)
        embeddings_2d = reducer.fit_transform(self.data)

        df = pd.DataFrame({"x": embeddings_2d[:, 0], "y": embeddings_2d[:, 1]})

        kmeans = KMeans()
        labels = kmeans.fit_predict(embeddings_2d)
        self.centroids = kmeans.cluster_centers_
        
        df["cluster"] = labels.astype(str)
        
        if self.ids is not None:
            df["id"] = self.ids

        return df

    # ------------------------------------------------------------------ #
    #  Plot construction                                                 #
    # ------------------------------------------------------------------ #

    def update(self, data, ids=None):
        if not self._validate(data, ids):
            return

        if self.fig:
            plt.close(self.fig)
            self._canvas_frame.destroy()  

        self.data = data
        self.ids = ids
        self._build_plot()
    
    def _build_plot(self):
        df = self._reduce_and_cluster()

        self.fig, self.ax = plt.subplots(figsize=(9, 6))
        self._style_axes()

        self.scatter_objects = self._draw_clusters(df)
        self._draw_centroids()
        self._draw_legend(df)
        self.tooltip = self._make_tooltip()

        self._embed_canvas()

    def _style_axes(self):
        self.fig.patch.set_facecolor("#1e1e1e")
        self.ax.set_facecolor("#1e1e1e")
        self.ax.tick_params(colors="white")
        for spine in self.ax.spines.values():
            spine.set_edgecolor("#444")

    def _draw_clusters(self, df):
        unique_clusters = sorted(df["cluster"].unique(), key=int)
        cmap = plt.colormaps.get_cmap("tab10")
        self.cluster_colors = {c: cmap(i) for i, c in enumerate(unique_clusters)}

        scatter_objects = []
        for cluster_id in unique_clusters:
            sub = df[df["cluster"] == cluster_id]
            sc = self.ax.scatter(
                sub["x"], sub["y"],
                color=self.cluster_colors[cluster_id],
                s=30, alpha=0.8,
                label=f"Cluster {cluster_id}",
                zorder=2,
            )
            scatter_objects.append((sc, sub.reset_index(drop=True)))

        return scatter_objects

    def _draw_centroids(self):
        self.ax.scatter(
            self.centroids[:, 0], self.centroids[:, 1],
            marker="x", s=120, color="white",
            linewidths=2, label="Centroids", zorder=3,
        )

    def _draw_legend(self, df):
        unique_clusters = sorted(df["cluster"].unique(), key=int)
        patches = [
            mpatches.Patch(color=self.cluster_colors[c], label=f"Cluster {c}")
            for c in unique_clusters
        ]
        patches.append(
            plt.Line2D([0], [0], marker="x", color="white", linestyle="None",
                       markersize=10, markeredgewidth=2, label="Centroids")
        )
        self.ax.legend(
            handles=patches, facecolor="#2e2e2e",
            labelcolor="white", edgecolor="#555", loc="best"
        )

    def _make_tooltip(self):
        tooltip = self.ax.annotate(
            "", xy=(0, 0), xytext=(12, 12),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.4", fc="#2e2e2e", ec="#888", alpha=0.95),
            color="white", fontsize=9, zorder=5,
        )
        tooltip.set_visible(False)
        return tooltip

    def _embed_canvas(self):
        self._canvas_frame = ttk.Frame(self) 
        self._canvas_frame.pack(fill='both', expand=True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self._canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)
        self.canvas.mpl_connect("button_press_event", self._on_click)

    # ------------------------------------------------------------------ #
    #  Event handlers                                                      #
    # ------------------------------------------------------------------ #

    def _on_hover(self, event):
        if event.inaxes != self.ax:
            self.tooltip.set_visible(False)
            self.fig.canvas.draw_idle()
            return

        hit_any = False
        for sc, sub in self.scatter_objects:
            cont, ind = sc.contains(event)
            if cont:
                row = sub.iloc[ind["ind"][0]]
                text = (
                    f"ID: {row['id']}\nCluster: {row['cluster']}"
                    if self.ids is not None
                    else f"Cluster: {row['cluster']}"
                )
                self.tooltip.set_text(text)
                self.tooltip.xy = (event.xdata, event.ydata)
                self.tooltip.set_visible(True)
                hit_any = True
                break

        if not hit_any:
            self.tooltip.set_visible(False)
        self.fig.canvas.draw_idle()

    def _on_click(self, event):
        if event.inaxes != self.ax or event.button != 1:
            return
        for sc, sub in self.scatter_objects:
            cont, ind = sc.contains(event)
            if cont:
                row : pd.Series = sub.iloc[ind["ind"][0]]
                if self.on_point_click:
                    self.on_point_click(row.get('id'))
                break

    def close(self):
        plt.close(self.fig)