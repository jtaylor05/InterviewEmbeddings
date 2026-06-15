import argparse

from src import InterviewIterator
from sentence_transformers import SentenceTransformer

import umap
import pandas as pd
import plotly.express as px

MODEL_NAME = 'sentence-transformers/stsb-mpnet-base-v2'

def get_embeddings(paragraphs):
    model = SentenceTransformer(MODEL_NAME)
    return model.encode(paragraphs)

def graph(data):
    reducer = umap.UMAP(n_neighbors=5, min_dist=0.3, init='random')
    embeddings_2d = reducer.fit_transform(data)
    df = pd.DataFrame({
        "x": embeddings_2d[:, 0],
        "y": embeddings_2d[:, 1],
    })
    fig = px.scatter(df, x="x", y="y")
    fig.write_html("embeddings_graph.html")

def run_from_save(file_path):
    with open(file_path, "r") as f:
        embeddings = [[float(x) for x in line.split(",") if x] for line in f.readlines()]
    return embeddings

def run_from_docx(file_path, save=False, save_path="embeddings.txt"):
    interview_iterator = InterviewIterator(file_path)
    embeddings = get_embeddings(interview_iterator.get_paragraphs())
    if save:
        with open(save_path, "w") as f:
            for embedding in embeddings:
                f.write(",".join(map(str, embedding)) + "\n")
    return embeddings

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Get Embeddings for Interviews")
    arg_parser.add_argument("file_path", type=str, help="Path to the interview document")
    arg_parser.add_argument("--model", "-M", type=str, help="SentenceTransformer model to use for embeddings")
    arg_parser.add_argument("--graph", "-g", action="store_true", help="Whether to graph the embeddings")
    arg_parser.add_argument("--save", "-s", action="store_true", help="Whether to save the embeddings to a file")
    arg_parser.add_argument("--save-path", type=str, default="embeddings.txt", help="Path to save the embeddings file")
    arg_parser.add_argument("--from-save", "-f", action="store_true", help="Whether to run from a saved embeddings file instead of a docx file")
    args = arg_parser.parse_args()
    
    if args.model:
        MODEL_NAME = args.model
    
    embeddings = []
    if args.from_save:
        embeddings = run_from_save(args.file_path)
    else:
        embeddings = run_from_docx(args.file_path, save=args.save, save_path=args.save_path)

    if args.graph:
        graph(embeddings)