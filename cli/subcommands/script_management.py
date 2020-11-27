import subprocess

from .host_management import _multiple_hosts, get_hosts
from .path import get_path
from .mounting import get_mount_adress
from .subcommand import SubCommand

__all__ = ["setup_host_scripts"]

_TOCOPY = ["scripts", "user-scripts", "activate", "install", "uninstall"]

@_multiple_hosts()
def setup_host_scripts(host):
    host_config = get_hosts().get(host)

    clu_dir = host_config["clusterutils_dir"]

    subprocess.run(["ssh", host, f"if [ -d {clu_dir} ]; then rm -r {clu_dir}/" + "{" + f"{','.join(_TOCOPY)}"+ "}" + f"; else mkdir -p {clu_dir}; fi"])
    subprocess.run(["scp", "-r", *[str(get_path(d)) for d in _TOCOPY ],
        get_mount_adress(host, mount_target=host_config["clusterutils_dir"])])
    subprocess.run(["ssh", host, f"if [ ! -f {clu_dir}/.installed ]; then {clu_dir}/install; fi"])

SubCommand(setup_host_scripts, setup_host_scripts.argument_gen, name="setuphostscripts")

