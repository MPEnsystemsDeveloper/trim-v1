import os
import pandas as pd # type: ignore
from pymongo import MongoClient # type: ignore
from dotenv import load_dotenv # type: ignore
import certifi # type: ignore

def aggregate_and_load_daily():
    """
    Reads time-series data from a CSV, aggregates it by day, calculates the
    sum of currents and total daily energy consumption (kWh), and loads the
    summary into a MongoDB collection.
    """
    # 1. Load Environment Variables
    print("Loading environment variables...")
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    device_name = os.getenv("DEVICE_NAME")

    if not mongo_uri or not device_name:
        print("Error: MONGO_URI and DEVICE_NAME must be set in the .env file.")
        return

    # --- Configuration ---
    csv_file_path = 'sensor_data.csv'
    db_name = "energy_data"
    # Use a new collection for this aggregated data
    collection_name = "daily_power_consumption"

    client = None
    try:
        # 2. Establish Connection to MongoDB Atlas
        print("Connecting to MongoDB Atlas...")
        ca = certifi.where()
        client = MongoClient(mongo_uri, tlsCAFile=ca)
        client.admin.command('ping')
        print("MongoDB connection successful.")

        db = client[db_name]
        collection = db[collection_name]

        # 3. Read and Pre-process the CSV file
        print(f"Reading data from {csv_file_path}...")
        df = pd.read_csv(csv_file_path)

        # Robustness: Clean column names (remove spaces, convert to lowercase)
        df.columns = df.columns.str.strip().str.lower()
        
        # Vital Step: Convert 'timestamp' column to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Handle any rows with missing data
        df.dropna(inplace=True)

        if df.empty:
            print("No data to process after cleaning. Exiting.")
            return

        # 4. Aggregate Data by Day
        print("Aggregating data by day...")
        
        # Set the timestamp as the index to use resampling tools
        df.set_index('timestamp', inplace=True)
        
        # Use resample('D') to group data by Day. Then apply sum() to aggregate.
        # This is the most efficient way to group by time in pandas.
        daily_summary_df = df.resample('D').sum()

        # 5. Perform Calculations on the Aggregated Data
        print("Calculating daily energy consumption (kWh)...")
        voltage = 230

        # Calculate the total sum of Amps for the day
        daily_summary_df['total_sum_of_amps'] = daily_summary_df['ct_r (a)'] + daily_summary_df['ct_y (a)'] + daily_summary_df['ct_b (a)']

        # --- Energy Calculation (kWh) ---
        # Formula: Energy (kWh) = Power (kW) * Time (Hours)
        # Power (kW) = (Total Amps * Volts) / 1000
        # Time (Hours) = For each reading (assumed to be per minute), it's 1/60th of an hour.
        # So, we sum up all the power-minutes and divide by 60 to get kWh.
        daily_summary_df['total_kWh'] = (daily_summary_df['total_sum_of_amps'] * voltage / 1000) / 60
        
        # Add the device name
        daily_summary_df['device_name'] = device_name
        
        # Reset index to turn the date back into a column
        daily_summary_df.reset_index(inplace=True)
        # Rename timestamp column to 'date' for clarity
        daily_summary_df.rename(columns={'timestamp': 'date'}, inplace=True)

        # 6. Prepare Data for MongoDB
        # Select and rename columns to match the desired output format
        output_df = daily_summary_df[[
            'date', 'ct_r (a)', 'ct_y (a)', 'ct_b (a)', 'total_kWh', 'device_name'
        ]].rename(columns={
            'ct_r (a)': 'sum_CT_R_A',
            'ct_y (a)': 'sum_CT_Y_A',
            'ct_b (a)': 'sum_CT_B_A'
        })
        
        # Convert date to string to avoid timezone issues, or keep as datetime
        # MongoDB handles datetime objects well, so we'll keep them.

        data_to_insert = output_df.to_dict('records')

        if not data_to_insert:
            print("No daily summary data to insert.")
            return

        # 7. Insert Data into MongoDB
        # For simplicity, we clear the collection before inserting new summaries.
        # In a real-world scenario, you might use `update_one` with `upsert=True`.
        print(f"Clearing previous data from '{collection_name}'...")
        collection.delete_many({})

        print(f"Inserting {len(data_to_insert)} daily summary records...")
        result = collection.insert_many(data_to_insert)
        print(f"Successfully inserted {len(result.inserted_ids)} records.")

    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
    except KeyError as e:
        print(f"A column was not found. Please check your CSV headers. Missing column: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 8. Ensure the client connection is closed
        if client:
            client.close()
            print("MongoDB connection closed.")


if __name__ == "__main__":
    aggregate_and_load_daily()




# import os
# import pandas as pd # type: ignore
# from pymongo import MongoClient # type: ignore
# from dotenv import load_dotenv # type: ignore
# import certifi # type: ignore
# from pathlib import Path # <-- Import the Path object for handling file paths

# def process_all_csvs_from_downloads():
#     """
#     Scans the user's Downloads folder for CSV files, combines them, aggregates
#     the data by day, calculates energy consumption (kWh), and loads the
#     summary into a MongoDB collection. Ideal for a one-time backfill of historical data.
#     """
#     # 1. Load Environment Variables
#     print("Loading environment variables...")
#     load_dotenv()
#     mongo_uri = os.getenv("MONGO_URI")
#     device_name = os.getenv("DEVICE_NAME")

#     if not mongo_uri or not device_name:
#         print("Error: MONGO_URI and DEVICE_NAME must be set in the .env file.")
#         return

#     # --- Configuration ---
#     # Get the path to the user's Downloads folder automatically
#     downloads_path = Path.home() / "Downloads"
#     db_name = "energy_data"
#     collection_name = "daily_power_consumption"
    
#     print(f"Scanning for CSV files in: {downloads_path}")

#     # --- NEW: Part 1 - Find and Combine all CSV files ---
#     all_dataframes = []
    
#     # Use glob to find all files ending with .csv
#     csv_files = list(downloads_path.glob('*.csv'))

#     if not csv_files:
#         print("No CSV files found in the Downloads folder. Exiting.")
#         return

#     print(f"Found {len(csv_files)} CSV files to process.")

#     for file_path in csv_files:
#         try:
#             print(f"--> Reading data from {file_path.name}...")
#             # Read the individual CSV file
#             df_single = pd.read_csv(file_path)

#             # --- Pre-process each file individually ---
#             # Robustness: Clean column names
#             df_single.columns = df_single.columns.str.strip().str.lower()
            
#             # Vital Step: Convert 'timestamp' column to datetime objects
#             df_single['timestamp'] = pd.to_datetime(df_single['timestamp'])
            
#             # Add the processed DataFrame to our list
#             all_dataframes.append(df_single)
#         except FileNotFoundError:
#             print(f"Warning: Could not find file {file_path}. Skipping.")
#         except KeyError as e:
#             print(f"Warning: File {file_path.name} is missing a required column: {e}. Skipping this file.")
#         except Exception as e:
#             print(f"Warning: An error occurred while processing {file_path.name}: {e}. Skipping this file.")

#     if not all_dataframes:
#         print("No valid data could be read from any CSV file. Exiting.")
#         return

#     # Combine all the individual dataframes into one large master DataFrame
#     print("\nCombining all CSV data into a single dataset...")
#     df = pd.concat(all_dataframes, ignore_index=True)
    
#     # Sort by timestamp to ensure chronological order after combining
#     df.sort_values('timestamp', inplace=True)
    
#     # Handle any rows with missing data from the combined frame
#     df.dropna(inplace=True)

#     if df.empty:
#         print("No data to process after combining and cleaning all files. Exiting.")
#         return
        
#     print(f"Total records to process: {len(df)}")
#     # --- END NEW: Part 1 ---

#     client = None
#     try:
#         # 2. Establish Connection to MongoDB Atlas
#         print("\nConnecting to MongoDB Atlas...")
#         ca = certifi.where()
#         client = MongoClient(mongo_uri, tlsCAFile=ca)
#         client.admin.command('ping')
#         print("MongoDB connection successful.")

#         db = client[db_name]
#         collection = db[collection_name]

#         # 3. Aggregate Data by Day (using the combined DataFrame 'df')
#         print("Aggregating all data by day...")
        
#         df.set_index('timestamp', inplace=True)
#         daily_summary_df = df.resample('D').sum()

#         # 4. Perform Calculations on the Aggregated Data
#         print("Calculating daily energy consumption (kWh)...")
#         voltage = 230
#         daily_summary_df['total_sum_of_amps'] = daily_summary_df['ct_r (a)'] + daily_summary_df['ct_y (a)'] + daily_summary_df['ct_b (a)']
#         daily_summary_df['total_kWh'] = (daily_summary_df['total_sum_of_amps'] * voltage / 1000) / 60
#         daily_summary_df['device_name'] = device_name
        
#         daily_summary_df.reset_index(inplace=True)
#         daily_summary_df.rename(columns={'timestamp': 'date'}, inplace=True)

#         # 5. Prepare Data for MongoDB
#         output_df = daily_summary_df[[
#             'date', 'ct_r (a)', 'ct_y (a)', 'ct_b (a)', 'total_kWh', 'device_name'
#         ]].rename(columns={
#             'ct_r (a)': 'sum_CT_R_A',
#             'ct_y (a)': 'sum_CT_Y_A',
#             'ct_b (a)': 'sum_CT_B_A'
#         })
        
#         data_to_insert = output_df.to_dict('records')

#         if not data_to_insert:
#             print("No daily summary data to insert.")
#             return

#         # 6. Insert Data into MongoDB
#         # This will replace all existing data in the collection.
#         # This is appropriate for a one-time full backfill.
#         print(f"\nWARNING: Clearing ALL previous data from '{collection_name}'...")
#         collection.delete_many({})

#         print(f"Inserting {len(data_to_insert)} daily summary records into MongoDB...")
#         result = collection.insert_many(data_to_insert)
#         print(f"Successfully inserted {len(result.inserted_ids)} records.")

#     except Exception as e:
#         print(f"An error occurred during MongoDB operations or data processing: {e}")
#     finally:
#         # 7. Ensure the client connection is closed
#         if client:
#             client.close()
#             print("MongoDB connection closed.")


# if __name__ == "__main__":
#     process_all_csvs_from_downloads()