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
├── *.xlsx # Source Excel files from Ministry of Culture of the Czech Republic
├── *.csv # Exported CSV files
└── README.md # Project description
```

## First Task - Automating Data Collection from the Ministry of Culture
This task demonstrates an approach to automatically download and manage data from the Ministry of Culture of the Czech Republic, ensuring that the latest information on registered libraries is always available for analysis. The workflow ensures that the latest Excel file is always available, changes are detected, and the data is converted for further analysis.

### Data Collection:
All functionality is implemented in a Python script called:
```shell
download_libraries.py
```

In this case, the script stores downloaded files in the same directory as the script is located.

This script ensures automatic downloading, change detection, and conversion of the dataset on registered libraries.

```bash
# Each run of the script produces the following files inside libraries-data/:

├── evidence-knihoven-06082025-20693.xlsx   # original Excel file from the Ministry
├── evidence-knihoven-06082025-20693.csv    # CSV file converted from Excel
└── last_hash.txt                           # hash file for change detection
```

The script is divided into several logical steps, which are described below together with code snippets. Each snippet comes directly from the script:

#### 1. Fetching the web page and locating the XLSX file
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

#### 2. Preparing storage and preserving original file names
The script preserves the original file name from the Ministry’s website.
```python
DATA_DIR = Path(".")
DATA_DIR.mkdir(exist_ok=True)

filename = os.path.basename(xlsx_url)
file_path = DATA_DIR / filename
```

#### 3. Downloading the file with change detection
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

#### 4. Handling Excel-specific features
The Ministry’s Excel files may contain defined names (print areas, table references, etc.). The script suppresses warnings and prints out these definitions.
```python
wb = load_workbook(file_path, data_only=True)
if wb.defined_names:
    print("\nDefined names in Excel:")
    for name in wb.defined_names.definedName:
        print(" -", name.name, "→", name.attr_text)
```

#### 5. Exporting data to CSV
Finally, the data is loaded into pandas and exported as a CSV file with the same name as the Excel file. The `|` character was used as a field separator.
```python
df = pd.read_excel(file_path, engine="openpyxl")
csv_path = file_path.with_suffix(".csv")
df.to_csv(csv_path, index=False, sep="|", encoding="utf-8")
print("Exported to CSV:", csv_path)
```

#### 6. Ready for automation
The workflow can be scheduled to run periodically (e.g. macOS/Linux cron), ensuring the dataset is always up-to-date without manual intervention.

### Automation with Cron:
Once the Python script (download_table.py) was created and tested, the next step was to ensure that it can run automatically without manual execution.
For our purposes, we use cron, a standard scheduler available on Unix-based systems (macOS, Linux).

We defined the following cron job to run the script every 5 minutes:
```bash
*/5 * * * * cd /path/to/libraries-data && echo "=== $(date) ===" >> cron_log.txt && /usr/bin/python3 download_table.py >> cron_log.txt 2>&1
```

Explanation:
* `*/5 * * * *` → runs the job every 5 minutes.
* cd /path/to/libraries-data → navigates to the folder where the script and data files are stored (replace /path/to/ with your actual directory).
* echo "=== $(date) ===" >> cron_log.txt → logs the current timestamp before each run.
* /usr/bin/python3 download_table.py → executes the script with Python (use the full path to your Python installation if needed).
* \>\> cron_log.txt 2>&1 → appends both script output and errors into a log file named cron_log.txt.

Every 5 minutes, the cron job checks for updates in the dataset. If the file has changed, it downloads the new Excel file, converts it to CSV, and updates the hash file. All activities (including timestamps, successful runs, or potential errors) are stored in cron_log.txt for later inspection.

For demonstration purposes, we scheduled the script to run every 5 minutes. In a real-world setup, a less frequent interval (e.g., once per day or once per week) is more practical, depending on how often the source data is updated.

## Second Task - Data Transformation and Interoperability
When working with datasets such as the national register of libraries, different levels of transformation can be applied depending on the intended use. For example, special characters for the Czech language like diacritics may be incompatible with some tools and databases. We can remove these characters with python script 

```bash
convert_to_ascii.py
```

which converts text encoding (from UTF-8 to ASCII) which can be run as follows:

```bash
python3 convert_to_ascii.py evidence-knihoven-06082025-20693.csv evidence-knihoven-06082025-20693_ascii.csv
```

The python scipt prodices ascii-converted csv file `evidence-knihoven-06082025-20693_ascii.csv` in the same directory whete is the executed python script.

Furthermore can be necessary to extract some partial data, e.g. selected columns. It can be done with standard UNIX command `awk`. For example, we can pick up all libraries, their postal codes and regions.

```bash
awk -F '|' '{print $12,$17,$20}' evidence-knihoven-06082025-20693_ascii.csv
```

The produced output can be further modified and then convert into JSON-LD format or into format suitable for any other database usage. 

## Third Task - Permanent and Secure Storage

* Backup on a university server or cloud storage (e.g. CESNET data storage)
* Versioning within a Git repository (e.g., GitHub) to capture changes over time.

## Fourth Task - Dataset Description According to the Czech Core Metadata Model (CCMM)
CCMM (Czech Core Metadata Model) is a very new standard that defines what information (described as classes and subclasses) must be provided about a dataset so that both people and machines can easily find and use it. Model is described on https://github.com/techlib/CCMM/tree/main?tab=readme-ov-file

For our example we can create a short metadata desription as follows:

* **<title>** e.g., “Registry of Libraries Registered by the Czech Ministry of Culture”
* **<description_text>** A dataset containing information about libraries officially registered by the Czech Ministry of Culture, including their names, addresses, and types.
* **<time_reference>** Current registry (snapshot as of 06082025)
* **<resource_url>** [link to download the dataset](https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341)

Created metada will be put in the head of the JSON-LD file we already created with the library data.





