import os
from dotenv import load_dotenv
import camelot
import sqlite3
import requests


def get_rate_sheet(remote_file: str, local_file: str):
    response = requests.get(remote_file)
    with open(local_file, "wb") as f:
        f.write(response.content)


def process_rate_sheet(local_file: str):
    # Process the downloaded `PDF and insert the data into the database
    # TODO: Right now we handle one format of the document. Error-handling should be added in case the format changes
    db_file = os.getenv("DB_FILE", "db.sqlite")
    tables = camelot.read_pdf(local_file, flavor='stream', pages='2-end')

    country = ""
    rate = ""
    start_record_found = False
    found_patterns = []
    dbconn = sqlite3.connect(db_file)
    for table in tables:
        frame = table.df
        for index, row in frame.iterrows():
            if len(row) == 3 and '$' in row[2]:
                rate = float(row[2].replace('$', ''))
            if row[0] and row[0] != 'Country':
                country = row[0]
                if country == 'Afghanistan':
                    start_record_found = True
            if start_record_found is True:
                patterns = row[1].split(", ")
                for pattern in patterns:
                    if pattern != 'Destination code' and pattern != '':
                        pattern = pattern.replace(',', '')
                        pattern = pattern.replace(' ', '')
                        if pattern in found_patterns:
                            print(f"Duplicate pattern {pattern} found. Unsure how to proceed.")
                            exit()
                        else:
                            found_patterns.append(str(pattern))
                        print(country, pattern, rate)
                        sql = f"INSERT INTO rates (pattern, country, rate) VALUES (?, ?, ?)"
                        dbconn.execute(sql, (pattern, country, rate))

    dbconn.commit()
    dbconn.close()


def main():
    load_dotenv()
    remote_file = os.getenv(
        "RATE_SHEET_URL",
        "https://www.webex.com/content/dam/wbx/us/documents/pdf/us-international-rates.pdf"
    )
    local_file = os.getenv("LOCAL_RATE_SHEET", "us-international-rates.pdf")
    print("Downloading rate sheet")
    get_rate_sheet(remote_file, local_file)
    print("Processing rate sheet")
    process_rate_sheet(local_file)
    print("Done")


if __name__ == '__main__':
    main()
