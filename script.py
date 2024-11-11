import requests
import os
import sys
import re
from pyral import Rally

api_key = '_ER5bgHLURomtDepEOkwiIqO4sJg50Ngt0Z3v8yC7Y0'

# Function to fetch the Object ID of a user story by its formatted ID
def get_object_id(formatted_id, api_key):
    rally_url = "https://rally1.rallydev.com/slm/webservice/v2.0/hierarchicalrequirement"
    params = {
        'query': f'(FormattedID = {formatted_id})',
        'fetch': 'ObjectID'
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(rally_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['QueryResult']['TotalResultCount'] > 0:
            return data['QueryResult']['Results'][0]['ObjectID']
        else:
            print(f"User story with FormattedID {formatted_id} not found.")
            return None
    else:
        print(f"Failed to fetch data. Status Code: {response.status_code}")
        return None

# Function to get the project name using the Object ID
def get_project_name(object_id, api_key):
    url = f"https://rally1.rallydev.com/slm/webservice/v2.0/hierarchicalrequirement/{object_id}"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        project_name = data['HierarchicalRequirement']['Project']['_refObjectName']
        return project_name
    else:
        print(f"Failed to retrieve data: {response.status_code} - {response.text}")
        return None

def create_rally_pull_request(rally_client, ref, pr):
    try:
        data = {
            "ExternalID": pr["number"],
            "ExternalFormattedId": pr["number"],
            "Artifact": ref,
            "Name": pr["title"],
            "Url": pr["html_url"],
            "Description": "This is workflow ID: pr["build_number"]",
        }
        result = rally_client.create('PullRequest', data)
        print(f"Created Pull Request: {result}")
    except Exception as e:
        print(f"Error: {e}")
        raise

# Function to extract all user story IDs from pull request body and remove duplicates
def extract_user_story_ids(pr_body):
    user_story_ids = re.findall(r'\bUS\d+\b', pr_body)
    if not user_story_ids:
        print("No user stories found in pull request body.")
        sys.exit(1)

    # Remove duplicates by converting the list to a set
    unique_user_story_ids = list(set(user_story_ids))
    
    return unique_user_story_ids

# Example usage
if __name__ == "__main__":
    rally_workspace = 'Workspace 1'
    rally_server = 'rally1.rallydev.com'

    pr_number = sys.argv[1]
    pr_title = sys.argv[2]
    pr_html_url = sys.argv[3]
    pr_body = sys.argv[4]
    build_number = sys.argv[5]

    # Extract all unique user story IDs from pull request body
    formatted_ids = extract_user_story_ids(pr_body)

    for formatted_id in formatted_ids:
        print(f"Processing User Story: {formatted_id}")

        # Get the Object ID and project name
        object_id = get_object_id(formatted_id, api_key)
        if object_id:
            project_name = get_project_name(object_id, api_key)
            if project_name:
                print(f"Object ID for {formatted_id}: {object_id}")
                print(f"Project Name: {project_name}")

                # Fetch the user story details from Rally
                rally_client = Rally(server=rally_server, apikey=api_key, workspace=rally_workspace, project=project_name)
                response = rally_client.get('UserStory', query=f'FormattedID = "{formatted_id}"')
                story = response.next()

                if not story:
                    print(f"No user story found with ID: {formatted_id}")
                    continue

                ref = story.ref

                # Create the pull request in Rally
                build = {
                    "number": pr_number,
                    "title": pr_title,
                    "html_url": pr_html_url
                    "build_number": build_number
                }
                create_rally_pull_request(rally_client, ref, build)
            else:
                print(f"Failed to get project name for {formatted_id}.")
        else:
            print(f"Failed to get Object ID for {formatted_id}.")
