import json
import os



# Function to format tree with info with children and depth
def format_tree_info( structure,node='root', prefix="", depth=0, is_last=True):
    print(structure)

    tree = ""
    num_children = len(structure.get(node, []))
    tree += f"{prefix}{'└── ' if is_last else '├── '}{node.split('/')[-1]} (Children: {num_children}, Depth: {depth})\n"
    
    if node in structure:
        children = structure[node]
        for i, child in enumerate(children):
            extension = "    " if is_last else "│   "
            tree += format_tree_info( structure,child, prefix + extension, depth + 1, i == len(children) - 1)
    return tree


# function to search for a file/folder, returns a string 
# cannot search in hidden files
def search(structure, target):
    path = []

    def find_path(node, target):
        if node == target:
            return True
        if node in structure:
            for child in structure[node]:
                path.append(child)
                if find_path(child, target):
                    return True
                path.pop()
        return False

    for root in structure:
        path.append(root)
        if find_path(root, target):
            return ' -> '.join(path)
        path.pop()
    return "Node not found"

# Function to create filters for the tree, criteria boolean function 
# see test.py for examples for usage
def filter(structure, criteria):
    filtered_structure = {}

    def find_parents(child_node, parents):
        for node, children in structure.items():
            if child_node in children:
                parents.append(node)
                find_parents(node, parents)
        return parents

    for node in structure:
        if criteria(node):
            parents = find_parents(node, [])
            for parent in parents:
                if parent not in filtered_structure:
                    filtered_structure[parent] = []
                if node not in filtered_structure:
                    filtered_structure[node] = []
                if node not in filtered_structure[parent]:
                    filtered_structure[parent].append(node)

    return {k: v for k, v in filtered_structure.items() if k in structure}

# basic format trees without any info
def format_tree(structure):
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

def max_depth(structure, node='root', current_depth=0):
    if not structure.get(node):  # If the node has no children
        return current_depth
    
    depths = []
    for child in structure[node]:
        if child in structure:  # Check if the child is a directory
            depths.append(max_depth(structure, child, current_depth + 1))
    
    return max(depths) if depths else current_depth

def count_files(structure, node='root'):
    file_count = 0

    # Check if the current node is a file (indicated by an empty list)
    if structure.get(node) == []:
        return 1

    # If the current node is a directory, iterate through its children
    for child in structure.get(node, []):
        file_count += count_files(structure, child)

    return file_count


def file_type_distribution(structure, node='root'):
    distribution = {}

    def add_extension(file_name):
        ext = file_name.split('.')[-1]
        if ext not in distribution:
            distribution[ext] = 1
        else:
            distribution[ext] += 1

    # Check if the current node is a file
    if structure.get(node) == []:
        add_extension(node)
    else:
        # If the current node is a directory, iterate through its children
        for child in structure.get(node, []):
            if structure.get(child) == []:
                add_extension(child)
            else:
                child_distribution = file_type_distribution(structure, child)
                for ext, count in child_distribution.items():
                    distribution[ext] = distribution.get(ext, 0) + count

    return distribution


def get_info(structure, node='root'):
    total_files = count_files(structure)
    depth = max_depth(structure)
    file_type = file_type_distribution(structure)

    res = (
        f"Total files: {total_files}\n"
        f"Maximum Depth: {depth}\n"
        f"File type distribution: {file_type}\n"
    )
    return res







# For git repos, returns a dictionary of the folders
def git_tree(g, repo_name):
    repo = g.get_user().get_repo(repo_name)
    contents = repo.get_contents("")
    directory_structure = {"root": []}

    def parse_contents(contents, parent_path="root"):
        for content in contents:
            relative_path = f"{parent_path}/{content.name}" if parent_path != "root" else content.name

            if content.type == "dir":
                directory_structure[parent_path].append(relative_path)
                directory_structure[relative_path] = []
                try:
                    subdir_contents = repo.get_contents(content.path)
                    parse_contents(subdir_contents, relative_path)
                except Exception as e:
                    print(f"Error accessing directory {relative_path}: {e}")
            else:
                directory_structure[parent_path].append(relative_path)
                directory_structure[relative_path] = []

    parse_contents(contents)
    return directory_structure







sample_structure = {
    "root": ["child1", "child2"],
    "child1": ["grandchild1", "grandchild2"],
    "child2": ["grandchild3"],
    "grandchild1": [],
    "grandchild2": [],
    "grandchild3": []
}

# Testing the functions
filtered_structure = filter(sample_structure, lambda node: "grandchild" in node)
filtered_tree = format_tree(filtered_structure)
search_result = search(sample_structure, "grandchild2")
tree_with_info = format_tree_info( sample_structure)
directory_tree = format_tree(sample_structure)

result_string = f"\nFilter Test:\n{filtered_tree}\nSearch Test:\n{search_result}\nTree with Node Information:\n{tree_with_info}\nDirectory Structure:\n{directory_tree}"
print(result_string)

from github import Github, Auth

# Authentication and GitHub Initialization
token = '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'
print(token)
auth = Auth.Token(token)
print(auth)
g = Github(auth=auth)
print(g)


# Visulise the repo
print(format_tree_info(structure= git_tree(g, 'mori.css')))

# Search for a file and return the file path
# cannot access hidden files
print(search(git_tree(g, 'mori.css'), 'docs-pic.png'))
# basic info 
l = get_info(sample_structure)
print(l)

