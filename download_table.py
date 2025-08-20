import requests
from bs4 import BeautifulSoup
import hashlib
from pathlib import Path
import pandas as pd
import os
import warnings
from openpyxl import load_workbook

# ignore openpyxl warnings (print area, Tabulka1[#All], etc.)
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

BASE_URL = "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341"

DATA_DIR = Path("/Users/monika/libraries-data")
DATA_DIR.mkdir(exist_ok=True)

# download the HTML page
resp = requests.get(BASE_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# find link to .xlsx
xlsx_links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".xlsx")]
if not xlsx_links:
    raise Exception("No XLSX link found on the page.")

xlsx_url = xlsx_links[0]
if not xlsx_url.startswith("http"):
    xlsx_url = "https://mk.gov.cz" + xlsx_url

print("Found XLSX file:", xlsx_url)

# download the XLSX file
resp = requests.get(xlsx_url)
resp.raise_for_status()

# use the original file name from the URL
filename = os.path.basename(xlsx_url)
file_path = DATA_DIR / filename

# hash for change detection
current_hash = hashlib.sha256(resp.content).hexdigest()
hash_file = DATA_DIR / "last_hash.txt"

if hash_file.exists() and hash_file.read_text() == current_hash:
    print("File has not changed since last download.")
else:
    with open(file_path, "wb") as f:
        f.write(resp.content)
    print("New file saved:", file_path)

    hash_file.write_text(current_hash)

    # --- list defined names in Excel workbook ---
    wb = load_workbook(file_path, data_only=True)
    if wb.defined_names:
        print("\nDefined names in Excel:")
        for name in wb.defined_names.definedName:
            print(" -", name.name, "→", name.attr_text)

    # load into pandas and export to CSV
    df = pd.read_excel(file_path, engine="openpyxl")
    csv_path = file_path.with_suffix(".csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print("\nExported to CSV:", csv_path)

