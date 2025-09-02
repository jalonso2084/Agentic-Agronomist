import os
from pathlib import Path

# NOTE: The folder is named "Literature" with a capital L in your directory
LITERATURE_PATH = Path("Literature")

def search_literature(query: str) -> list:
    """
    Searches all .txt files in the literature folder for a given query.
    """
    if not LITERATURE_PATH.exists():
        print(f"Error: Literature directory not found at '{LITERATURE_PATH}'")
        return []
    
    found_results = []
    search_query = query.lower()

    for file_path in LITERATURE_PATH.glob("*.txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            chunks = content.split('\n\n')
            
            for chunk in chunks:
                if search_query in chunk.lower():
                    result = {
                        "citation": file_path.name,
                        "content": chunk.strip()
                    }
                    found_results.append(result)
                    
    return found_results

# --- Main part of the script ---
if __name__ == "__main__":
    print("--- Searching for information on 'organic use' for copper ---")
    results1 = search_literature("organic use")
    if results1:
        print(f"Found {len(results1)} relevant sections:")
        for res in results1:
            print(f"  - Citation: {res['citation']}")
            print(f"    Content: \"{res['content']}\"")
    else:
        print("No information found.")
        
    print("\n" + "-"*30 + "\n")

    print("--- Searching for information on 'tuber blight' ---")
    results2 = search_literature("tuber blight")
    if results2:
        print(f"Found {len(results2)} relevant sections:")
        for res in results2:
            print(f"  - Citation: {res['citation']}")
            print(f"    Content: \"{res['content']}\"")
    else:
        print("No information found.")