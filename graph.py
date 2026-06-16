import argparse

from src import InterviewDataset

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
import umap

def graph(data, ids=None, save_path="embeddings_graph.html") -> pd.DataFrame:
    reducer = umap.UMAP(n_neighbors=5, min_dist=0.3, init='random')
    embeddings_2d = reducer.fit_transform(data)
    df = pd.DataFrame({
        "x": embeddings_2d[:, 0],
        "y": embeddings_2d[:, 1],
    })

    kmeans = KMeans()
    labels = kmeans.fit_predict(embeddings_2d)
    centroids = kmeans.cluster_centers_

    centroid_df = pd.DataFrame({
        "x": centroids[:, 0],
        "y": centroids[:, 1],
    })

    df["cluster"] = labels.astype(str)

    if ids is not None:
        df["id"] = ids
        custom_data_cols = ["id", "cluster"]
        hovertemplate = "ID: %{customdata[0]}<br>Cluster: %{customdata[1]}<extra></extra>"
    else:
        custom_data_cols = ["cluster"]
        hovertemplate = "Cluster: %{customdata[0]}<extra></extra>"

    fig = px.scatter(
        df, x="x", y="y", color="cluster",
        custom_data=custom_data_cols,
        hover_data={"x": False, "y": False, "cluster": False},
    )

    if ids is not None:
        fig.update_traces(
            hovertemplate=hovertemplate,
            selector=dict(mode="markers"),
        )

    centroid_trace = go.Scatter(
        x=centroid_df["x"],
        y=centroid_df["y"],
        mode="markers",
        marker=dict(symbol="x", size=12, color="black", line=dict(width=2)),
        name="Centroids",
        hoverinfo="skip",
    )
    fig.add_trace(centroid_trace)

    fig.write_html(save_path)
    
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Get Graph for Embeddings")
    arg_parser.add_argument("data_path", type=str, help="Path to the embedding data")
    arg_parser.add_argument("--save-path", type=str, default="graph.html", help="Path to save the graph")
    args = arg_parser.parse_args()
    
    embeddings_data = InterviewDataset()
    embeddings_data.load(args.data_path)
    data = [[float(num) for num in embedding.split(",")] for embedding in embeddings_data.data()]
    
    df = graph(data, ids=embeddings_data.ids(), save_path=args.save_path)