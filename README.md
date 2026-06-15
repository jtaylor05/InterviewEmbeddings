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

Then you can run the command as long as you have a GPU, or you can use the raw embeddings.

For a .docx file
```bash
python main.py <file_path> -g 
```

For an embeddings file
```bash
python main.py <file_path> -fg
```
