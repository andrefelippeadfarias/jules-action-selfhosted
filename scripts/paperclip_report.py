#!/usr/bin/env python3
"""Report the generated PR to Paperclip.
The script expects the following environment variables set by the workflow:
  PR_URL            – URL of the created PR (optional, may be empty)
  GITHUB_REPOSITORY – owner/repo name (e.g. vamm-dev/frime-app)
  PAPERCLIP_API_KEY – secret token for Paperclip API
  PAPERCLIP_URL     – base URL of Paperclip (default http://127.0.0.1:3100)
"""
import os, sys, json, requests

PR_URL = os.getenv('PR_URL')
REPO = os.getenv('GITHUB_REPOSITORY')
API_KEY = os.getenv('PAPERCLIP_API_KEY')
BASE_URL = os.getenv('PAPERCLIP_URL', 'http://127.0.0.1:3100')

if not PR_URL:
    print('No PR URL – nothing to report.')
    sys.exit(0)

# Try to fetch minimal PR info from GitHub (requires GITHUB_TOKEN, already provided by actions)
# We use the GitHub CLI (gh) that is pre‑installed on the runner.
import subprocess
try:
    pr_json = subprocess.check_output([
        'gh', 'pr', 'view', PR_URL, '--json', 'title,body,number', '--repo', REPO
    ], text=True)
    pr = json.loads(pr_json)
except Exception as e:
    print('Failed to fetch PR details via gh:', e)
    pr = {'title': 'Jules PR', 'body': f'Generated PR: {PR_URL}', 'number': None}

# Build payload for Paperclip – create a new issue (or update if you have a rule)
payload = {
    'title': f"[Jules] {pr.get('title', 'Generated PR')}",
    'description': pr.get('body', '') + f"\n\nGitHub PR: {PR_URL}",
    'status': 'in_progress',
    'projectKey': 'JULES',   # you can have a dedicated project in Paperclip
    'tags': ['jules', 'automation']
}

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

resp = requests.post(f"{BASE_URL}/api/issues", headers=headers, json=payload)
if resp.status_code not in (200, 201):
    print('Paperclip request failed:', resp.status_code, resp.text)
    sys.exit(1)
else:
    print('Paperclip issue created/updated successfully.')
    print('Response:', resp.json())
