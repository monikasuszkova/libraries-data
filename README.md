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

