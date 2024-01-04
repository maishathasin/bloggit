
import os
import requests
import markdown2
from jinja2 import Environment, FileSystemLoader
from github import Github, Auth
from dotenv import load_dotenv
import os 

load_dotenv()

# Authentication and GitHub Initialization
token = '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'
print(token)
auth = Auth.Token(token)
print(auth)
g = Github(auth=auth)
print(g)

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
            relative_path = f"{parent_path}/{content.name}" if parent_path else content.name

            if content.type == "dir":
                directory_structure[relative_path] = []
                try:
                    subdir_contents = repo.get_contents(content.path)
                    parse_contents(subdir_contents, relative_path)
                except Exception as e:
                    print(f"Error accessing directory {relative_path}: {e}")
            else:
                if parent_path:
                    if relative_path not in directory_structure[parent_path]:
                        directory_structure[parent_path].append(relative_path)
                else:
                    if relative_path not in directory_structure:
                        directory_structure[relative_path] = []

    parse_contents(contents)
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



def add_tags():

    pass


def create_blog_content(g, repo_name,tags):
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
             # store each readme in the contents folder as the repo_name and then render from there, instead of 
             # repo name, we make the article name as markdown file name 
             # add flags for build that just builds the content folder, add flags for add
            readme_html = markdown2.markdown(contents.decoded_content.decode('utf-8'))
                # Convert list of tags into HTML format
            tags_html = '<ul>' + ''.join([f'<div class= "tag color-change">{tag}</div>' for tag in tags]) + '</ul>'
            # Incorporate tags into the full content
            readme_html = f"<pre>{formatted_structure}</pre> <br> {readme_html}<h3>Tags:</h3>{tags_html}"
        except Exception as e:
            contents = ' '
            readme_html = "<p>This is where you add your content</p>"  

        print(contents)
        full_content = f"{readme_html}"
        return full_content
    except Exception as e:
        print(f"Error processing {repo_name}: {e}")
        return None

def generate_blog_html(g, repo_tags):
    repo_contents = {}
    for repo_name, tags in repo_tags.items():
        content = create_blog_content(g, repo_name, tags)
        if content:
            repo_contents[repo_name] = content

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('blog_template.html')
    output_from_parsed_template = template.render(repos=repo_contents, repo_tags=repo_tags)

    with open(os.path.join(OUTPUT_DIR, 'test.html'), 'w') as file:
        file.write(output_from_parsed_template)





def get_tags_for_repo(repo_name):
    tags_str = input(f"Enter tags for {repo_name} (comma-separated): ")
    return tags_str.split(',')

    
# Generate the file tree for only input 
# and only generate the input for either public or give github token 

repos = get_user_repositories(g)
print(repos)
print("Select repositories to create blogs from (comma-separated):")
for i, repo in enumerate(repos):
    print(f"{i}: {repo.name}")

selected_indexes = input()
selected_repos = [repos[int(i)] for i in selected_indexes.split(',')]

# Collect tags for each selected repository

repo_tags = {repo.name: get_tags_for_repo(repo.name) for repo in selected_repos}

# Generate blog HTML using the selected repositories and their respective tags
generate_blog_html(g, repo_tags)

