from flask import Flask, request, jsonify
import os
import git
import json
from datetime import datetime
from emission_tracker import measure_emissions_g_co2_eq
from multiprocessing import Process
import requests  # For creating pull requests via GitHub API
from llm_code_optimizer import optimize_code   # Import the optimization function

app = Flask(__name__)

# Paths and environment variables
CURRENT_REPO_DIR = "./"
LOG_FILE_PATH = "./emissions_log.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "abhisheknagargoje"  # Update with your GitHub username or organization
REPO_NAME = "emission_monitor"  # Update with your repository name

def log_emissions_to_file(repo_name, emissions_data):
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as log_file:
            try:
                log_entries = json.load(log_file)
            except json.JSONDecodeError:
                log_entries = []
    else:
        log_entries = []

    timestamp = datetime.now().isoformat()
    log_entry = {
        "repo_name": repo_name,
        "timestamp": timestamp,
        "emissions": emissions_data
    }
    log_entries.append(log_entry)

    with open(LOG_FILE_PATH, "w") as log_file:
        json.dump(log_entries, log_file, indent=4)

def optimize_code_and_create_pr(repo_folder, modified_files, added_files):
    repo = git.Repo(repo_folder)
    original_branch = repo.active_branch
    new_branch_name = f"optimize_{original_branch.commit.hexsha[:7]}"

    # Create a new branch for the optimized code
    repo.git.checkout('-b', new_branch_name)
    
    for file in modified_files + added_files:
        if file.endswith(".pyc") or file.startswith("tests") or "test_" in os.path.basename(file):
            continue  # Skip non-relevant files

        file_path = os.path.join(repo_folder, file)
        with open(file_path, "r") as f:
            original_code = f.read()
        
        # Generate optimized code using LLM
        try:
            optimized_code = optimize_code(original_code)
        except ValueError as e:
            print(f"Failed to optimize code for {file}: {str(e)}")
            continue

        # Write the optimized code back to the file
        with open(file_path, "w") as f:
            f.write(optimized_code)
    
    # Commit the optimized changes
    repo.git.add(update=True)
    repo.git.commit('-m', f"Optimized code for modified files in commit {original_branch.commit.hexsha[:7]}")
    
    # Push the new branch
    repo.git.push('--set-upstream', 'origin', new_branch_name)

    # Create a pull request using the GitHub API
    create_pull_request(new_branch_name, f"Optimize Code: {new_branch_name}")

    # Switch back to the original branch
    repo.git.checkout(original_branch)

def create_pull_request(branch_name, title):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "head": branch_name,
        "base": "main",  # Use the appropriate base branch name
        "body": f"Automated optimization for modified files in {branch_name}"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("Pull request created successfully.")
    else:
        print("Failed to create pull request:", response.json())

def process_commit_emissions(repo_folder, modified_files, added_files, repo_name):
    emissions_data = {}
    for file in modified_files + added_files:
        if not file.endswith(".pyc") and file.startswith("tests") and "test_" in os.path.basename(file):
            test_file_path = os.path.join(repo_folder, file)
            try:
                print("Processing emissions for:", test_file_path)
                emissions = measure_emissions_g_co2_eq(test_file_path)
                emissions_data[file] = round(emissions, 6)
            except Exception as e:
                emissions_data[file] = f"Error calculating emissions for {file}: {str(e)}"
    
    log_emissions_to_file(repo_name, emissions_data)
    # Trigger code optimization after emissions calculation
    optimize_code_and_create_pr(repo_folder, modified_files, added_files)

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    payload = request.json

    if request.headers.get('X-GitHub-Event') == 'push':
        try:
            latest_commit = payload['commits'][0]
            modified_files = latest_commit.get('modified', [])
            added_files = latest_commit.get('added', [])
            
            repo_name = payload['repository']['name']
            
            print(f"Pulling latest changes for {repo_name}...")
            repo = git.Repo(CURRENT_REPO_DIR)
            origin = repo.remotes.origin
            origin.pull()
            print(f"Repository {repo_name} updated successfully!")

            process = Process(
                target=process_commit_emissions, 
                args=(CURRENT_REPO_DIR, modified_files, added_files, repo_name)
            )
            process.start()

            return "Webhook received. Processing emissions and optimizations in the background.", 200

        except KeyError as e:
            return f"Missing expected key: {str(e)}", 400
    
    return "Not a push event", 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
