import os
import argparse
import subprocess

def is_git_installed():
    """Check if git is installed on the system."""
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def get_git_tracked_files(path="."):
    """Get the list of files tracked by git in the current branch."""
    try:
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path, text=True).strip()
        tracked_files = subprocess.check_output(["git", "ls-tree", "-r", branch_name, "--name-only"], cwd=path, text=True)
        return set(tracked_files.splitlines())
    except subprocess.CalledProcessError:
        return set()

def generate_tree(path=".", prefix="", show_hidden=False, hide_config=False, git_only=False, config_exceptions=None, git_tracked_files=None, exclude=None):
    """
    Recursively generates an ASCII directory tree.

    Args:
        path (str): Path to the directory to generate the tree for.
        prefix (str): Prefix for the current level of the tree.
        show_hidden (bool): Whether to include all hidden files and directories.
        hide_config (bool): Whether to hide special configuration files.
        git_only (bool): Whether to include only files tracked by git.
        config_exceptions (list): List of configuration files to always show unless hidden.
        git_tracked_files (set): Set of git-tracked file paths.
        exclude (list): List of file or directory names to exclude.

    Returns:
        str: ASCII representation of the directory tree.
    """
    if config_exceptions is None:
        config_exceptions = [".gitignore", ".dockerignore"]

    if exclude is None:
        exclude = []

    entries = []
    for e in sorted(os.listdir(path)):
        full_path = os.path.join(path, e)
        relative_path = os.path.relpath(full_path, start=path)

        if e in exclude:
            continue

        if git_only and git_tracked_files is not None and not os.path.isdir(full_path) and relative_path not in git_tracked_files:
            continue

        if not show_hidden and e.startswith("."):
            if hide_config or e not in config_exceptions:
                continue

        entries.append(e)

    tree = []

    for index, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "

        tree.append(f"{prefix}{connector}{entry}")

        if os.path.isdir(full_path):
            extension = "    " if is_last else "│   "
            tree.append(generate_tree(full_path, prefix=prefix + extension, show_hidden=show_hidden, hide_config=hide_config, git_only=git_only, config_exceptions=config_exceptions, git_tracked_files=git_tracked_files, exclude=exclude))

    return "\n".join(tree)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an ASCII directory tree.")
    parser.add_argument(
        "path",
        metavar="path",
        type=str,
        nargs="?",
        default=".",
        help="The root directory to start the tree from (default: current directory)."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s", "--show-hidden",
        action="store_true",
        help="Include all hidden files and directories."
    )
    group.add_argument(
        "-c", "--hide-config",
        action="store_true",
        help="Hide special configuration files like .gitignore and .dockerignore."
    )
    parser.add_argument(
        "-g", "--git-only",
        action="store_true",
        help="Show only files tracked by git on the current branch."
    )
    parser.add_argument(
        "-e", "--exclude",
        action="append",
        default=[],
        help="Exclude files or directories with this name (can be used multiple times)."
    )

    args = parser.parse_args()

    git_tracked_files = None
    if args.git_only:
        if not is_git_installed():
            print("Error: git is not installed or not available in PATH.")
            exit(1)
        git_tracked_files = get_git_tracked_files(path=args.path)

    print("Directory Tree:\n")
    print(generate_tree(path=args.path, show_hidden=args.show_hidden, hide_config=args.hide_config, git_only=args.git_only, git_tracked_files=git_tracked_files, exclude=args.exclude))
