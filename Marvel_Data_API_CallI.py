import hashlib
import time
import requests
import datetime
import pandas as pd
import sqlite3
import os
from marvel import Marvel
import streamlit as st
import pandas as pd
import io
import subprocess

def hash_params(itimestap, ikey_private, ikey_public):
    #Marvel API requires server side API calls to include md5 hash of timestamp + public key + private key
    #Buildup hashed paramter that's required by the website for api calls
    hash_md5 = hashlib.md5()
    hash_md5.update(f'{itimestap}{ikey_private}{ikey_public}'.encode('utf-8'))
    hashed_params = hash_md5.hexdigest()

    return hashed_params

def api_parameters_buildup(itimestap,ikey_private,ikey_public):
    #Buildup hash
    hash = hash_params(itimestap,ikey_private,ikey_public)
    
    #Buildup paramters for api call
    params = {
                'ts': itimestap, 
                'apikey': ikey_public, 
                'hash': hash,
                'limit' : 100,
                'offset' : 0
            };
    
    return params

def get_api_call_characters(imarvel_api_character_url,iparams):
    #Make the get call to get character data
    result = requests.get(imarvel_api_character_url, params=iparams)
    return result

def get_all_characters(imarvel_api_character_url,iparams,iworking_directory):
    #Offest for API pagination due to api call limited to 100 request at a time
    offset = 0

    #Total characters
    total = 1

    #loop to get all characters
    while offset < total:
        #Add small delay for rate limiting
        time.sleep(1)
        
        #Offset to get next set of values
        iparams["offset"] = offset

        #Get the list of characters and store it in results variable
        response = get_api_call_characters(imarvel_api_character_url,iparams)
        data = response.json()

        #Check if response has data
        if "data" in data:
            #Get the total characters count
            total = data["data"]["total"]

            # Extract character list
            results = data["data"]["results"]  

            #Extract only needed information
            characters = [
                (char["id"], char["name"], char["comics"]["available"])
                for char in results
            ]

            #Load feteched data into database
            load_data_into_database(characters,iworking_directory)

            #Dsiplay fetched results
            print(f"Fetched {offset + len(results)} : {total} total characters")


            #increase offset to get next batch
            offset += 100
        else:
            #Display any errors during call
            print(f"Error: {response.status_code}, {response.text}")
            break
    
def load_data_into_database(i_data_char,iworking_directory):
    #Create database connection
    conn = sqlite3.connect(iworking_directory + "marvel_characters.db")
    cursor = conn.cursor()

    #Create table if it does not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        name TEXT,
        comics_available INTEGER
    )
    """)

    
    # Insert characters into the database
    cursor.executemany("INSERT OR IGNORE INTO characters (id, name, comics_available) VALUES (?, ?, ?)", i_data_char)

    #Commit and close database connection
    conn.commit()
    conn.close()

def database_clean(iworking_directory):
    #Path to SqlLite database
    db_path = iworking_directory + "marvel_characters.db"

    #Check if the file exists, then delete it
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Database '{db_path}' deleted successfully!")
    else:
        print(f"Database '{db_path}' does not exist.")    

def database_read(iworking_directory):
    #print All Cahracter Data
    print(f"Display All characters")
    
    #Create database connection
    conn = sqlite3.connect(iworking_directory + "marvel_characters.db")
    cursor = conn.cursor()

    #Query all character data
    cursor.execute("SELECT id, name, comics_available FROM characters")
    rows = cursor.fetchall()

    #Output data
    for row in rows:
        print(f"Character name: {row[1]}, quantity of comics they appear in: {row[2]}")

    #Close database connection
    conn.close()

def integrity_checks(ikey_private, ikey_public,iworking_directory,irows_to_Check):
    #Pirnt data integrity checks
    print(f"Start data integrity checks")

    #Initate rows check
    rows_matching = 0

    #Create marvel api call using marvel module
    marvel = Marvel(ikey_public, ikey_private)

    #Connect to local db
    conn = sqlite3.connect(iworking_directory + "marvel_characters.db")
    cursor = conn.cursor()

    #Buildup query for data check
    query = "SELECT id, name, comics_available FROM characters limit " + str(irows_to_Check)

    #Run query
    cursor.execute(query)
    #Get rows
    rows = cursor.fetchall()

    #Loop through query results
    for row in rows:
        #Assing each column to a varaible for ease of use
        character_id = row[0]
        character_name = row[1]
        character_comics_count = row[2]

        #Get cahrtaccter data for certain character by uisng the assinged character id
        character_data = marvel.characters.get(character_id)
        
        #Check if character has data
        if "data" in character_data and "results" in character_data["data"]:
            #Get the data for api call
            character = character_data["data"]["results"][0]
            
            #Lookup comic book count
            api_comics_count = character["comics"]["available"]
        
        
        #Display lookup results
        print(f"For {character_name} database value: {character_comics_count} vs marvel api value: {api_comics_count}")

        #Check if databse and api call counts match and add to final count
        if(character_comics_count == api_comics_count):
            rows_matching = rows_matching + 1
    
    #Check data integrity
    if(rows_matching == irows_to_Check):
        print(f"Data integrity verified matched {rows_matching} of {irows_to_Check}")
    else:
        print(f"Data integrity not verified matched {rows_matching} of {irows_to_Check}")

def report_builder(iworking_directory):
    streamlit_code = f"""
import streamlit as st
import sqlite3
import pandas as pd
import io

#Set web page Title

st.set_page_config(page_title="Marvel Character Data", layout="wide")

#Path to database
path_db = "{iworking_directory}marvel_characters.db"

#Get table data dynamically
@st.cache_data
def get_table_names():
    conn = sqlite3.connect(path_db)
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(tables_query, conn)
    conn.close()
    return tables["name"].tolist() if not tables.empty else []

#Get all table names    
tables = get_table_names()

#Tables exists generate report
if tables:
    selected_table = st.sidebar.selectbox("Select a Table", tables)

    @st.cache_data
    def load_data(table_name):
        conn = sqlite3.connect(path_db)
        query = f"SELECT * FROM {{table_name}}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    df = load_data(selected_table)

    st.title(f"Marvel Report for `{{selected_table}}`")

    st.sidebar.header("Filters")
    columns = df.columns.tolist()

    filtered_df = df.copy()

    for column in columns:
        if df[column].dtype == "object":
            unique_values = df[column].dropna().unique().tolist()
            selected_value = st.sidebar.multiselect(f"Filter {{column}}:", unique_values)
            if selected_value:
                filtered_df = filtered_df[filtered_df[column].isin(selected_value)]
        else:
            min_value, max_value = df[column].min(), df[column].max()
            range_values = st.sidebar.slider(f"Filter {{column}}:", min_value, max_value, (min_value, max_value))
            filtered_df = filtered_df[(filtered_df[column] >= range_values[0]) & (filtered_df[column] <= range_values[1])]

    st.write("Filtered Data")
    st.dataframe(filtered_df)

    csv = filtered_df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "filtered_marvel_character_data.csv", "text/csv")

    excel_buffer = io.BytesIO()
    filtered_df.to_excel(excel_buffer, index=False, engine="xlsxwriter")
    excel_buffer.seek(0)

    st.download_button(
        label="Download Excel",
        data=excel_buffer,
        file_name="filtered_marvel_character_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("No tables found in the database.")
"""
    
    # Define the filename for the dynamically created report
    report_filename = "Marvel_Data_API_CallI.py"

    # Write the Streamlit script to a file
    with open(report_filename, "w") as f:
        f.write(streamlit_code)

    print(f"Streamlit report '{report_filename}' generated successfully.")

    # Step 2: Run the Streamlit script dynamically
    subprocess.run(["streamlit", "run", report_filename])

def main():
    #Timestamp in format Year-month-date hour:minute:seconds example 2025-03-0815:15:28
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')

    #Your public key
    key_public = '54c6b20d3c40292d220952da6456d8c3'

    #Your Private key
    key_private = '57954991457055ade9f281dc6c47726f8f6c89c9'

    #marvel base url
    marvel_api_url_base = 'https://gateway.marvel.com:443'

    #character api url
    marvel_api_url_character = marvel_api_url_base + '/v1/public/characters'

    #path to solution directory
    working_directory = "C:\\Files\\Interview\\Blue Harvest\\"

    try:
        #clean database
        database_clean(working_directory)

        #paramter buildup
        params = api_parameters_buildup(timestamp,key_private,key_public)
        
        #Get all characters
        get_all_characters(marvel_api_url_character,params,working_directory)

        #Display all results
        database_read(working_directory)

        #Perform integrity checks
        integrity_checks(key_private,key_public,working_directory,15)

        #Build dynamic report using streamlit need to run streamlit run working_directory
        print(f"Once done running command press CTRL + C to close report") 
        report_builder(working_directory)



    except Exception as e:
        #print out any errors for debugging
        print(f'Encountered erorr {e}')

main()