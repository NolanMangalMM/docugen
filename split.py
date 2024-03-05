"""
This file contains the logic needed to split a python repository into constituent parts.
It will keep things organized in a tree structure similarly to the directory structure of a file system.
However, it will split individual files into classes, and split classes into constituent classes as well as functions.
"""

import os
import ast
import json


def build_tree(directory):
    """
    Builds a tree structure representing the directory and its subdirectories,
    containing only files and folders with names ending in '.py'.
    """
    tree = {}
    contents = os.listdir(directory)

    for item in contents:
        path = os.path.join(directory, item)

        if os.path.isdir(path):
            tree[item] = build_tree(path)
        elif os.path.isfile(path) and item.endswith(".py"):
            tree[item] = None

    return tree
"""
# Example usage
root_dir = "/path/to/your/directory"
tree = build_tree(root_dir)
print(tree)
"""

def parse_file(file_path):
    with open(file_path, 'r') as file:
        source = file.read()

    tree = {}
    module = ast.parse(source)

    # Process functions
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    tree['functions'] = {func.name: parse_function(func, source) for func in functions}

    # Process classes
    classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
    tree['classes'] = {cls.name: parse_class(cls, source) for cls in classes}

    # Process module-level variables
    variables = [node.targets[0].id for node in module.body if isinstance(node, ast.Assign)]
    tree['variables'] = variables

    return tree

def parse_function(function_node, source):
    start_line = function_node.lineno
    end_line = function_node.body[-1].end_lineno if function_node.body else function_node.lineno
    function_source = "\n".join(get_lines(source, start_line, end_line))

    function_dict = {
        'source': function_source,
        'functions': {},
        'classes': {},
        'variables': [arg.arg for arg in function_node.args.args]
    }

    for node in function_node.body:
        if isinstance(node, ast.FunctionDef):
            function_dict['functions'][node.name] = parse_function(node, source)
        elif isinstance(node, ast.ClassDef):
            function_dict['classes'][node.name] = parse_class(node, source)

    return function_dict

def parse_class(class_node, source):
    start_line = class_node.lineno
    end_line = class_node.body[-1].end_lineno if class_node.body else class_node.lineno
    class_source = "\n".join(get_lines(source, start_line, end_line))

    class_dict = {
        'source': class_source,
        'functions': {},
        'classes': {},
        'variables': [target.id for stmt in class_node.body if isinstance(stmt, ast.AnnAssign) for target in stmt.targets]
    }

    for node in class_node.body:
        if isinstance(node, ast.FunctionDef):
            class_dict['functions'][node.name] = parse_function(node, source)
        elif isinstance(node, ast.ClassDef):
            class_dict['classes'][node.name] = parse_class(node, source)

    return class_dict

def get_lines(source, start_line, end_line):
    lines = source.splitlines()
    return lines[start_line - 1:end_line]

# Example usage
file_path = 'car.py'
tree = parse_file(file_path)
print(json.dumps(tree, indent=2))