from datetime import datetime
import pandas as pd

# --- 1. Import all the tools you have built ---
from epirules.engine import evaluate_rule_set
from fetch_weather import get_weather_data # Assuming your failover logic is in this function
from knowledge_querier import query_field_details
from literature_searcher import search_literature
from vision_classifier import classify_leaf

def run_agent(field_id: str, image_path: str):
    """
    Orchestrates the tools to produce a risk assessment for a given field and leaf image.
    """
    print(f"--- AGENT-RUNNING: Analyzing risk for {field_id} ---")
    
    # --- STEP 1: VISUAL ANALYSIS (Vision Tool) ---
    print("\n[1] Analyzing leaf image...")
    visual_finding = classify_leaf(image_path)
    print(f"-> Diagnosis: {visual_finding['diagnosis']} (Confidence: {visual_finding['confidence']:.2%})")
    
    # --- STEP 2: FIELD HISTORY (Knowledge Querier Tool) ---
    print("\n[2] Retrieving field history...")
    field_info = query_field_details(field_id)
    if not field_info:
        print(f"-> ERROR: Field '{field_id}' not found in knowledge base.")
        return
    
    days_since_spray = (datetime.now() - datetime.strptime(field_info['last_spray_date'], '%Y-%m-%d')).days
    print(f"-> Variety: {field_info['potato_variety']}, Last Sprayed: {days_since_spray} days ago")

    # --- STEP 3: WEATHER ANALYSIS (Weather + Rules Tools) ---
    print("\n[3] Fetching and analyzing recent weather data...")
    # NOTE: For a real application, you'd get lat/lon from field_info. We'll use the hardcoded ones.
    weather_df = get_weather_data(latitude=46.40, longitude=-63.79, start_date="2025-08-25", end_date="2025-08-31", vc_api_key="YOUR_VC_KEY_HERE")
    
    if weather_df is None:
        print("-> ERROR: Could not fetch weather data.")
        return

    # We need the rules config to run the rules checker
    rules_config = {'Hutton': {'min_temp_c': 10, 'rh_threshold': 90, 'min_hours_per_day': 6, 'consecutive_days': 2}}
    weather_risk = evaluate_rule_set(weather_df, rules_config, 'Hutton')
    print(f"-> Weather Risk (Hutton): Triggered = {weather_risk['result']['triggered']}")

    # --- STEP 4: LITERATURE SEARCH (RAG Tool) ---
    print("\n[4] Searching literature for context...")
    # Search for info on the diagnosed disease and the potato variety
    disease_info = search_literature(visual_finding['diagnosis'])
    variety_info = search_literature(field_info['potato_variety'])
    print(f"-> Found {len(disease_info)} sections on the disease and {len(variety_info)} on the variety.")

    # --- STEP 5: SYNTHESIS (The "Planner's Decision") ---
    print("\n[5] Synthesizing final recommendation...")
    recommendation = "No action needed at this time."
    urgency = "Low"

    # A simple rule-based synthesis (simulating an LLM's reasoning)
    if weather_risk['result']['triggered'] and visual_finding['diagnosis'] == 'late_blight':
        if days_since_spray > 7:
            recommendation = "IMMEDIATE ACTION RECOMMENDED: High weather risk and visible late blight symptoms detected. Last spray was over a week ago. Consult literature on effective fungicides."
            urgency = "High"
        else:
            recommendation = "MONITOR CLOSELY: High weather risk and symptoms are present, but a recent spray may provide protection. Assess spray effectiveness."
            urgency = "Medium"
    elif weather_risk['result']['triggered']:
        recommendation = "PRECAUTIONARY ALERT: Weather conditions are favorable for late blight. Scout fields, especially susceptible varieties."
        urgency = "Medium"

    print(f"\n--- AGENT-COMPLETE ---")
    print(f"  Urgency: {urgency}")
    print(f"  Recommendation: {recommendation}")
    # The final JSON record would include all the evidence collected in the steps above
    # print(f"  Evidence: visual={visual_finding}, field={field_info}, etc...")

# --- Main part of the script to demonstrate a run ---
if __name__ == "__main__":
    # Define the inputs for this specific run
    target_field = "FIELD_002"  # A field with a 'Kennebec' potato
    target_image = "test_leaf.jpg" # Your test image of a blighted leaf
    
    # Make sure you have your Visual Crossing API key in your fetch_weather.py file,
    # or pass it into the run_agent function.
    run_agent(field_id=target_field, image_path=target_image)