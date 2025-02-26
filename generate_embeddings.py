from sentence_transformers import SentenceTransformer
import pandas as pd

# Load a pre-trained embedding model from Hugging Face
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """
    Generates an embedding for the given text using Sentence Transformers.
    """
    return model.encode(text).tolist()  # Convert numpy array to Python list

# Read CSV file properly
file_path = "cleaned_data_1.csv"

try:
    df = pd.read_csv(file_path)  # Load the dataset
    print("✅ CSV file loaded successfully!")

    # Convert all columns into text format
    df.fillna("", inplace=True)  # Replace NaN with empty strings
    texts = df.astype(str).agg(" ".join, axis=1).tolist()  # Combine all columns into a single text per row
    
    # Generate embeddings for each row
    embeddings = [get_embedding(text) for text in texts]
    
    print("✅ Embeddings generated successfully!")
except FileNotFoundError:
    print(f"❌ Error: '{file_path}' not found. Please check the file location.")
    exit()
except Exception as e:
    print(f"❌ Error loading CSV: {e}")
    exit()
