import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi # <--- ADD THIS IMPORT

def transform_and_load():
    """
    Reads data from a CSV file, performs calculations to add new power-related columns,
    and loads the transformed data into a MongoDB Atlas collection.
    """
    # 1. Load Environment Variables from .env file
    print("Loading environment variables...")
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    device_name = os.getenv("DEVICE_NAME")

    if not mongo_uri or not device_name:
        print("Error: MONGO_URI and DEVICE_NAME must be set in the .env file.")
        return

    # --- MongoDB Connection Details ---
    db_name = "energy_data"
    collection_name = "read_processed_data"
    
    csv_file_path = 'sensor_data.csv'  # Path to the CSV file containing sensor data

    client = None
    try:
        # 2. Establish Connection to MongoDB Atlas
        print("Connecting to MongoDB Atlas...")
        
        # --- MODIFIED LINE ---
        # Explicitly pass the certificate authority file from the certifi package.
        # This helps in environments where system SSL certificates are not found.
        ca = certifi.where()
        client = MongoClient(mongo_uri, tlsCAFile=ca) # <--- MODIFIED THIS LINE
        
        client.admin.command('ping')
        print("MongoDB connection successful.")
        
        db = client[db_name]
        collection = db[collection_name]

        # ... (the rest of the script is exactly the same)
        print(f"Reading data from {csv_file_path}...")
        df = pd.read_csv(csv_file_path)
        df.dropna(inplace=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        print("Performing calculations...")
        voltage = 230
        df['R_power(kW)'] = (df['CT_R (A)'] * voltage) / 1000
        df['Y_power(kW)'] = (df['CT_Y (A)'] * voltage) / 1000
        df['B_power(kW)'] = (df['CT_B (A)'] * voltage) / 1000
        df['Total_power(kW)'] = df['R_power(kW)'] + df['Y_power(kW)'] + df['B_power(kW)']
        df['device_name'] = device_name
        
        data_to_insert = df.to_dict('records')
        
        if not data_to_insert:
            print("No data to insert.")
            return

        print(f"Inserting {len(data_to_insert)} records into collection '{collection_name}'...")
        result = collection.insert_many(data_to_insert)
        print(f"Successfully inserted {len(result.inserted_ids)} records.")

    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client:
            client.close()
            print("MongoDB connection closed.")


if __name__ == "__main__":
    transform_and_load()





# import os
# import pandas as pd
# from pymongo import MongoClient
# from dotenv import load_dotenv
# import certifi
# from pathlib import Path 

# def process_and_load_all_raw_data():
#     """
#     Scans the user's Downloads folder for all CSV files, combines them,
#     performs power calculations on each row, and loads the transformed
#     raw data into a MongoDB collection.
#     """
#     # 1. Load Environment Variables from .env file
#     print("Loading environment variables...")
#     load_dotenv()
#     mongo_uri = os.getenv("MONGO_URI")
#     device_name = os.getenv("DEVICE_NAME")

#     if not mongo_uri or not device_name:
#         print("Error: MONGO_URI and DEVICE_NAME must be set in the .env file.")
#         return

#     # --- Configuration ---
#     downloads_path = Path.home() / "Downloads"
#     db_name = "energy_data"
#     collection_name = "read_processed_data"

#     print(f"Scanning for CSV files in: {downloads_path}")

#     # --- Part 1: Find and Combine all CSV files ---
#     all_dataframes = []
#     csv_files = list(downloads_path.glob('*.csv'))

#     if not csv_files:
#         print("No CSV files found in the Downloads folder. Exiting.")
#         return

#     print(f"Found {len(csv_files)} CSV files to process.")

#     for file_path in csv_files:
#         try:
#             print(f"--> Reading data from {file_path.name}...")
#             df_single = pd.read_csv(file_path)
#             all_dataframes.append(df_single)
#         except Exception as e:
#             print(f"Warning: An error occurred while processing {file_path.name}: {e}. Skipping this file.")

#     if not all_dataframes:
#         print("No valid data could be read from any CSV file. Exiting.")
#         return

#     print("\nCombining all CSV data into a single dataset...")
#     df = pd.concat(all_dataframes, ignore_index=True)

#     # --- Part 2: Pre-process the COMBINED DataFrame ---
#     # It's more efficient to clean and process the combined data once.
#     print("Pre-processing combined data...")
    
#     # Robustness: Clean column names to be consistent (lowercase, no spaces)
#     # This is very important for preventing errors.
#     df.columns = df.columns.str.strip().str.lower()
    
#     # Handle any rows with missing data
#     df.dropna(inplace=True)
    
#     # Convert 'timestamp' column to datetime objects (uses the cleaned lowercase name)
#     df['timestamp'] = pd.to_datetime(df['timestamp'])

#     # Sort by timestamp to ensure chronological order
#     df.sort_values('timestamp', inplace=True)
    
#     if df.empty:
#         print("No data to process after combining and cleaning. Exiting.")
#         return
        
#     print(f"Total records to process: {len(df)}")

#     # --- Part 3: Perform Calculations ---
#     print("Performing power calculations on all records...")
#     voltage = 230
#     # Use the cleaned, lowercase column names for calculations
#     df['r_power(kw)'] = (df['ct_r (a)'] * voltage) / 1000
#     df['y_power(kw)'] = (df['ct_y (a)'] * voltage) / 1000
#     df['b_power(kw)'] = (df['ct_b (a)'] * voltage) / 1000
#     df['total_power(kw)'] = df['r_power(kw)'] + df['y_power(kw)'] + df['b_power(kw)']
#     df['device_name'] = device_name
    
#     client = None
#     try:
#         # 4. Establish Connection to MongoDB Atlas
#         print("\nConnecting to MongoDB Atlas...")
#         ca = certifi.where()
#         client = MongoClient(mongo_uri, tlsCAFile=ca)
#         client.admin.command('ping')
#         print("MongoDB connection successful.")
        
#         db = client[db_name]
#         collection = db[collection_name]
        
#         # 5. Prepare data for insertion
#         data_to_insert = df.to_dict('records')
        
#         if not data_to_insert:
#             print("No data to insert after processing.")
#             return
            
#         # 6. Insert Data into MongoDB
#         # WARNING: This will replace all existing data in the collection.
#         # This is suitable for a one-time backfill.
#         print(f"\nWARNING: Clearing ALL previous data from '{collection_name}'...")
#         collection.delete_many({})

#         print(f"Inserting {len(data_to_insert)} records into collection '{collection_name}'...")
#         result = collection.insert_many(data_to_insert)
#         print(f"Successfully inserted {len(result.inserted_ids)} records.")

#     except KeyError as e:
#         print(f"A required column was not found after cleaning. Please check your CSV headers. Missing column: {e}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         if client:
#             client.close()
#             print("MongoDB connection closed.")


# if __name__ == "__main__":
#     process_and_load_all_raw_data()