# Data Extraction & Basic Transformation
## Scenario and Task
StoryPoints AI processes large-scale clickstream, transaction, and currency conversion data daily. The task is to extract data from multiple sources (CSV files and APIs), apply basic transformations, and store the cleaned datasets into a structured, partitioned GCS bucket.

## Dataset Understanding
- clickstream.csv is a tracking site of pages visited and at what times with location. It has a little over 200k rows
- transactions.csv has records of purchases made in differnt currencies witha little over 100k rows.

## Approach
1. I reviewed the csvs attached and signed up on [exchange rate site](https://app.exchangerate-api.com/dashboard/confirmed) to get an api key for daily exchange rates. I read through the task to understand the deliverables and planned my approach: to get the script to fetch and upload the exchange rates first. Then script the main transform code which will need the earlier uploaded exchange json document.
2. I tested the sample code in the forked github files to see if it could fetch and extract single currrency coversions and this worked. I also created a bucket on the Google Cloud console and set up my CLI to connect with Google Cloud
3. I coded the exchange_rate.py script to be able to get the daily exchange rates and to upload it to the GCS bucket.
4. Wrote the code for the main ETL job in main_etl.py
    - had to review a bit of pandas and using it for data transformation
5. Reviewing and improving code with routines to make it as DRY as possible

