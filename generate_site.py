


import os
import requests
import markdown2
from jinja2 import Environment, FileSystemLoader
from github import Github, Auth

# Authentication and GitHub Initialization
auth = Auth.Token("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")
g = Github(auth=auth)

# Directory Definitions
TEMPLATE_DIR = 'templates'
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_user_repositories(g):
    user = g.get_user()
    return user.get_repos()

def get_repo_directory_structure(g, repo_name):
    repo = g.get_user().get_repo(repo_name)
    contents = repo.get_contents("")
    directory_structure = {}

    def parse_contents(contents, path=""):
        for content in contents:
            if content.type == "dir":
                print("come here")
                new_path = f"{path}/{content.name}" if path else content.name
                directory_structure[new_path] = []
                parse_contents(repo.get_contents(content.path), new_path)
            else:
                file_path = f"{path}/{content.name}" if path else content.name
                directory_structure[path].append(file_path)

    parse_contents(contents)
    return directory_structure


def format_directory_structure(structure):
    def format_tree(node, prefix=""):
        tree = ""
        print(structure.get(node, []))
        for i, path in enumerate(structure.get(node, [])):
            print(tree)
            is_last = i == len(structure[node]) - 1
            tree += f"{prefix}{'└── ' if is_last else '├── '}{path.split('/')[-1]}\n"
            print(tree)
            if path in structure:
                extension = '    ' if is_last else '│   '
                tree += format_tree(path, prefix + extension)
        return tree
    

    return format_tree("")



def create_blog_content(g, repo_name):
    try:

        # Get directory structure
        directory_structure = get_repo_directory_structure(g, repo_name)
        print(directory_structure)
        formatted_structure = format_directory_structure(directory_structure)
        print(formatted_structure)


        repo = g.get_user().get_repo(repo_name)
        contents = repo.get_contents("README.md")
        readme_html = markdown2.markdown(contents.decoded_content.decode('utf-8'))
        full_content = f"<pre>{formatted_structure}</pre>{readme_html}"
        return full_content
    except Exception as e:
        print(f"Error processing {repo_name}: {e}")
        return None

def generate_blog_html(g, selected_repos):
    repo_contents = {}
    for repo in selected_repos:
        content = create_blog_content(g, repo.name)
        if content:
            repo_contents[repo.name] = content

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('blog_template.html')
    output_from_parsed_template = template.render(repos=repo_contents)

    with open(os.path.join(OUTPUT_DIR, 'test.html'), 'w') as file:
        file.write(output_from_parsed_template)

repos = get_user_repositories(g)
print("Select repositories to create blogs from (comma-separated):")
for i, repo in enumerate(repos):
    print(f"{i}: {repo.name}")

selected_indexes = input()
selected_repos = [repos[int(i)] for i in selected_indexes.split(',')]
generate_blog_html(g, selected_repos)
