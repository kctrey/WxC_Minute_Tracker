import camelot
import sqlite3

file = "us-international-rates.pdf"

tables = camelot.read_pdf(file, flavor='stream', pages='2-end')

country = ""
rate = ""
start_record_found = False
found_patterns = []
dbconn = sqlite3.connect('database')
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