import os
import sqlite3
from dotenv import load_dotenv
import wxcadm

load_dotenv()
access_token = os.getenv("WEBEX_ACCESS_TOKEN")
db_file = os.getenv("DB_FILE", "db.sqlite")
cdr_hours = os.getenv("CDR_HOURS", 25)
print(f"Using Database: {db_file}")
if not access_token:
    print("No WEBEX_ACCESS_TOKEN found. Cannot continue.")
    exit(1)

webex = wxcadm.Webex(access_token)
try:
    cdrs = webex.org.calls.cdr(hours=int(cdr_hours))
except wxcadm.APIError:
    print("No CDRs returned")
    exit()

dbconn = sqlite3.connect(db_file)
for cdr in cdrs:
    print(f"{cdr['Calling number']} -> {cdr['Called number']}")
    if cdr['Call ID'] == '' or cdr['User type'] == 'Place':
        continue
    sql = """
        INSERT OR IGNORE INTO cdr (
            call_id, 
            user_uuid, 
            user_type, 
            location_uuid, 
            location_name,
            start_time, 
            duration, 
            answered, 
            direction, 
            call_type, 
            intl_country, 
            location_timezone, 
            calling_num, 
            dialed_digits, 
            called_num
        )
        VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    dbconn.execute(sql, (
        cdr['Call ID'],
        cdr['User UUID'],
        cdr['User type'],
        cdr['Site UUID'],
        cdr['Location'],
        cdr['Start time'],
        cdr['Duration'],
        cdr['Answered'],
        cdr['Direction'],
        cdr['Call type'],
        cdr['International country'],
        cdr['Site timezone'],
        cdr['Calling number'],
        cdr['Dialed digits'],
        cdr['Called number']
    ))

dbconn.commit()
dbconn.close()
