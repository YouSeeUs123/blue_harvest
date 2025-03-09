# Marvel Character Data API Fetcher & Report Generator

This project fetches Marvel character data using the **Marvel API**, stores it in a **SQLite database**, and generates an interactive **Streamlit dashboard** for visualization and reporting.

## Features
- **Marvel API Integration**: Fetches character data, including names and comic appearances.
- **SQLite Database Storage**: Saves data locally to `marvel_characters.db`.
- **Data Integrity Check**: Verifies stored data against real-time API data for a few records.
- **Dynamic Streamlit Report**: Generates an interactive dashboard for data exploration.
- **Downloadable Reports**: Export data as CSV or Excel from the streamlit report.

---

## Installation
### 1. Clone the Repository
```sh
git clone https://github.com/YouSeeUs123/blue_harvest.git
cd marvel-character-report
```

### 2. Install Dependencies
Ensure you have Python **3.x** installed. Install required packages:
```sh
pip install -r requirements.txt
```
If `requirements.txt` is missing, install manually:
```sh
pip install requests pandas sqlite3 streamlit xlsxwriter marvel
```

### 3. Get Your Marvel API Keys
Sign up at [Marvel Developer Portal](https://developer.marvel.com/) to get:
- **Public Key**
- **Private Key**

Set these values inside `main()` in `Marvel_Data_API_CallI.py`:
```python
key_public = 'your_public_key'
key_private = 'your_private_key'
```

---

## Usage
### 1. Update variables in main method before running
```sh
python Marvel_Data_API_CallI.py
```
This will:
1. Fetch all Marvel characters from the API.
2. Store them in `marvel_characters.db`.
3. Display all db results
4. Perform data integrity checks.
5. Generate streamlit report

---

## Features in the Streamlit Report
- **Table Selection:** Choose different tables from the database.
- **Filtering:** Apply filters based on character names and comic appearances.
- **Data Export:** Download **filtered data** as CSV or Excel.
- **Interactive UI:** Built using Streamlit for easy data analysis.

---

## Project Structure
```
📂 marvel-character-report
│── Marvel_Data_API_CallI.py    # Main script for API calls & reporting
│── requirements.txt            # Dependencies
│── README.md                   # This documentation
│── marvel_characters.db         # SQLite database (auto-generated)
```

---

## Notes & Limitations
- **API Rate Limits**: The Marvel API limits 100 results per requests . The script includes a delay to handle this and pagenation.
- **Data Accuracy**: The script verifies integrity using a subset of the data.

---

## To-Do List (Future Improvements)
- Fetch and store all Marvel comics  
- Implement data better integrity checks  
- Enhance UI with visualization charts  
- Add character images from API  

---

## Contributing
Want to improve this project? Feel free to fork and submit a pull request.

---

## License
This project is open-source under the **MIT License**.

---

## Contact
If you have questions or suggestions, reach out via GitHub Issues or email.

