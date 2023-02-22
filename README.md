WxC Minute Tracker
==================
Purpose
-------
These scripts are an example of what can be done with the Webex Calling Real-Time CDR API in conjunction with external
data (i.e. PSTN rate tables). The use case for this particular example is a Webex Calling Organization that wants to
track the PSTN spending of each user when they dial from the United States to an International country. It is made up
of three (3) individual Python scripts:

* ``rate_table_builder.py`` - Fetches the Cisco Calling Plans U.S. International Rate table PDF and extracts the rate table
into an SQLite3 database. This script is designed to be run periodically (e.g. weekly, monthly) to ensure the rate table
if up to date.
* ``cdr_collector.py`` - Uses the Webex Real-Time CDR API to collect CDRs from the last X hours and store them in the
SQLite3 database. This script is designed to be run daily, and the number of hours of CDRs to retrieve is controlled
with the .env file
* ``user_usage_audit.py`` - Searches the CDRs for International calls and uses the rate table to calculate the cost
of each. It then groups the calls by user and reports the number and cost of each call along with a total spent by the
user. This script is design to be run on-demand when a report is needed. The output appears as follows:

``` text
User: user1@domain.com
Number of Intl Calls: 3
	1 minute call to United Kingdom billed at 0.01288/min is $0.01288
	1 minute call to Italy billed at 0.50071/min is $0.50071
	1 minute call to Italy billed at 0.50071/min is $0.50071
User Spend: $1.0143
---------------------------------
User: user2@domain.com
Number of Intl Calls: 1
	3 minute call to Singapore billed at 0.046/min is $0.138
User Spend: $0.138
=================================
Total Org Spend: $1.152
```

Installation
------------
The scripts are ready to run as-is. Simply download or clone the ``master`` branch. Once downloaded, rename the
``.env.example`` file to ``.env`` and set the correct variables. The only .env variable that **must** be defined is the
``WEBEX_ACCESS_TOKEN``, which must be set to a valid access token that has the Real-Time CDR roles and permissions.

Obtaining an access token is beyond the scope of this example. Information regarding token and Integrations can be
found at https://developer.webex.com/docs/integrations.

Quickstart
----------
Once the files have been downloaded and the ``.env`` file has been updated with a valid access token, the following
procedure will allow the scripts to be run and tested.

1. Run ``rate_table_builder.py`` and ensure there are no errors. The output will show all of the International country
dialing codes and their associated rate.
2. Ensure an International call has been placed within the past 24 hours, and longer than 5 minutes ago. This is needed
to ensure that the CDR is present and the following tests will report data
3. Run ``cdr_collector.py`` and ensure there are no errors. This is the script that is most likely to fail, because it
is the only one that calls the Webex APIs and requires the Webex access token to be configured properly.
    * If the script fails, the error should indicate the cause of the problem. Most likely you will have to adjust the
Integration or User settings to allow the right access levels.
4. Run ``user_usage_audit.py`` and ensure the output shows the International call(s) that are expected.

Once you are satisfied that the scripts work as expected, most admins will want to set up the following "cron jobs",
running some scripts at pre-defined intervals.

* ``rate_table_builder.py`` - Monthly on the 1st of the month
* ``cdr_collector.py`` - Nightly, usually 00:00, every day

When a report is needed, simply run ``user_usage_audit.py``.