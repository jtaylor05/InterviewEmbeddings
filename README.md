# HOW IT WORKS
The program is currently simple and relies on a pre-trained embeddings model from [sentence-transformers](https://huggingface.co/sentence-transformers/stsb-mpnet-base-v2). Different models will have different strengths

I then flatten the data into 2d using [umap](https://umap-learn.readthedocs.io/en/latest/) and plot that data using plotly.

# HOW TO USE IT

If you want to use it, first you have to have python and git installed. Then you must clone the environment onto your machine. Use the address in the 'CODE' section

```bash
git clone <code address> prj_embed
cd prj_embed
```

Then you have to make an environment and download all the proper dependencies.
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Then you must process your interview data:

```bash
python process.py --save_dataset=path_to_dataset path/to/interviews/*
```

The embeddings should be saved to the file embeddings.txt in the same directory as you ran this file. You can then graph your data with:

```bash
python graph.py embeddings.txt
```
