import pandas as pd
from datetime import datetime

# Load the entire CSV into a pandas DataFrame when the script starts.
# This is efficient as we only read the file from disk once.
try:
    FARM_DATA = pd.read_csv("farm_data.csv")
except FileNotFoundError:
    print("Error: farm_data.csv not found. Please ensure it's in the correct directory.")
    FARM_DATA = None

def query_field_details(field_id: str) -> dict:
    """
    Finds and returns the details for a specific field_id from the CSV.
    
    Args:
        field_id: The unique identifier for the field (e.g., "FIELD_001").

    Returns:
        A dictionary containing the field's details, or None if not found.
    """
    if FARM_DATA is None:
        return None
        
    # Find the row that matches the field_id
    field_record = FARM_DATA[FARM_DATA['field_id'] == field_id]
    
    # If we found a record, convert it to a dictionary and return it
    if not field_record.empty:
        return field_record.to_dict('records')[0]
    
    # Otherwise, return None
    return None

# --- Main part of the script to demonstrate its use ---
if __name__ == "__main__":
    # Example 1: Query for a field that exists
    print("--- Querying for FIELD_002 ---")
    details_002 = query_field_details("FIELD_002")
    if details_002:
        # Calculate days since last spray for context
        last_spray = datetime.strptime(details_002['last_spray_date'], '%Y-%m-%d')
        days_since_spray = (datetime.now() - last_spray).days
        
        print(f"Found details: {details_002}")
        print(f"Potato Variety: {details_002['potato_variety']}")
        print(f"Days since last spray: {days_since_spray}")
    else:
        print("Field ID FIELD_002 not found.")

    print("\n" + "-"*30 + "\n")

    # Example 2: Query for a field that does NOT exist
    print("--- Querying for FIELD_999 ---")
    details_999 = query_field_details("FIELD_999")
    if details_999:
        print(f"Found details: {details_999}")
    else:
        print("Field ID FIELD_999 not found.")