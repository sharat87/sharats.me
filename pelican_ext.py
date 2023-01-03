import os
import re
import json

from pelican import signals
import requests


settings = None

# Docs: <https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories>.
GITHUB_STARS_QUERY = '''\
{
  sharat87: search(query: "user:sharat87", type: REPOSITORY, first: 100) {
    repositoryCount
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
      }
    }
  }
  antigen: search(query: "repo:zsh-users/antigen", type: REPOSITORY, first: 1) {
    repositoryCount
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
      }
    }
  }
  appsmith: search(query: "repo:appsmithorg/appsmith", type: REPOSITORY, first: 1) {
    repositoryCount
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
      }
    }
  }
}
'''


def render_github_stars(content):
    github_api_token = os.getenv("GITHUB_API_TOKEN")
    if not github_api_token:
        print("GitHub token not available.")
        return

    stars_by_project = {}

    try:
        with open("stars.json") as f:
            stars_by_project = json.load(f)
    except FileNotFoundError:
        response = requests.post(
            "https://api.github.com/graphql",
            json={
                "query": GITHUB_STARS_QUERY,
            },
            headers={
                "Authorization": "Bearer " + github_api_token,
            },
        )
        if not response.ok:
            print(response)
            return
        else:
            for search_result in response.json()["data"].values():
                for node in search_result["nodes"]:
                    stars_by_project[node["nameWithOwner"]] = node["stargazerCount"]
            print(stars_by_project)
            with open("stars.json", "w") as f:
                f.write(json.dumps(stars_by_project))

    def replacement(match):
        project = match.group("project")
        if "/" not in project:
            project = "sharat87/" + project
        stars: int = stars_by_project.get(project, 0)
        stars_str: str = f"{round(stars / 1000)}k" if stars > 999 else str(stars)
        return f'<a class=star-btn href="https://github.com/{project}" target=_blank rel=noopener title="Star project on GitHub">Star {stars_str}</a>'

    content._content = re.sub(r"{github-stars\s+(?P<project>.+?)}", replacement, content._content)


def on_init(sender):
    global settings
    settings = sender.settings


def on_content_init(content):
    if content.source_path.endswith(".md"):
        render_github_stars(content)


def register():
    signals.initialized.connect(on_init)
    signals.content_object_init.connect(on_content_init)
