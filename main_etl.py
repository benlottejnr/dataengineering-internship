import pandas as pd
import json
from google.cloud import storage
from datetime import datetime


client = storage.Client() #initializing gcs client
bucket_name = 'storypointsai_client1' #bucket name to hold info
today = datetime.now().strftime('%Y-%m-%d') #getting today's date so I use it for partitioning
exchange_rate_file_path = f"data/raw/api_currency/{today}/exchange_rates.json" #exchange rate file path stored on gcs already

chunksize = 50000
clickstream_input   =   'clickstream.csv'
transactions_input  =   'transactions.csv'
clickstream_output  =   f"clickstream/ingest_date={today}/clickstream_output.csv"
transactions_output =   f"transactions/ingest_date={today}/transactions_output.csv"

#mother subroutine
def process_file(file_input_path, output_path, file_type, rates):
    all_chunks = []
    for chunk in pd.read_csv(file_input_path, chunksize=chunksize):
        if file_type == "clickstream":
            transformed = transform_clickstream(chunk)
            all_chunks.append(transformed)
        elif file_type == "transactions":
            transformed = transform_transactions(chunk, rates)
            all_chunks.append(transformed)
    full_dataframe = pd.concat(all_chunks, ignore_index=True)
    
    #uploading to google cloud storage
    upload_to_gcs(full_dataframe, bucket_name, output_path)


#transform clickstream data
def transform_clickstream(chunk):
    chunk = standardize_columns(chunk)
    chunk = convert_to_utc(chunk)
    chunk = deduplicate(chunk)
    return chunk


#Transform transactions data + add USD conversion
def transform_transactions(chunk, rates):
    chunk = standardize_columns(chunk)
    chunk = convert_to_utc(chunk)
    chunk = deduplicate(chunk)
    
    # amount_in_usd column logic here
    chunk["amount_in_usd"] = chunk.apply(
        lambda row: row["amount"] / rates.get(row["currency"], 1),
        axis=1
    )

    return chunk


#standardize column names
def standardize_columns(dataframe):
    dataframe.columns = dataframe.columns.str.lower().str.replace(' ', '_')
    return dataframe

#convert timestamps to utc
def convert_to_utc(dataframe):
    for col in dataframe.select_dtypes(include=['datetime64']).columns:
        dataframe[col] = dataframe[col].dt.tz_convert('UTC')
    return dataframe

#remove duplicates
def deduplicate(dataframe):
    return dataframe.drop_duplicates()

#uploading dataframe to GCS subroutine
def upload_to_gcs(full_dataframe, bucket_name, output_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Convert full_dataframe to CSV
    csv_data = full_dataframe.to_csv(index=False)

    # Upload to GCS
    blob = bucket.blob(output_path)
    blob.upload_from_string(
        data=csv_data,
        content_type='text/csv' 
    )
    
    print(f"Uploaded to gs://{bucket_name}/{output_path}")


#downloading exchange rate from gcs as json
def download_from_gcs(bucket_name, exchange_rate_file_path):
    client = storage.Client()           #initialize client
    bucket = client.bucket(bucket_name)     #getting bucket and blob
    blob = bucket.blob(exchange_rate_file_path)

    json_data = blob.download_as_text() #downloading json to text
    data = json.loads(json_data) #parsing to python dict
    rates = data["conversion_rates"]
    
    return rates


if __name__ == "__main__":
    filetype = int(input('Enter 1 for Clickstream and 2 for Transaction: '))
    if filetype == 1:
        rates = ""
        process_file(clickstream_input, clickstream_output, "clickstream", rates)
    elif filetype == 2:
        rates = download_from_gcs(bucket_name, exchange_rate_file_path)
        process_file(transactions_input, transactions_output, "transactions", rates)
    else:
        print('Wrong input, please try again')