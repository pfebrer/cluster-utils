from .subcommand import SubCommand
import os
from pathlib import Path

__all__ = ["path"]

def get_path(path=""):
    """Returns a path starting from cluster-utils root"""
    return Path(os.environ.get("CLUSTER_UTILS_ROOT")).expanduser()/path

def path(path):
    """Prints a path starting from cluster-utils root"""
    print(str(get_path(path)))

def _arguments_path(subparser):
    subparser.add_argument("path", nargs="?")

SubCommand(path, _arguments_path)