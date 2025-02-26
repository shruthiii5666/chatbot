from bs4 import BeautifulSoup
import pandas as pd

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text(separator=" ") if pd.notnull(text) else ''

# 1. Read CSV with validation
try:
    df = pd.read_csv("raw_html_1.csv")
except FileNotFoundError:
    print("Error: File not found. Check path/filename")
    exit()

# 2. Identify HTML content column
html_columns = [col for col in df.columns if 'html' in col.lower()]
if not html_columns:
    raise ValueError(f"No HTML column found. Available columns: {df.columns.tolist()}")

# 3. Use first matching HTML column
html_col = html_columns[0]
print(f"Using column '{html_col}' for cleaning")  # Debug output

# 4. Clean the HTML content
df['cleaned_text'] = df[html_col].apply(clean_html)

# 5. Remove duplicates based on cleaned content
df = df.drop_duplicates(subset=['cleaned_text'])

# 6. Save cleaned data
output_cols = ['URL', 'cleaned_text'] if 'URL' in df.columns else ['cleaned_text']
df[output_cols].to_csv("cleaned_data_1.csv", index=False)

import re

def validate_cleaning(df):
    # Check 1: No HTML tags remaining
    html_tags = df['cleaned_text'].apply(lambda x: bool(re.search('<[^>]+>', str(x))))
    print(f"Rows with HTML remnants: {html_tags.sum()}")

    # Check 2: Whitespace validation
    leading_trailing = df['cleaned_text'].apply(lambda x: x != x.strip() if pd.notnull(x) else False)
    print(f"Rows with leading/trailing spaces: {leading_trailing.sum()}")

    # Check 3: Null values
    print(f"Empty cleaned texts: {df['cleaned_text'].isnull().sum()}")

    # Check 4: Duplicates
    print(f"Remaining duplicates: {df.duplicated(subset=['cleaned_text']).sum()}")

validate_cleaning(df)