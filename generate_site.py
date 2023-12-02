import os
import requests
import sys; print(sys.path)
import markdown2
from jinja2 import Environment, FileSystemLoader
from pprint import pprint
from github import Github,Auth
# Authentication is defined via github.Auth
import marko




# Public Web Github


# using an access token
auth = Auth.Token("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")
# Github username
# pygithub object
g = Github()
g = Github(auth=auth)
# get that user by username
user = g.get_user()


def create_blog_from_repo(repo_name):
    repo = user.get_repo(repo_name)
    print(repo)
    contents = repo.get_contents("README.md")
    #print(contents.decoded_content)
    readme_md = requests.get(contents.download_url).text
    readme_html = markdown2.markdown(contents.decoded_content)
    print(readme_html)
  

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('blog_template.html')
    output_from_parsed_template = template.render(repo=repo, readme=readme_html)

    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f'{repo_name}.html'), 'w') as file:
        file.write(output_from_parsed_template)

# Example usage
# Replace 'repository_name' with the actual repository name
create_blog_from_repo('mori.css')  
