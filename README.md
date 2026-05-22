# 🎬 Movie Recommendation System

A simple machine learning-based movie recommendation web app built using Python and Streamlit.

## Features

- Movie recommendations using cosine similarity
- TF-IDF vectorization
- Fuzzy movie search
- Interactive Streamlit UI

## Flow 

User
  ↓
app.py (UI)
  ↓
model.py (recommendation logic)
  ↓
Results returned
  ↓
app.py displays them

## Tech Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit

## Run Locally

```bash
uv add -r requirements.txt
streamlit run app.py


##note
dataset download link: https://www.kaggle.com/datasets/harshshinde8/movies-csv