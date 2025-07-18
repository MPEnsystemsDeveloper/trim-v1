import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Optional
import certifi

# --- Initial Setup ---

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app instance
app = FastAPI(
    title="Energy Data API",
    description="API to fetch energy consumption data from MongoDB Atlas for graphing.",
    version="1.0.0"
)

# --- CORS (Cross-Origin Resource Sharing) ---
# This allows your frontend (like a React/Vue/Angular app) to communicate with this backend
origins = [
    "http://localhost",
    "http://localhost:3000", # Common for React apps
    "http://localhost:8080", # Common for Vue apps
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- MongoDB Connection ---

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables. Please create a .env file.")

try:
    # Use certifi to provide the CA bundle for TLS/SSL connections
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.energy_data
    processed_data_collection = db.read_processed_data
    daily_consumption_collection = db.daily_power_consumption
    
    # The ping command is a great way to verify a successful connection.
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# --- Helper Function to parse datetime strings ---

def parse_datetime_input(date_str: Optional[str], time_str: Optional[str]) -> Optional[datetime]:
    """Parses date and optional time strings into a datetime object."""
    if not date_str:
        return None
    time_str = time_str or "00:00" # Default to the beginning of the day if time is not provided
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time."
        )

# --- API Endpoints ---

# ADDED: Root endpoint to handle requests to "/"
@app.get("/", summary="Root Endpoint / Health Check")
async def read_root():
    """
    Provides a welcome message and a link to the API documentation.
    This resolves the '404 Not Found' error for the root path.
    """
    return {
        "status": "ok",
        "message": "Welcome to the Energy Data API!",
        "documentation_url": "/docs"
    }

@app.get("/devices", summary="Get a list of all unique device names")
async def get_device_names() -> List[str]:
    """
    Fetches a sorted list of unique device names from both data collections.
    """
    try:
        names1 = processed_data_collection.distinct("device_name")
        names2 = daily_consumption_collection.distinct("device_name")
        # Combine and get unique names, then sort them alphabetically
        unique_names = sorted(list(set(names1 + names2)))
        return unique_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/processed", summary="Fetch processed time-series data")
async def get_processed_data(
    device_name: str,
    start_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_date: Optional[str] = None,
    end_time: Optional[str] = None,
    interval: str = Query("raw", enum=["raw", "1hr", "4hr", "8hr", "12hr", "24hr"])
):
    """
    Fetches time-series data for a specific device.
    Can be raw data or aggregated into hourly intervals.
    If no date range is provided, it defaults to the last 24 hours of available data.
    """
    start_dt = parse_datetime_input(start_date, start_time)
    end_dt = parse_datetime_input(end_date, end_time)

    # Default to the last 24 hours if no date range is specified
    if not start_dt or not end_dt:
        latest_doc = processed_data_collection.find_one(
            {"device_name": device_name},
            sort=[("timestamp", -1)]
        )
        if not latest_doc:
            return [] # No data found for this device
        
        end_dt = latest_doc['timestamp']
        start_dt = end_dt - timedelta(days=1)

    match_query = {
        "device_name": device_name,
        "timestamp": {"$gte": start_dt, "$lte": end_dt}
    }

    if interval == "raw":
        cursor = processed_data_collection.find(match_query).sort("timestamp", 1)
    else:
        # Use an aggregation pipeline for interval-based averaging
        interval_hours = {"1hr": 1, "4hr": 4, "8hr": 8, "12hr": 12, "24hr": 24}[interval]
        pipeline = [
            {"$match": match_query},
            {
                "$group": {
                    "_id": {"$dateTrunc": {"date": "$timestamp", "unit": "hour", "binSize": interval_hours}},
                    "ct_r_a": {"$avg": "$ct_r (a)"},
                    "ct_y_a": {"$avg": "$ct_y (a)"},
                    "ct_b_a": {"$avg": "$ct_b (a)"},
                    "r_power_kw": {"$avg": "$r_power(kw)"},
                    "y_power_kw": {"$avg": "$y_power(kw)"},
                    "b_power_kw": {"$avg": "$b_power(kw)"},
                    "total_power_kw": {"$avg": "$total_power(kw)"}
                }
            },
            {
                "$project": {
                    "_id": 0, "timestamp": "$_id", "ct_r (a)": "$ct_r_a", "ct_y (a)": "$ct_y_a",
                    "ct_b (a)": "$ct_b_a", "r_power(kw)": "$r_power_kw", "y_power(kw)": "$y_power_kw",
                    "b_power(kw)": "$b_power_kw", "total_power(kw)": "$total_power_kw"
                }
            },
            {"$sort": {"timestamp": 1}}
        ]
        cursor = processed_data_collection.aggregate(pipeline)

    results = [doc for doc in cursor]
    # Convert MongoDB's ObjectId and datetime to JSON-serializable formats
    for doc in results:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
        if 'timestamp' in doc and isinstance(doc['timestamp'], datetime):
            doc['timestamp'] = doc['timestamp'].isoformat()

    return results


@app.get("/daily-consumption", summary="Fetch daily power consumption data")
async def get_daily_consumption(
    device_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Fetches daily total power consumption for a specific device.
    If no date range is provided, it defaults to the last 7 days of available data.
    """
    start_dt = parse_datetime_input(start_date, "00:00")
    end_dt = parse_datetime_input(end_date, "23:59")

    # Default to the last 7 days if no date range is specified
    if not start_dt or not end_dt:
        latest_doc = daily_consumption_collection.find_one(
            {"device_name": device_name},
            sort=[("date", -1)]
        )
        if not latest_doc:
            return [] # No data found for this device
        
        end_dt = latest_doc['date']
        start_dt = end_dt - timedelta(days=6)

    query = {
        "device_name": device_name,
        "date": {"$gte": start_dt, "$lte": end_dt}
    }
    
    cursor = daily_consumption_collection.find(query).sort("date", 1)

    results = [doc for doc in cursor]
    # Convert MongoDB's ObjectId and datetime to JSON-serializable formats
    for doc in results:
        doc['_id'] = str(doc['_id'])
        if 'date' in doc and isinstance(doc['date'], datetime):
            doc['date'] = doc['date'].isoformat()

    return results

# This block allows running the app directly with `python main.py`
# The `reload=True` is great for development, as it restarts the server on code changes.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)