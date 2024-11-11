from flask import Flask, request, jsonify
import os
import git
import threading
import json
from datetime import datetime
from emission_tracker import measure_emissions_g_co2_eq

app = Flask(__name__)

# Paths for the current repository and emissions log
CURRENT_REPO_DIR = "./"  # Root directory of the current repo
LOG_FILE_PATH = "./emissions_log.json"

def log_emissions_to_file(repo_name, emissions_data):
    # Check if the log file exists
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as log_file:
            try:
                log_entries = json.load(log_file)  # Load existing JSON data into a list
            except json.JSONDecodeError:
                log_entries = []  # Start a new list if the JSON is invalid or empty
    else:
        log_entries = []  # Start with an empty list if the log file doesn't exist

    # Prepare the new log entry
    timestamp = datetime.now().isoformat()
    log_entry = {
        "repo_name": repo_name,
        "timestamp": timestamp,
        "emissions": emissions_data
    }

    # Append the new log entry
    log_entries.append(log_entry)

    # Write the updated list back to the file as a valid JSON array
    with open(LOG_FILE_PATH, "w") as log_file:
        json.dump(log_entries, log_file, indent=4)


def process_commit_emissions(repo_folder, modified_files, added_files, repo_name):
    emissions_data = {}
    for file in modified_files + added_files:
        # Skip .pyc files and process only test files
        if not file.endswith(".pyc") and file.startswith("tests") and "test_" in os.path.basename(file):
            test_file_path = os.path.join(repo_folder, file)
            try:
                print("Processing emissions for:", test_file_path)
                emissions = measure_emissions_g_co2_eq(test_file_path)
                emissions_data[file] = round(emissions, 6)  # Rounded for readability
            except Exception as e:
                emissions_data[file] = f"Error calculating emissions for {file}: {str(e)}"
    
    log_emissions_to_file(repo_name, emissions_data)


@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    payload = request.json

    # Check if the event is a push event
    if request.headers.get('X-GitHub-Event') == 'push':
        try:
            # Get the latest commit details
            latest_commit = payload['commits'][0]
            modified_files = latest_commit.get('modified', [])
            added_files = latest_commit.get('added', [])
            
            repo_name = payload['repository']['name']
            
            # Pull the latest changes to the current repo
            print(f"Pulling latest changes for {repo_name}...")
            repo = git.Repo(CURRENT_REPO_DIR)
            origin = repo.remotes.origin
            origin.pull()
            print(f"Repository {repo_name} updated successfully!")

            # Start the emissions tracking in a separate thread
            thread = threading.Thread(
                target=process_commit_emissions, 
                args=(CURRENT_REPO_DIR, modified_files, added_files, repo_name)
            )
            thread.start()

            # Respond immediately to avoid GitHub timeout
            return "Webhook received. Processing emissions in the background.", 200

        except KeyError as e:
            return f"Missing expected key: {str(e)}", 400
    
    return "Not a push event", 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
