import argparse
import os, stat
import getpass
import platform
from pathlib import Path
import subprocess

from .subcommand import SubCommand
from .host_management import get_hosts, _multiple_hosts

__all__ = ["lsmounts", "mount", "unmount", "fssh"]

def get_mounts_dir():
    if "CLUSTER_UTILS_MOUNTS" not in os.environ:
        raise ValueError("The 'CLUSTER_UTILS_MOUNTS' environment variable is not defined")

    return Path(os.environ.get("CLUSTER_UTILS_MOUNTS")).expanduser()

def get_mount_adress(host, mount_target=False, host_config=None):
    if host_config is None:
        host_config = get_hosts().get(host, {})

    adress = f"{host_config.get('user', getpass.getuser())}@{host_config.get('mount_hostname', host)}"

    if mount_target:
        if mount_target is True:
            mount_target = host_config.get('mount_target', '')
        adress += f":{mount_target}"

    return adress

def _write_permissions(path, grant):
    """
    Adds or removes write permissions from a file or directory

    Parameters
    -----------
    path: str or Path
        The path to the file/directory for which you want to change write permissions
    grant: bool
        If true, adds write permissions, else removes them.
    """
    current_mode = os.stat(path).st_mode

    if grant:
        new_mode = current_mode | stat.S_IWUSR
    else:
        new_mode = current_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)

    os.chmod(path, new_mode)

def get_mounted():
    """Gets all the currently mounted hosts"""
    mounts_dir = get_mounts_dir()
    mounts = []

    if mounts_dir.is_dir():
        mounts = [d.name for d in mounts_dir.glob("*") if os.path.ismount(d)]
    
    return mounts

def lsmounts():
    """Lists the currently mounted hosts"""
    print(" ".join(get_mounted()))

@_multiple_hosts()
def mount(host, args):
    """
    Mounts hosts into the mounts directory.

    Parameters
    -------------
    host: list or str, optional
        The name of the host, as understood by ssh (and cluster-utils).
        If it's a list, it will mount all hosts.
    all: bool, optional
        If `True`, all known hosts are mounted (hosts is ignored).
    """
    mounts_dir = get_mounts_dir()

    # Make sure the mounts directory exists
    if not mounts_dir.exists():
        os.makedirs(mounts_dir)
    elif not mounts_dir.is_dir():
        raise ValueError(f"CLUSTER_UTILS_MOUNTS is set to {str(mounts_dir)}, which is a file.")

    host_mnt = mounts_dir / host

    if not host_mnt.exists():
        # Set write permissions for the mounts directory
	    # Check the line where we unset them below for the explanation.
        _write_permissions(mounts_dir, True)
        os.makedirs(host_mnt)

    # As a safety measure, we unset writing permissions for the directory
    # where we store all the mounts. A recursive search that finds the directory
    # will protect the mountpoints, but NOT THE CONTENTS of the mountpoint.
    # However, it will at least prompt you to check if you are sure to continue
    # the recursive search down the path.
    # This is not the main safety measure (check the definition of "rm" alias
    # on the main "activate" script), but it's a nice addition. You are never too
    # safe when it comes to your scientific work!
    # We do this here outside the if statement just in case the user had previously
    # created the directory but this is the first time cluster-utils uses it.
    _write_permissions(mounts_dir, False)

    subprocess.run(
        ["sshfs",
         "-o", "ServerAliveInterval=5,ServerAliveCountMax=2,ConnectTimeout=3,ConnectionAttempts=1",
         *args,
         get_mount_adress(host, mount_target=True), str(host_mnt)]
    )

def _arguments_mount(subparser):
    mount.argument_gen(subparser)
    
    subparser.add_argument("args", nargs=argparse.REMAINDER, 
        help="Additional args (options) that go into the sshfs command").completer = lambda *args, **kwargs: ""

@_multiple_hosts(all_getter=get_mounted)
def unmount(host):
    """
    Unmounts previously mounted directories.

    If a host is not mounted, it will do nothing.

    Parameters
    -------------
    hosts: list or str, optional
        The name of the host, as understood by ssh (and cluster-utils).
        If it's a list, it will mount all hosts.
    all: bool, optional
        If `True`, all mounted hosts are unmounted (hosts is ignored).
    """
    mounted_in = get_mounts_dir() / host

    try:
        OS = platform.system()
        if OS == "Darwin":
            commands = ["umount", str(mounted_in)]
        else:
            commands = ["fusermount", "-zu", str(mounted_in)]
        subprocess.run(commands).check_returncode()
    except subprocess.CalledProcessError:
        pass
    else:
        print(f"Succesfully unmounted {host}")

def remove_mount_point(host):

    if host in get_mounted():
        unmount(host)
    
    mounts_dir = get_mounts_dir()
    mount_point = mounts_dir / host

    if mount_point.is_dir():
        _write_permissions(mounts_dir, True)

        os.rmdir(mount_point)

    if len(list(mounts_dir.glob("*"))) > 0:
        _write_permissions(mounts_dir, False)

def get_host_from_path(path=""):
    """
    Given a path, returns the mounted host to which that path belongs.

    It also returns the path of the remote that is equivalent.

    Parameters
    ------------
    path: str or Path, optional
        The path for which we want the above mentioned returns. Defaults to the cwd.

    Returns
    -----------
    str:
        The name of the host
    Path:
        Remote path that corresponds to the given local path.
    """

    current_path = Path(path).resolve()
    mounts_dir = get_mounts_dir()

    if mounts_dir not in current_path.parents:
        raise ValueError(f"Your current path ({current_path}) is not inside the mounts directory")

    from_mounts = current_path.relative_to(mounts_dir)
    host = str(list(from_mounts.parents)[-2])

    hosts = get_hosts()

    host_dir = mounts_dir / host
    remote_root = Path(hosts[host].get("mount_target", ""))

    remote_dir = remote_root / current_path.relative_to(host_dir)

    return host, remote_dir

def fssh(command=None):
    """
    If inside a mountpoint, ssh into the equivalent remote directory.
    """
    host, remote_dir = get_host_from_path()

    if command is None or command == []:
        subprocess.run(["ssh", host, "-t", f'bash --init-file <(echo \". \$HOME/.bash_profile; cd {remote_dir}\")'])
    else:
        subprocess.run(["ssh", host, f'cd {remote_dir}; {" ".join(command)}'])

def _arguments_fssh(subparser):
    subparser.add_argument("command", nargs=argparse.REMAINDER, help="Command that you want to execute on this folder on the host."
        "If not provided, you will be left with a terminal at the remote directory")

    subparser.epilog = "Example: 'clu fssh mycommand --arg1 value --arg2' will run 'mycommand --arg1 value --arg2'"\
        " in the equivalent REMOTE folder."

SubCommand(lsmounts)
SubCommand(mount, _arguments_mount)
SubCommand(unmount, unmount.argument_gen)
SubCommand(fssh, _arguments_fssh)
