# 1. Import Libraries
import pandas as pd
import logging
from google.colab import files
import os
from datetime import datetime

# 2. Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 3. File Upload
def upload_file():
    uploaded = files.upload()
    for fn in uploaded.keys():
        logging.info(f'Uploaded file "{fn}" with length {len(uploaded[fn])} bytes')
    return uploaded

def read_file_to_dataframe(uploaded_file):
    import io
    df = pd.read_csv(io.BytesIO(uploaded_file))
    return df

# 4. Data Reading
def get_data():
    uploaded = upload_file()
    for fn in uploaded.keys():
        return read_file_to_dataframe(uploaded[fn])
    return None

# 5. Name Parsing Function
def parse_name(full_name):
    organization_keywords = [
        "corp", "corporation", "inc", "company", "co", "limited", "ltd", "incorporated", "plc", "corporate",
        "LLC", "LC", "limited liability company", "LLP", "LP", "partnership",
        "foundation", "trust", "nonprofit", "association", "committee",
        "church", "temple", "mosque", "synagogue", "ministry",
        "school", "university", "college", "institute", "academy",
        "department", "agency", "bureau", "office", "commission",
        "club", "society", "union", "organization", "group", "board", "council", "league", "bank"
    ]

    estate_keywords = ["deceased", "estate", "et al", "deceased estate", "personal representative", "representative"]

    parts = full_name.split()
    estate_part = ""

    if any(keyword.lower() in full_name.lower() for keyword in organization_keywords):
        return "", "", full_name, estate_part

    for keyword in estate_keywords:
        if keyword.lower() in full_name.lower():
            estate_part = " ".join([word for word in parts if keyword.lower() in word.lower()])
            parts = [word for word in parts if keyword.lower() not in word.lower()]
            break

    first_name, middle_name, last_name = "", "", ""
    if len(parts) == 1:
        last_name = parts[0]
    elif len(parts) == 2:
        last_name, first_name = parts
    elif len(parts) >= 3:
        last_name = parts[0]
        first_name = parts[1]
        if len(parts) == 3:
            middle_name = parts[2]
        else:
            middle_name = " ".join(parts[2:])

    return first_name, middle_name, last_name, estate_part

# Parse Multiple Owner Names Function
def parse_names(full_name):
    owners = full_name.split("&")
    if len(owners) == 1:
        owners = full_name.split(",")
    
    owners = [owner.strip() for owner in owners]

    if len(owners) == 2:
        owner1, owner2 = owners
        
        first_name1, middle_name1, last_name1, estate1 = parse_name(owner1)
        parts_owner2 = owner2.split()

        if len(parts_owner2) == 1:
            first_name2 = parts_owner2[0]
            middle_name2 = ""
            last_name2 = last_name1
        elif len(parts_owner2) == 2:
            if len(parts_owner2[1]) == 1 or (len(parts_owner2[1]) == 2 and parts_owner2[1][1] == "."):
                first_name2, middle_name2 = parts_owner2
                last_name2 = last_name1
            else:
                first_name2 = parts_owner2[1]
                middle_name2 = ""
                last_name2 = parts_owner2[0]
        else:
            first_name2, middle_name2 = parts_owner2[1], " ".join(parts_owner2[2:])
            last_name2 = parts_owner2[0]

        return first_name1, middle_name1, last_name1, estate1, first_name2, middle_name2, last_name2, estate1
    else:
        first_name1, middle_name1, last_name1, estate1 = parse_name(owners[0])
        return first_name1, middle_name1, last_name1, estate1, "", "", "", ""


# 6 Processing Names in DataFrame
def process_names(df, column_number):
    parsed_data = df.iloc[:, column_number].map(parse_names)
    df['First Name 1'], df['Middle Name 1'], df['Last Name 1'], df['Estate 1'], df['First Name 2'], df['Middle Name 2'], df['Last Name 2'], df['Estate 2'] = zip(*parsed_data)
    return df

# 7. Deduplication
def remove_duplicates(df):
    return df.drop_duplicates()

# 8. Save Output
def save_output(df):
    current_time = datetime.now().strftime('%H:%M:%S')
    filename = f"Lis Pendens Parsed Names {current_time}.csv"
    df.to_csv(filename, index=False)
    file_size = os.path.getsize(filename)
    logging.info(f'File "{filename}" was saved at {current_time} with size {file_size} bytes')
    return filename

# 9. Frequency Calculation and Identification of Potential Issues
def analyze_names(df):
    first_name_counts = df['First Name 1'].value_counts()
    last_name_counts = df['Last Name 1'].value_counts()
    df['Potential Issue'] = df['First Name 1'].isin(last_name_counts.index) & ~df['Last Name 1'].isin(first_name_counts.index)
    return df

# Main Execution Flow
def main():
    logging.info("Starting the name parsing script.")
    df = get_data()
    if df is not None:
        column_number = int(input("Enter the column number containing the names (starting from 0): "))
        df = process_names(df, column_number)
        df = remove_duplicates(df)

        # Analyze and flag potential issues
        df = analyze_names(df)

        filename = save_output(df)
        logging.info("Script completed successfully.")
    else:
        first_name1, middle_name1, last_name1, estate1 = parse_name(owners[0])
        return first_name1, middle_name1, last_name1, estate1, "", "", "", ""

main()
