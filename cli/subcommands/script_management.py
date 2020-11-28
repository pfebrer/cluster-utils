import subprocess

from .host_management import _multiple_hosts, get_hosts
from .path import get_path
from .mounting import get_mount_adress
from .subcommand import SubCommand

__all__ = ["setup_host_scripts"]

_TOCOPY = ["scripts", "user-scripts", "activate", "install", "uninstall"]

@_multiple_hosts()
def setup_host_scripts(host):
    """
    Makes sure that the scripts on the host are updated.

    Also, runs the install script if cluster-utils is not installed.
    """
    host_config = get_hosts().get(host)

    clu_dir = host_config["clusterutils_dir"]

    subprocess.run(["ssh", host, f"if [ -d {clu_dir} ]; then rm -r {clu_dir}/" + "{" + f"{','.join(_TOCOPY)}"+ "}" + f"; else mkdir -p {clu_dir}; fi"])
    subprocess.run(["scp", "-r", *[str(get_path(d)) for d in _TOCOPY ],
        get_mount_adress(host, mount_target=host_config["clusterutils_dir"])])
    subprocess.run(["ssh", host, f"if [ ! -f {clu_dir}/.installed ]; then {clu_dir}/install; fi"])

# def set_script(what, target, path, host=None, global_=False):
#     """
#     Sets a script permanently for the user clusters
#     """


# def _arguments_setscript(subparser):
#     subparser.add_argument("what", nargs=1, choices=["env_loader", "runner"],
#         help="The kind of script that you want to add")

#     subparser.add_argument("target", nargs=1, help="The target for this script (i.e. the name of the program)")

#     subparser.add_argument("path", nargs=1, help="The path to the file that you want to add")

#     subparser.add_argument("--host", help="The name of the host that this script should be used on. If not"\
#         " provided, it will be interpreted as a generic script (i.e. for all hosts that don't implement it)")

#     subparser.add_argument("-g", "--global_", action="store_true", help="If set, the script is stored in the global"\
#         " scripts, otherwise it's installed in your personal scripts. Note that you should only use this flag if"\
#         " you pretend to share it with others by submitting a pull request to https://github.com/pfebrer/cluster-utils"
#     )

SubCommand(setup_host_scripts, setup_host_scripts.argument_gen, name="setuphostscripts")
# SubCommand(set_script, _arguments_setscript, name="setscript")

