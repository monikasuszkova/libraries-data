# Registered Libraries – Data for MUNI
This readme was created by Monika Suszkova

## Description
The aim of this repository is to demonstrate how to automatically download, process, and analyze data for ECON MUNI usage. The source data come from the Ministry of Culture of the Czech Republic and relate to the database of all registered libraries in the country.

## Repository Structure
/libraries-data
├── download_libraries.py # Python script to download and process XLSX data
├── last_hash.txt # Stores hash of the last downloaded file
├── *.xlsx # Source Excel files from MK CR
├── *.csv # Exported CSV files
└── README.md # Project description

## First Task
This task demonstrates an approach to automatically download and manage data from the Ministry of Culture of the Czech Republic, ensuring that the latest information on registered libraries is always available for analysis.

### Implementation
This task demonstrates how to automatically download and process the latest data on registered libraries from the Ministry of Culture of the Czech Republic. The workflow ensures that the latest Excel file is always available, changes are detected, and the data is converted for analysis.

#### 1. Fetching the web page and locating the XLSX file
We use Python to download the web page and parse it to find the link to the latest Excel file:
```python
import requests
from bs4 import BeautifulSoup

resp = requests.get(BASE_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

xlsx_links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".xlsx")]
xlsx_url = xlsx_links[0]
if not xlsx_url.startswith("http"):
    xlsx_url = "https://mk.gov.cz" + xlsx_url

print("Found XLSX file:", xlsx_url)
```

#### 2. Preserving original file name and preparing storage
We save the file with its original name and ensure the data directory exists:
```python
from pathlib import Path
import os

DATA_DIR = Path("/Users/monika/libraries-data")
DATA_DIR.mkdir(exist_ok=True)

filename = os.path.basename(xlsx_url)
file_path = DATA_DIR / filename
```

#### 3. Downloading the file with change detection
We calculate a SHA-256 hash to check if the file has changed since the last download:
```python
import hashlib

resp = requests.get(xlsx_url)
current_hash = hashlib.sha256(resp.content).hexdigest()
hash_file = DATA_DIR / "last_hash.txt"

if hash_file.exists() and hash_file.read_text() == current_hash:
    print("File has not changed since last download.")
else:
    with open(file_path, "wb") as f:
        f.write(resp.content)
    print("New file saved:", file_path)
    hash_file.write_text(current_hash)
```

#### 4. Handling Excel-specific features
We suppress openpyxl warnings and list defined names in the workbook:
```python
import warnings
from openpyxl import load_workbook

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

wb = load_workbook(file_path, data_only=True)
if wb.defined_names:
    print("\nDefined names in Excel:")
    for name in wb.defined_names.definedName:
        print(" -", name.name, "→", name.attr_text)
```

#### 5. Loading into pandas and exporting to CSV
Finally, we convert the Excel data to CSV for easier analysis:
```python
import pandas as pd

df = pd.read_excel(file_path, engine="openpyxl")
csv_path = file_path.with_suffix(".csv")
df.to_csv(csv_path, index=False, encoding="utf-8")
print("\nExported to CSV:", csv_path)
```

#### 6. Ready for automation
The workflow can be scheduled to run periodically (e.g., via cron on macOS), ensuring the dataset is always up-to-date without manual intervention.
