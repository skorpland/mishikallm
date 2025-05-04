import os
import ast
import sys
from typing import List, Tuple, Optional


def find_mishikallm_type_hints(directory: str) -> List[Tuple[str, int, str]]:
    """
    Recursively search for Python files in the given directory
    and find type hints containing 'mishikallm.'.

    Args:
        directory (str): The root directory to search for Python files

    Returns:
        List of tuples containing (file_path, line_number, type_hint)
    """
    mishikallm_type_hints = []

    def is_mishikallm_type_hint(node):
        """
        Recursively check if a type annotation contains 'mishikallm.'

        Handles more complex type hints like:
        - Optional[mishikallm.Type]
        - Union[mishikallm.Type1, mishikallm.Type2]
        - Nested type hints
        """
        try:
            # Convert node to string representation
            type_str = ast.unparse(node)

            # Direct check for mishikallm in type string
            if "mishikallm." in type_str:
                return True

            # Handle more complex type hints
            if isinstance(node, ast.Subscript):
                # Check Union or Optional types
                if isinstance(node.value, ast.Name) and node.value.id in [
                    "Union",
                    "Optional",
                ]:
                    # Check each element in the Union/Optional type
                    if isinstance(node.slice, ast.Tuple):
                        return any(is_mishikallm_type_hint(elt) for elt in node.slice.elts)
                    else:
                        return is_mishikallm_type_hint(node.slice)

                # Recursive check for subscripted types
                return is_mishikallm_type_hint(node.value) or is_mishikallm_type_hint(
                    node.slice
                )

            # Recursive check for attribute types
            if isinstance(node, ast.Attribute):
                return "mishikallm." in ast.unparse(node)

            # Recursive check for name types
            if isinstance(node, ast.Name):
                return "mishikallm" in node.id

            return False
        except Exception:
            # Fallback to string checking if parsing fails
            try:
                return "mishikallm." in ast.unparse(node)
            except:
                return False

    def scan_file(file_path: str):
        """
        Scan a single Python file for MishikaLLM type hints
        """
        try:
            # Use utf-8-sig to handle files with BOM, ignore errors
            with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as file:
                tree = ast.parse(file.read())

            for node in ast.walk(tree):
                # Check type annotations in variable annotations
                if isinstance(node, ast.AnnAssign) and node.annotation:
                    if is_mishikallm_type_hint(node.annotation):
                        mishikallm_type_hints.append(
                            (file_path, node.lineno, ast.unparse(node.annotation))
                        )

                # Check type hints in function arguments
                elif isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        if arg.annotation and is_mishikallm_type_hint(arg.annotation):
                            mishikallm_type_hints.append(
                                (file_path, arg.lineno, ast.unparse(arg.annotation))
                            )

                    # Check return type annotation
                    if node.returns and is_mishikallm_type_hint(node.returns):
                        mishikallm_type_hints.append(
                            (file_path, node.lineno, ast.unparse(node.returns))
                        )
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)

    # Recursively walk through directory
    for root, dirs, files in os.walk(directory):
        # Remove virtual environment and cache directories from search
        dirs[:] = [
            d
            for d in dirs
            if not any(
                venv in d
                for venv in [
                    "venv",
                    "env",
                    "myenv",
                    ".venv",
                    "__pycache__",
                    ".pytest_cache",
                ]
            )
        ]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                # Skip files in virtual environment or cache directories
                if not any(
                    venv in full_path
                    for venv in [
                        "venv",
                        "env",
                        "myenv",
                        ".venv",
                        "__pycache__",
                        ".pytest_cache",
                    ]
                ):
                    scan_file(full_path)

    return mishikallm_type_hints


def main():
    # Get directory from command line argument or use current directory
    directory = "./mishikallm/"

    # Find MishikaLLM type hints
    results = find_mishikallm_type_hints(directory)

    # Print results
    if results:
        print("MishikaLLM Type Hints Found:")
        for file_path, line_num, type_hint in results:
            print(f"{file_path}:{line_num} - {type_hint}")
    else:
        print("No MishikaLLM type hints found.")


if __name__ == "__main__":
    main()
