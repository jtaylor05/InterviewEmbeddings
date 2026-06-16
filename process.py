import argparse

from src import InterviewIterator, InterviewDataset
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'sentence-transformers/stsb-mpnet-base-v2'

def get_embeddings(paragraphs : list[str]):
    model = SentenceTransformer(MODEL_NAME)
    return model.encode(paragraphs)

def get_dataset(paths : list[str]) -> InterviewDataset:
    return InterviewDataset(InterviewIterator(paths))

def run_from_save(paths : list[str]):
    embeddings = []
    for path in paths:
        with open(path, "r") as f:
            embeddings += [[float(x) for x in line.split(",") if x] for line in f.readlines()]
    return embeddings

def run_from_docx(paths : list[str], save=False, save_path="embeddings.txt"):
    interview_iterator = InterviewIterator(*paths)
    embeddings = get_embeddings(interview_iterator.get_paragraphs())
    if save:
        with open(save_path, "w") as f:
            for embedding in embeddings:
                f.write(",".join(map(str, embedding)) + "\n")
    return embeddings

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Get Embeddings for Interviews")
    arg_parser.add_argument("interviews", nargs='+', type=str, help="Path to the interview or interview directory")
    arg_parser.add_argument("--model", "-M", type=str, help="SentenceTransformer model to use for embeddings")
    arg_parser.add_argument("--save-path", type=str, default="embeddings.txt", help="Path to save the embeddings file")
    arg_parser.add_argument("--save_dataset", type=str, default="", help="If you want to save the paragraph dataset")
    args = arg_parser.parse_args()
    
    if args.model:
        MODEL_NAME = args.model
    paragraph_data = InterviewDataset(InterviewIterator(*args.interviews))
    
    if args.save_dataset:
        paragraph_data.save(args.save_dataset)
    
    embeddings = get_embeddings(paragraph_data.data())
    
    embeddings_data = InterviewDataset([",".join([str(f) for f in e]) for e in embeddings])
    
    embeddings_data.save(args.save_path)