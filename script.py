from pyral import Rally
import os
import sys

def create_rally_pull_request(rally_client, ref, pr):
    try:
        # Define the data for the pull request
        data = {
            "ExternalID": pr["number"],
            "ExternalFormattedId": pr["number"],
            "Artifact": ref,
            "Name": pr["title"],  # This will be the commit message
            "Url": pr["html_url"],  # This is your workflow URL
        }

        # Create the pull request connection in Rally
        result = rally_client.create('PullRequest', data)
        print(f"Created Pull Request: {result}")

    except Exception as e:  # Catch all exceptions
        print(f"Error: {e}")
        raise  # Re-raise the exception if needed

# Example usage
if __name__ == "__main__":
    rally_server = 'rally1.rallydev.com'
    rally_api_key = os.getenv('RALLY_API_KEY')  # Retrieve API key from environment variable
    rally_workspace = 'Workspace 1'  # Replace with your workspace ID
    rally_project = 'Naveen'  # Replace with your project name
    rally_client = Rally(server=rally_server, apikey=rally_api_key, workspace=rally_workspace, project=rally_project)

    # Get pull request data from command line arguments or environment variables
    pr_number = sys.argv[1]  # Pull request number passed as an argument
    pr_title = sys.argv[2]   # Pull request title (commit message) passed as an argument
    pr_html_url = sys.argv[3]  # Pull request URL passed as an argument
    pr_body = sys.argv[4]  # Pull request body passed as an argument

    # Extract user story ID from pull request body
    user_story_id = None
    for line in pr_body.splitlines():
        if line.startswith('userstoryID'):
            user_story_id = line.split('=')[1].strip()
            break

    if not user_story_id:
        print("User story ID not found in pull request body.")
        sys.exit(1)

    # Fetch the user story from Rally
    response = rally_client.get('UserStory', query=f'FormattedID = "{user_story_id}"')
    story = response.next()
    ref = story.ref

    # Create the pull request in Rally
    build = {
        "number": pr_number,
        "title": pr_title,
        "html_url": pr_html_url
    }
    create_rally_pull_request(rally_client, ref, build)
