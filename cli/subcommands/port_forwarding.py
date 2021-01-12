import subprocess

from .mounting import get_host_from_path
from .host_management import get_hosts
from .subcommand import SubCommand

__all__ = ["remotejupyternb"]

def remotejupyternb(host=None, port=8003, path=""):
    """
    Runs the remote version of jupyter notebook and forwards the port to your local computer.

    Then, you can use the notebook GUI that is running on the remote as if it was running in your computer. 
    Therefore, you will be using the python kernels that are installed in your remote.

    To use this, you need to allow remote access to jupyter in your remote. For this, set the option
    `NotebookApp.allow_remote_access` to `True` in your jupyter config file.
    See: https://jupyter-notebook.readthedocs.io/en/stable/config.html

    Parameters
    -------------
    host: str, optional
        The name of the host, as understood by ssh (and cluster-utils).

        If not provided, clusterutils will assume that you want the host to be inferred from your
        current path (you are inside a mountpoint).
    port: int, optional
        The port where the jupyter notebook should run (and that will be forwarded to your equivalent local port)
    path: str or Path, optional
        The path to the place where jupyter should be run.
        
        If a host is provided, the path is taken as is. 
        Otherwise, this is a path relative to the mountpoint and clu calculates the equivalent remote path.
    """

    if host is None:
        host, path = get_host_from_path(path)

    subprocess.run(
        ["ssh", "-L", f"{port}:localhost:{port}", host, "-t", f"jupyter notebook {path} --port {port}"]
    )

def _arguments_remotejupyternb(subparser):
    
    subparser.add_argument("host", nargs="?",
        help="Host where to run the jupyter notebook. If not provided, it will be inferred from your current path"+
        " (you must be inside a mountpoint)").completer = lambda *args, **kwargs: get_hosts()
    
    subparser.add_argument("-p", "--port", help="The port where the jupyter notebook should run", default=8003, type=int)

    subparser.add_argument("--path", help="The path to the place where jupyter should be run. "+
        "If a host is provided, the path is taken as is. Otherwise, this is a path relative to the mountpoint and"+
        " clu calculates the equivalent remote path.", default="")

SubCommand(remotejupyternb, _arguments_remotejupyternb)