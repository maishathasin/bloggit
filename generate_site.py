
import os
import markdown2
from jinja2 import Environment, FileSystemLoader
from github import Github, Auth
from dotenv import load_dotenv
import os 
import argparse
import webbrowser




# Directory Definitions
TEMPLATE_DIR = 'templates'
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to get repositories for an authenticated user or a specified username
def get_user_repositories(g, username=None):
    if username:
        user = g.get_user(username)
    else:
        user = g.get_user()
    return user.get_repos()

def get_repo_directory_structure(g, repo_name,username=None):
    if username:
        repo = g.get_user(username).get_repo(repo_name)
    else:
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
        include_directory_tree = input(f"Do you want to include the directory tree for {repo_name}? (Y/N): ").strip().lower() == 'y'
        
        formatted_structure = ""
        if include_directory_tree:
            directory_structure = get_repo_directory_structure(g, repo_name)
            formatted_structure = format_directory_structure(directory_structure)

        
        repo = g.get_user().get_repo(repo_name)
        try:
            contents = repo.get_contents("README.md")
             # store each readme in the contents folder as the repo_name and then render from there, instead of 
             # repo name, we make the article name as markdown file name 
             # add flags for build that just builds the content folder, add flags for add
            readme_html = markdown2.markdown(contents.decoded_content.decode('utf-8'))


            
           # Conditionally add tags if they exist
            if tags:
                tags_html = '<ul>' + ''.join([f'<div class= "tag color-change">{tag}</div>' for tag in tags]) + '</ul>'
                tags_section = f"<h3>Tags:</h3>{tags_html}"
            else:
                tags_section = ''
            readme_html = f"<pre>{formatted_structure}</pre> <br> {readme_html} {tags_section}"
        except Exception as e:
            # for if there is not , add exeption for if there is no Readme 
            contents = ' '
            readme_html = "<p>This is where you add your content</p>"  

        full_content = f"{readme_html}"
        return full_content
    except Exception as e:
        print(f"Error processing {repo_name}: {e}")
        return None

import json


def generate_blog_html(g, repo_tags):
    repo_contents = {}
    tags_info = {}
    for repo_name, tags in repo_tags.items():
        content = create_blog_content(g, repo_name, tags)
        if content:
            repo_contents[repo_name] = content
            tags_info[repo_name] = tags
            # Save each repo's content to a separate HTML file
            with open(os.path.join(OUTPUT_DIR, 'content', f'{repo_name}.html'), 'w') as file:
                file.write(content)

  # Read existing tags from tags.json
    tags_file_path = os.path.join(OUTPUT_DIR, 'tags.json')
    if os.path.exists(tags_file_path):
        with open(tags_file_path, 'r') as file:
            existing_tags = json.load(file)
    else:
        existing_tags = {}

    # Update and save tags
    for repo_name, new_tags in repo_tags.items():
        existing_tags_for_repo = set(existing_tags.get(repo_name, []))
        updated_tags = list(existing_tags_for_repo.union(new_tags))
        existing_tags[repo_name] = updated_tags

    with open(tags_file_path, 'w') as file:
        json.dump(existing_tags, file, indent=4)



def build_blog_from_content():
    # Ensure the content folder exists
    content_dir = os.path.join(OUTPUT_DIR, 'content')
    if not os.path.exists(content_dir):
        print("Content directory does not exist. Please generate content first.")
        return

    # Read HTML files from the content folder
    repo_contents = {}
    for file_name in os.listdir(content_dir):
        if file_name.endswith('.html'):
            repo_name = file_name[:-5] 
            with open(os.path.join(content_dir, file_name), 'r') as file:
                repo_contents[repo_name] = file.read()

    # Load tags from JSON file
    try:
        with open(os.path.join(OUTPUT_DIR, 'tags.json'), 'r') as file:
            repo_tags = json.load(file)
    except FileNotFoundError:
        print("Tags file not found. Tags will be empty.")
        repo_tags = {repo: [] for repo in repo_contents}

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('blog_template.html')
    output_from_parsed_template = template.render(repos=repo_contents, repo_tags=repo_tags)

    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as file:
        file.write(output_from_parsed_template)

    print("Blog built successfully from content folder , named index.html")



def get_tags_for_repo(repo_name):
    tags_str = input(f"Enter tags for {repo_name} (comma-separated): ")
    return tags_str.split(',') if tags_str.strip() else None


def delete_blog(repo_name):
    content_file_path = os.path.join(OUTPUT_DIR, 'content', f'{repo_name}.html')
    tags_file_path = os.path.join(OUTPUT_DIR, 'tags.json')

    # Delete the blog HTML file
    if os.path.exists(content_file_path):
        os.remove(content_file_path)
        print(f"Deleted blog content for {repo_name}.")
    else:
        print(f"No content file found for {repo_name}.")

    # Update the tags
    if os.path.exists(tags_file_path):
        with open(tags_file_path, 'r') as file:
            tags = json.load(file)

        # Remove the tags for the deleted blog
        if repo_name in tags:
            del tags[repo_name]

            # Save the updated tags
            with open(tags_file_path, 'w') as file:
                json.dump(tags, file, indent=4)
            print(f"Updated tags after deleting {repo_name}.")
        else:
            print(f"No tags found for {repo_name}.")
    else:
        print(f"Tags file not found.")



    
# Generate the file tree for only input 
# and only generate the input for either public or give github token 
'''
repos = get_user_repositories(g)
print("Select repositories to create blogs from (comma-separated):")
repo_dict = {repo.name: repo for repo in repos}

for repo_name in repo_dict.keys():
    print(repo_name)

selected_repo_names = input().split(',')
selected_repos = [repo_dict[name.strip()] for name in selected_repo_names if name.strip() in repo_dict]


# Collect tags for each selected repository

# Generate the repo_tags dictionary
repo_tags = {}
for repo in selected_repos:
    tags = get_tags_for_repo(repo.name)
    if tags is not None:
        repo_tags[repo.name] = tags

# Generate blog HTML using the selected repositories and their respective tags
generate_blog_html(g, repo_tags)
build_blog_from_content()
delete_blog('mori.css')
'''

