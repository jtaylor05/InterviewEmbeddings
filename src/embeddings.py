from InterviewData import InterviewDataset

from sentence_transformers import SentenceTransformer

MODEL_NAME = 'sentence-transformers/stsb-mpnet-base-v2'

def get_embeddings(dataset : InterviewDataset) -> InterviewDataset:
    dict = dataset.as_dict()
    data = dataset.data()
    
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(data)
    
    return InterviewDataset.from_dict([{**d, InterviewDataset.DATA:list(e)} for d, e in zip(dict, embeddings)])