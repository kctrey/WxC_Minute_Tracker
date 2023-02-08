import os
import sqlite3
from dotenv import load_dotenv
import wxcadm

load_dotenv()
access_token = os.getenv("WEBEX_ACCESS_TOKEN")
if not access_token:
    print("No WEBEX_ACCESS_TOKEN found. Cannot continue.")
    exit(1)

webex = wxcadm.Webex(access_token)
cdrs = webex.org.calls.cdr(hours=24)

dbconn = sqlite3.connect('db.sqlite')
for cdr in cdrs:
    print(f"{cdr['Calling number']} -> {cdr['Called number']}")
    if cdr['Call ID'] == '' or cdr['User type'] == 'Place':
        continue
    sql = f"INSERT OR IGNORE INTO cdr (call_id, user_uuid, user_type, location_uuid, location_name, start_time, duration," \
          f"answered, direction, call_type, intl_country, location_timezone, calling_num, dialed_digits, called_num) " \
          f"VALUES ('{cdr['Call ID']}', '{cdr['User UUID']}', '{cdr['User type']}', '{cdr['Site UUID']}', '{cdr['Location']}', " \
          f"'{cdr['Start time']}', {cdr['Duration']}, '{bool(cdr['Answered'])}', '{cdr['Direction']}', '{cdr['Call type']}', " \
          f"'{cdr['International country']}', {cdr['Site timezone']}, '{cdr['Calling number']}', '{cdr['Dialed digits']}', " \
          f"'{cdr['Called number']}')"
    #print(f"SQL: {sql}")
    dbconn.execute(sql)

dbconn.commit()
dbconn.close()
