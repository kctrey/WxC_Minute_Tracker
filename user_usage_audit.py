import os
from dotenv import load_dotenv
import sqlite3
import math
import wxcadm

load_dotenv()
access_token = os.getenv("WEBEX_ACCESS_TOKEN")
if not access_token:
    print("No WEBEX_ACCESS_TOKEN found. Cannot continue.")
    exit(1)

webex = wxcadm.Webex(access_token)
company_spend = 0.000
dbconn = sqlite3.connect('database')
cur = dbconn.cursor()
cur.execute("SELECT DISTINCT user_uuid FROM cdr WHERE call_type = 'SIP_INTERNATIONAL'")
user_rows = cur.fetchall()
for user_row in user_rows:
    print("---------------------------------")
    user_spend = 0.000
    user_uuid = user_row[0]
    person_id = wxcadm.webex_api_call('get', '/v1/people', params={'id': user_uuid})[0]['id']
    person = webex.org.get_person_by_id(person_id)
    print(f"User: {person.email}...")
    cur2 = dbconn.cursor()
    cur2.execute("SELECT * FROM cdr WHERE user_uuid = ? AND call_type = ?", (user_uuid, 'SIP_INTERNATIONAL'))
    calls = cur2.fetchall()
    call_count = len(calls)
    print(f"Number of Intl Calls: {call_count}")
    for call in calls:
        called_num = call[14]
        duration = call[6]
        sql = f"SELECT pattern, country, rate FROM rates WHERE {called_num} LIKE pattern || '%' ORDER BY pattern DESC LIMIT 1"
        cur3 = dbconn.cursor()
        cur3.execute(sql)
        rates_match = cur3.fetchone()
        rate = rates_match[2]
        minutes = math.ceil(duration/60)
        print(f"\t{minutes} minute call to {rates_match[1]} billed at {rate}/min is ${rate * minutes}")
        user_spend += rate * minutes
    print(f"User Spend: ${user_spend}")
    company_spend += float(user_spend)
print("=================================")
print(f"Total Org Spend: ${round(company_spend,3)}")
