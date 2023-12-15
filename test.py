import markdown2

def format_directory_structure(structure):
    def is_directory(item):
        return item in structure

    def format_tree(node, prefix="", is_last=True):
        tree = ""
        if node:  # For non-root nodes
            tree += f"{prefix}{'└── ' if is_last else '├── '}{node.split('/')[-1]}\n"

        if node in structure:
            children = structure[node]
            for i, child in enumerate(children):
                extension = "    " if is_last else "│   "
                tree += format_tree(child.split('/')[-1], prefix + extension, i == len(children) - 1)
        return tree

    # Start from the roots (top-level directories)
    roots = [node for node in structure if not any(node in items for items in structure.values())]
    return '\n'.join(format_tree(root) for root in roots).strip()

# Example usage
directory_structure = {
    'day1': ['day1/pt1', 'day2', 'day1/pt1'],
    'day2': ['day2/pt2', 'day3'],
    'day3': ['day3/pt2', 'day4'],
    'day4': ['day4/pt2', 'day4/pt1']
}
print(format_directory_structure(directory_structure))

ll = markdown2.markdown(format_directory_structure(directory_structure))
print(ll)


