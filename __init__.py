
#!/usr/bin/env python

from rich.console import Console
from rich.table import Table
import argparse
import webbrowser
from github import Github, Auth
import os 
from generate_site import  build_blog_from_content, add_repo, delete_blog, get_user_repositories, get_tags_for_repo, generate_blog_html
import sys


console = Console()

def main():

    if len(sys.argv) == 1:
            console.print(""" 
               ,--,                                                             ___             
    ,---,    ,--.'|                                                 ,--,      ,--.'|_           
  ,---.'|    |  | :       ,---.                                   ,--.'|      |  | :,'          
  |   | :    :  : '      '   ,'\    ,----._,.           ,----._,. |  |,       :  : ' :          
  :   : :    |  ' |     /   /   |  /   /  ' /          /   /  ' / `--'_     .;__,'  /           
  :     |,-. '  | |    .   ; ,. : |   :     |         |   :     | ,' ,'|    |  |   |            
  |   : '  | |  | :    '   | |: : |   | .\  .         |   | .\  . '  | |    :__,'| :            
  |   |  / : '  : |__  '   | .; : .   ; ';  |         .   ; ';  | |  | :      '  : |__          
  '   : |: | |  | '.'| |   :    | '   .   . |         '   .   . | '  : |__    |  | '.'|         
  |   | '/ : ;  :    ;  \   \  /   `---`-'| |          `---`-'| | |  | '.'|   ;  :    ;         
  |   :    | |  ,   /    `----'    .'__/\_: |          .'__/\_: | ;  :    ;   |  ,   /          
  /    \  /   ---`-'               |   :    :          |   :    : |  ,   /     ---`-'           
  `-'----'                          \   \  /            \   \  /   ---`-'                       
                                     `--`-'              `--`-'                                 
""", style='yellow',justify='left')
            console.print(""" :sparkles: Welcome to Blog Git - A minimal static site generator for your Github repos.:sparkles:\n  """, style="bold green",justify='left')
            console.print("""To get started enter your username or use a token to get access to private repositories, you can add
repos using the add command and generate the site using the build command.By default each blog content is 
populated with it's READme.md if it exists. All the content is available in the output/content folder 
                             """,style='yellow',justify='left')
            console.print("Commands available: \n", style='bold underline green')
            console.print(" [yellow]build  [/yellow] - Build the static site from content")
            console.print(" [yellow]add  [/yellow]   - Add a repository or multiple repositories to the blog")
            console.print(" [yellow]addall  [/yellow]- Add all repositories to the blog")
            console.print(" [yellow]delete  [/yellow]- Delete a specific blog")
            console.print(" [yellow]show    [/yellow]- Show a list of all articles already in content")
            console.print(" [yellow]open    [/yellow]- Open the generated site in a web browser\n")
            console.print("Use 'bloggit --help' for more information on a specific command.")
            exit(0)

    parser = argparse.ArgumentParser(
        description="GitBlog: A Static Site Generator CLI for GitHub repositories.")
    
    parser.add_argument("--token", help="GitHub token for authentication")

    subparsers = parser.add_subparsers(dest="command")

    # Build command
    parser_build = subparsers.add_parser("build", help="Build the static site from content")
    #username
    parser.add_argument("--username", help="GitHub username for accessing public repositories")


    # Add command
    parser_add = subparsers.add_parser("add", help="Add a repository to the blog")
    parser_add.add_argument("repo_name", nargs='?', default=None, help="Name of the repository to add")

    # Addall command
    parser_addall = subparsers.add_parser("addall", help="Add all repositories to the blog")

    # Delete command
    parser_delete = subparsers.add_parser("delete", help="Delete a specific blog")
    parser_delete.add_argument("blog_name", help="Name of the blog to delete")

    # Show command
    parser_show = subparsers.add_parser("show", help="Show a list of all articles")

    # Open command
    parser_open = subparsers.add_parser("open", help="Open the generated site in a web browser")

    args = parser.parse_args()
    if args.command == "delete":
        delete_blog(args.blog_name)
    elif args.command == "show":
        show_articles()
    elif args.command == "open":
        open_in_browser()
    elif args.command == "build":
        build_blog_from_content()

    
    if not args.token and not args.username:
        console.print("Either GitHub token or username is required.", style="bold red underline")
        exit(1)

    if args.token:
        g = Github(auth=Auth.Token(args.token))
    else:
        g = Github(args.username)

    # only can add after getting github
    if args.command == "add":
        add_repo(g, args.repo_name)
    elif args.command == "addall":
        add_all_repos(g)




# only works if index.html
def open_in_browser():
    output_html = 'output/index.html'  
    if os.path.exists(output_html):
        webbrowser.open_new_tab(f'file://{os.path.abspath(output_html)}')
        console.print("Opened the generated site in the web browser.", style="bold green")
    else:
        console.print("The output HTML file does not exist. Build the site first, or make sure your output is named index.html", style="bold red")


def add_repo(g, repo_name_or_true):
    repos = get_user_repositories(g)
    repo_dict = {repo.name: repo for repo in repos}
    if repo_name_or_true is None or repo_name_or_true is True:
        console.print("Select repositories to create blogs from (comma-separated):")
        for repo_name in repo_dict.keys():
            console.print(repo_name, style="italic blue")

        selected_repo_names = input().split(',')
        print(selected_repo_names)
        selected_repos = [repo_dict[name.strip()] for name in selected_repo_names if name.strip() in repo_dict]
        print(selected_repos)
    else:
        selected_repos = []
        if repo_name_or_true in repo_dict:
            selected_repos.append(repo_dict[repo_name_or_true])
        else:
            console.print(f"Repository '{repo_name_or_true}' not found.", style="bold red")

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
