
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
        formatted_structure = format_directory_structure(directory_structure)

        
        repo = g.get_user().get_repo(repo_name)
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


from rich.console import Console
from rich.table import Table


console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="GitBlog: A Static Site Generator CLI for GitHub repositories.",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--token", help="GitHub token for authentication")
    parser.add_argument("--build", action="store_true", help="Build the static site from content")
    parser.add_argument("--add", nargs='?', const=True, default=False, help="Add a repository to the blog")
    parser.add_argument("--addall", action="store_true", help="Add all repositories to the blog")
    parser.add_argument("--delete", help="Delete a specific blog\nUsage: --delete <blog_name>")
    parser.add_argument("--show", action="store_true", help="Show a list of all articles")
    parser.add_argument("--version", action="version", version="Static Site Generator 1.0")
    parser.add_argument("--open", action="store_true", help="Open the generated site in a web browser")


    args = parser.parse_args()

    if args.token:
        g = Github(auth=Auth.Token(args.token))
        console.print("Authenticated with GitHub", style="bold green")
    else:
        console.print("GitHub token is required.", style="bold red")
        exit(1)

    if args.build:
        build_blog_from_content()
    elif args.open:
        open_in_browser()
    elif args.add is not False:
        add_repo(g, args.add)
    elif args.addall:
        add_all_repos(g)
    elif args.delete:
        delete_blog(args.delete)
    elif args.show:
        show_articles()



# only works if index.html
def open_in_browser():
    output_html = 'output/index.html'  
    if os.path.exists(output_html):
        webbrowser.open_new_tab(f'file://{os.path.abspath(output_html)}')
        console.print("Opened the generated site in the web browser.", style="bold green")
    else:
        console.print("The output HTML file does not exist. Build the site first, or make sure your output is named index.html", style="bold red")


def add_repo(g, repo_name_or_true):
    if repo_name_or_true is True:
        # Show all repositories and ask for selection
        repos = get_user_repositories(g)
        repo_dict = {repo.name: repo for repo in repos}
        console.print("Select repositories to create blogs from (comma-separated):")
        for repo_name in repo_dict.keys():
            console.print(repo_name, style="italic blue")

        selected_repo_names = input().split(',')
        selected_repos = [repo_dict[name.strip()] for name in selected_repo_names if name.strip() in repo_dict]
    else:
        # Specific repository name provided
        selected_repos = [g.get_repo(repo_name_or_true)]

    repo_tags = {}
    for repo in selected_repos:
        tags = get_tags_for_repo(repo.name)
        # Ensure tags are a list, even if empty
        repo_tags[repo.name] = tags if tags is not None else []

    generate_blog_html(g, repo_tags)
    console.print("Added repositories and generated content.", style="cyan")


def add_all_repos(g):
    repos = get_user_repositories(g)
    repo_tags = {repo.name: get_tags_for_repo(repo.name) for repo in repos if get_tags_for_repo(repo.name) is not None}
    generate_blog_html(g, repo_tags)
    console.print("Added all repositories and generated content.", style="cyan")

def show_articles():
    content_dir = 'output/content'  # Replace with your actual content directory path
    articles = os.listdir(content_dir)
    
    table = Table(title="Articles in Content Folder", show_header=True, header_style="bold magenta")
    table.add_column("Article Name", style="italic blue")

    for article in articles:
        table.add_row(article)

    console.print(table)

if __name__ == "__main__":
    main()
