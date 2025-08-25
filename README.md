# Registered Libraries – Data for MUNI
This readme was created by Monika Suszkova

## Description
The aim of this repository is to showcase how to download and manipulate data for ECON MUNI usage.  
The source data are provided by the Ministry of Culture of the Czech Republic and relate to the database of all registered libraries in the country.  

- Official dataset: [Evidence knihoven – Ministry of Culture](https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341)

## Repository Structure
```markdown
/libraries-data
├── download_libraries.py # Python script to download and process XLSX data
├── last_hash.txt # Stores hash of the last downloaded file
├── *.xlsx # Source Excel files from MK CR
├── *.csv # Exported CSV files
└── README.md # Project description
```

## First Task - Automating Data Collection from the Ministry of Culture
This task demonstrates an approach to automatically download and manage data from the Ministry of Culture of the Czech Republic, ensuring that the latest information on registered libraries is always available for analysis.

### Implementation
This task demonstrates how to automatically download and process the latest data on registered libraries from the Ministry of Culture of the Czech Republic. The workflow ensures that the latest Excel file is always available, changes are detected, and the data is converted for analysis.

#### Data Collection:
All functionality is implemented in a Python script called:
```shell
download_libraries.py
```

The script stores downloaded files in the same directory as the script.

This script ensures automatic downloading, change detection, and conversion of the dataset on registered libraries provided by the Ministry of Culture of the Czech Republic.

```bash
# Each run of the script produces the following files inside libraries-data/:

├── evidence-knihoven-06082025-20693.xlsx   # original Excel file from the Ministry
├── evidence-knihoven-06082025-20693.csv    # CSV file converted from Excel
└── last_hash.txt                           # hash file for change detection
```

The script is divided into several logical steps, which are described below together with code snippets. Each snippet comes directly from the script:

##### 1. Fetching the web page and locating the XLSX file
First, the script downloads the HTML page and finds the link to the most recent Excel file published by the Ministry.
```python
resp = requests.get(BASE_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

xlsx_links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".xlsx")]
xlsx_url = xlsx_links[0]
if not xlsx_url.startswith("http"):
    xlsx_url = "https://mk.gov.cz" + xlsx_url

print("Found XLSX file:", xlsx_url)
```

##### 2. Preparing storage and preserving original file names
All downloaded files are saved in the directory:
```bash
/Users/monika/libraries-data
```

The script preserves the original file name from the Ministry’s website.
```python
DATA_DIR = Path("/Users/monika/libraries-data")
DATA_DIR.mkdir(exist_ok=True)

filename = os.path.basename(xlsx_url)
file_path = DATA_DIR / filename
```

##### 3. Downloading the file with change detection
To avoid storing duplicates, the script computes a SHA-256 hash of the file. If the file is unchanged since the last run, it is not downloaded again.
```python
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

##### 4. Handling Excel-specific features
The Ministry’s Excel files may contain defined names (print areas, table references, etc.). The script suppresses warnings and prints out these definitions.
```python
wb = load_workbook(file_path, data_only=True)
if wb.defined_names:
    print("\nDefined names in Excel:")
    for name in wb.defined_names.definedName:
        print(" -", name.name, "→", name.attr_text)
```

##### 5. Exporting data to CSV
Finally, the data is loaded into pandas and exported as a CSV file with the same name as the Excel file.
```python
df = pd.read_excel(file_path, engine="openpyxl")
csv_path = file_path.with_suffix(".csv")
df.to_csv(csv_path, index=False, encoding="utf-8")
print("\nExported to CSV:", csv_path)
```

##### 6. Ready for automation
The workflow can be scheduled to run periodically (e.g., GitHub Actions, CI/CD pipelines, Windows Task Scheduler, macOS/Linux cron), ensuring the dataset is always up-to-date without manual intervention.

#### Automation with Cron:
Once the Python script (download_table.py) was created and tested, the next step was to ensure that it can run automatically without manual execution.
For our purposes, we use cron, a standard scheduler available on Unix-based systems (macOS, Linux).

We defined the following cron job to run the script every 5 minutes:
```bash
*/5 * * * * cd /path/to/libraries-data && echo "=== $(date) ===" >> cron_log.txt && /usr/bin/python3 download_table.py >> cron_log.txt 2>&1
```

Explanation:
* */5 * * * * → runs the job every 5 minutes.
* cd /path/to/libraries-data → navigates to the folder where the script and data files are stored (replace /path/to/ with your actual directory).
* echo "=== $(date) ===" >> cron_log.txt → logs the current timestamp before each run.
* /usr/bin/python3 download_table.py → executes the script with Python (use the full path to your Python installation if needed).
* \>\> cron_log.txt 2>&1 → appends both script output and errors into a log file named cron_log.txt.

Every 5 minutes, the cron job checks for updates in the dataset. If the file has changed, it downloads the new Excel file, converts it to CSV, and updates the hash file. All activities (including timestamps, successful runs, or potential errors) are stored in cron_log.txt for later inspection.

For demonstration purposes, we scheduled the script to run every 5 minutes. In a real-world setup, a less frequent interval (e.g., once per day or once per week) would be more practical, depending on how often the source data is updated.

## Second Task - Data Transformation and Interoperability
When working with datasets such as the national register of libraries, different levels of transformation can be applied depending on the intended use. Below we outline three levels – from basic cleaning to advanced interoperability with other data sources.

### 1. Basic cleaning and normalization
* UTF-8 encoding for proper handling of Czech characters.
* Remove duplicates and invalid records.
* Standardize column names (e.g., library_name, municipality_code, ico).
* Convert Excel files to CSV for easier reuse.

### 2. Improving interoperability with other data sources
* Geocode addresses into latitude and longitude.
* Structure addresses into Street, House Number, Postal Code, City, Region.
* Use standardized geographic codes (RÚIAN IDs, NUTS/LAU codes).
* Add official identifiers: IČO, ISIL, and optionally Wikidata Q-ID.

### 3. Publishing as open data
* Export into machine-readable formats: CSV, JSON, GeoJSON, RDF.
* Add persistent IDs (UUIDs or Wikidata links).
* Include metadata: source, date of download, license.

## Third Task - Permanent and Secure Storage
### 1. Short-term storage:
* Versioning within a Git repository (e.g., GitHub, GitLab) to capture changes over time.

### 2. Long-term storage:
* Store in a database (e.g., PostgreSQL with PostGIS extension for spatial data).
* Backup on a university server or cloud storage (e.g., Ceph, S3-compatible storage).
* Implement access controls, audit logs, and regular snapshots.

### 3. Persistent identifiers:
* Assign a DOI or Handle to the dataset (e.g., using Dataverse or Zenodo) to ensure long-term citability.

## Fourth Task - Dataset Description According to the Czech Core Metadata Model (CCMM)
CCMM is based on DCAT-AP and Dublin Core.

Essential metadata to provide:
* **Dataset title:** e.g., “Registry of Libraries Registered by the Czech Ministry of Culture”
* **Description:** Brief summary of content, purpose, and provenance
* **Provider:** Czech Ministry of Culture
* **Dataset manager:** University or faculty responsible within the project
* **Publication and update dates**
* **Format:** CSV, JSON, RDF, XLSX
* **License:** e.g., Creative Commons BY 4.0 (if allowed by the source)
* **Geographic coverage:** Czech Republic
* **Temporal coverage:** if the dataset is versioned
* **Distribution URL:** link to download the dataset

Recommendation:
* Create metadata in JSON-LD or RDF format to ensure machine readability.





