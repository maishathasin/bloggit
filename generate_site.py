


import os
import requests
import markdown2
from jinja2 import Environment, FileSystemLoader
from github import Github, Auth
from dotenv import load_dotenv
import os 

load_dotenv()

# Authentication and GitHub Initialization
token = os.getenv('token')
auth = Auth.Token(token)
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

    def parse_contents(contents, parent_path=""):
        for content in contents:
            # Determine the relative path of the content
            if parent_path:
                relative_path = f"{parent_path}/{content.name}"
            else:
                relative_path = content.name

            if content.type == "dir":
                # Add the directory as a key with an empty list, and parse its contents
                directory_structure[relative_path] = []
                try:
                    subdir_contents = repo.get_contents(content.path)
                    parse_contents(subdir_contents, relative_path)
                except Exception as e:
                    print(f"Error accessing directory {relative_path}: {e}")
            else:
                # Add the file to the parent directory's list
                if parent_path:
                    directory_structure[parent_path].append(content.name)
                else:
                    # Handle root-level files
                    directory_structure[content.name] = []

    try:
        parse_contents(contents)
    except Exception as e:
        print(f"Error building directory structure for {repo_name}: {e}")

    return directory_structure




def format_directory_structure(structure):
    def format_tree(node, prefix="", is_last=True):
        tree = ""
        if node:  
            tree += f"{prefix}{'└── ' if is_last else '├── '}{node.split('/')[-1]}\n"

        if node in structure:
            children = structure[node]
            for i, child in enumerate(children):
                extension = "    " if is_last else "│   "
                tree += format_tree(child, prefix + extension, i == len(children) - 1)
        return tree

    roots = [node for node in structure if not any(node in items for items in structure.values())]
    tree = ""
    for i, root in enumerate(roots):
        tree += format_tree(root, is_last=(i == len(roots) - 1))
    return tree.strip()


def create_blog_content(g, repo_name):
    try:

        # Get directory structure
        directory_structure = get_repo_directory_structure(g, repo_name)
        print('helloo')
        print(directory_structure)
        formatted_structure = format_directory_structure(directory_structure)
        print(formatted_structure)


        repo = g.get_user().get_repo(repo_name)
        print(repo)
        # for if there is not 
        try:
            contents = repo.get_contents("README.md")
            readme_html = markdown2.markdown(contents.decoded_content.decode('utf-8'))
        except Exception as e:
            contents = ' '
            readme_html = "<p>This is where you add your content</p>"  

        print(contents)
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
