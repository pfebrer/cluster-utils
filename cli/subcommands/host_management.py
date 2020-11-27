from functools import wraps
from pathlib import Path
import getpass
import subprocess
import yaml

from .path import get_path
from .subcommand import SubCommand

__all__ = ["send_key", "setup_host", "remove_host"]

KNOWN_CONFIG_KEYS = {
    "host": {
        "description": "This is the alias that the host will have. It doesn't need to be the real name"\
            " of the computer. ssh commands will be able to understand this name. If you mount the computer"\
            " in your filesystem, it will be the name of the directory."
    },
    "user": {
        "default": lambda key, config: getpass.getuser(),
        "description": "The user that will be used to log into the host. It is possible that you can access the"\
            " same computer with multiple users. In that case, we advise you to set up different hosts for each one,"\
            " maybe incorporating a suffix to discern between them. NOTE: You can always specify the user when you ssh"\
            " into the host, this is just the default user."
    },
    "hostname": {
        "description": "The real address, or host name, that should be used to communicate with the host.",
        "default": lambda key, config: config["host"]
    },
    "mount_hostname": {
        "description": "Some hosts have a dedicated address for large file transfers. If it's your case, indicate it"\
        "here.",
        "default": lambda key, config: config["hostname"]
    },
    "mount_target": {
        "description": "The directory of the remote host that you want to be mounted into your filesystem. Unless"\
            " you have a good reason, this is by default the home directory (leave it empty)"
    },
    "clusterutils_dir": {
        "description": "The directory that clusterutils will use to save scripts and commands in this host.",
        "default": lambda key, config: "~/.cluster-utils"
    }
}

def add_config_arguments(subparser):
    for key in KNOWN_CONFIG_KEYS:
        subparser.add_argument(f"--{key}", help=KNOWN_CONFIG_KEYS[key].get("description", ""))

def get_hosts(files=None):

    if files is None:
        files = [get_path("clusters.yaml")]
    
    if not isinstance(files, (str, Path)):
        hosts = {}
        for f in files:
            hosts.update(get_hosts(f))
        return hosts
    
    # If only one file is provided, then we can proceed to read it
    if isinstance(files, dict):
        return files

    yaml_file = Path(files)
    if not yaml_file.is_file():
        return {}

    with yaml_file.open() as f:
        hosts_dict = yaml.safe_load(f)

    return hosts_dict

def write_hosts(hosts, filepath=None):

    if filepath is None:
        filepath = get_path("clusters.yaml")
    
    with open(filepath, "w") as f:
        yaml.dump(hosts, f)

def add_hosts(hosts_dict):

    hosts = get_hosts()

    hosts.update(hosts_dict)

    write_hosts(hosts)

def remove_hosts_yaml(hosts):

    hosts_dict = get_hosts()

    for host in hosts:
        del hosts_dict[host]

    write_hosts(hosts_dict) 

def remove_host_ssh_config(host, ssh_config=None):

    if ssh_config is None:
        ssh_config = Path("~") / ".ssh" / "config"

    ssh_config = Path(ssh_config).expanduser()

    with ssh_config.open("r") as f:
        lines = f.readlines()
    
    host_block = False
    empty_lines = 0
    new_lines = []
    for line in lines:
        line = line.rstrip()
        if f"Host {host}" == line:
            host_block = True

        if line == "":
            empty_lines += 1
            host_block = False
        else: 
            empty_lines = 0
        
        if not host_block and empty_lines <= 1:
            new_lines.append(line)
    if line != "":
        new_lines.append("")
    
    with ssh_config.open("w") as f:
        f.write("\n".join(new_lines))

def _multiple_hosts(all_getter=get_hosts):

    def wrapper(function):

        @wraps(function)
        def wrapped(host=None, all=False, **kwargs):

            if all and all_getter is not None:
                hosts = all_getter()
            elif host is None:
                return
            else:
                hosts = [host] if isinstance(host, str) else host

            for host in hosts:
                function(host, **kwargs)

            return
        
        def argument_gen(subparser):
            subparser.add_argument(
                "host", metavar="H", nargs="*",
                help="The name(s) of the host(s), as understood by ssh (and cluster-utils)"
            ).completer = lambda *args, **kwargs: all_getter()

            if all_getter is not None:
                subparser.add_argument("--all", action="store_true", help="If set, the command"\
                f"is repeated for all hosts returned by {all_getter.__name__}.")

        wrapped.argument_gen = argument_gen
    
        return wrapped

    return wrapper

def lshosts():
    """
    Prints the list of hosts that are known by cluster-utils
    """
    print(" ".join(list(get_hosts())))

@_multiple_hosts()
def send_key(host, t="ecdsa", bits=None):
    """
    Sends the SSH key of this computer to the host. 
    
    If there is no key with the requested encryption, it creates it.

    Parameters
    -----------
    t: str
        The encryption algorithm used to generate the key.

        See https://www.ssh.com/ssh/keygen/.
    """
    public_keys = Path("~").expanduser() / ".ssh" / f"id_{t}.pub"

    if not public_keys.exists():
        if bits is None:
            bits = {"rsa": "4096", "ecdsa": "521"}.get(t)
        subprocess.run(["ssh-keygen", "-t", t, *(["-b", str(bits)] if bits else [])])
        if not public_keys.exists():
            return

    subprocess.run(["ssh-copy-id", "-i", public_keys, host if isinstance(host, str) else host[0]])

def _arguments_sendkey(subparser):
    send_key.argument_gen(subparser)

    subparser.add_argument("-t", default="ecdsa",
        help="The encryption algorithm used to generate the key. See https://www.ssh.com/ssh/keygen/.")

def setup_host(config=None, **kwargs):
    from .script_management import setup_host_scripts

    if config is None or config == []:
        config = {}

    if not isinstance(config, dict) :
        hosts_dict = get_hosts(config)

        for name, config_vals in hosts_dict.items():
            if "host" not in config_vals:
                config_vals["host"] = name
            setup_host(config=config_vals, **kwargs)
        return

    current_hosts = get_hosts()

    config.update({key: val for key, val in kwargs.items() if val is not None})

    print("Following, we will ask for the parameters of this host:")
    print("Enter '?' for a help message.")
    for key, specs in KNOWN_CONFIG_KEYS.items():
        if config.get(key) is None:
            default = specs.get("default", lambda key, config: "")(key, config)
            description = specs.get("description", "")

            val = None
            while val is None or val == "?":
                if val is not None:
                    print(f"\t({description})")
                val = input(f" - {key} ({default}): ")
            print("\033[K", end="")
            config[key] = val or default
        else:
            print(f" - {key}: {config[key]}")

    # Write the parameters to the ssh config file
    ssh_config = Path("~/.ssh/config").expanduser()
    with ssh_config.open("a") as f:
        f.writelines("\n".join([
            "",
            f"Host {config['host']}",
            f" User {config['user']}",
            f" HostName {config['hostname']}"
        ]))

    add_hosts({config["host"]: config})

    send_key(config["host"])

    setup_host_scripts(config["host"])

def _file_extension_completer_gen(extension=""):

    def _file_extension_completer(prefix, *args, **kwargs):
        return [str (path) for path in Path().glob(f"{prefix}*.{extension}")]
    
    return _file_extension_completer

def _arguments_setuphost(subparser):
    subparser.add_argument("--config", nargs="*").completer = _file_extension_completer_gen("y?ml")

    add_config_arguments(subparser)

@_multiple_hosts()
def remove_host(host):
    # There are 3 steps:
    # 1. Remove the mountpoint for that host
    from .mounting import remove_mount_point
    remove_mount_point(host)

    # 2. SSH config: Remove from the Host definition to the next empty line
    remove_host_ssh_config(host)

    # 3. Remove host from the yaml file
    remove_hosts_yaml([host])

@_multiple_hosts()
def update_host_config(host, **kwargs):
    """
    Updates the host configuration with the new values provided.

    It can also be used to set host options that are new and therefore have no value
    set in the current configuration.

    Basically, it removes the host and sets it up again, to make sure changes are really applied.
    """
    from .mounting import remove_mount_point

    try:
        host_config = get_hosts()[host]
    except KeyError:
        KeyError(f"Host {host} doesn't exist. Use the `clu setuphost` command if you want to setup a new host")

    remove_mount_point(host)

    remove_host_ssh_config(host)

    host_config.update({key: val for key, val in kwargs.items() if val is not None})
    setup_host(host_config)

def _arguments_update_host(subparser):
    update_host_config.argument_gen(subparser)

    add_config_arguments(subparser) 

SubCommand(send_key, _arguments_sendkey, name="sendkey")
SubCommand(setup_host, _arguments_setuphost, name="setuphost")
SubCommand(remove_host, remove_host.argument_gen, name="removehost")
SubCommand(update_host_config, _arguments_update_host, name="updatehostconfig")

