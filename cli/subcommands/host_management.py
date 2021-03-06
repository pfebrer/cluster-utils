from functools import wraps
from pathlib import Path
import getpass
import subprocess
import shutil
import yaml

from .path import get_path
from .subcommand import SubCommand

__all__ = ["send_keys", "setup_host", "remove_host"]

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
            " you have a good reason, this is by default the home directory (leave it empty)",
        "default": lambda key, config: ""
    },
    "host_auth_keys": {
        "description": "The path to the file where the host keeps register of authorized keys. The default should be fine"\
            " unless the cluster administrators are doing some fancy non-standard stuff",
        "default": lambda key, config: "~/.ssh/authorized_keys"
    },
    "clusterutils_dir": {
        "description": "The directory that clusterutils will use to save scripts and commands in this host.",
        "default": lambda key, config: "~/.cluster-utils"
    },
    "jump_through":{
        "description": "In some occasions, you can not ssh directly to your host, but you need to jump through another"\
            " server. This is the NAME OF THE HOST TO USE AS AN INTERMEDIATE STEP. If you set this to a not known host,"\
            " we will go on to set it up before finishing to set up this host."\
            " Notice that you can use as many jumping steps as you need. Also, you can use a host normally and as a 'jump_through'"\
            " at the same time.",
        "default": lambda key, config: ""
    }
}

def add_config_arguments(subparser):
    for key in KNOWN_CONFIG_KEYS:
        subparser.add_argument(f"--{key}", help=KNOWN_CONFIG_KEYS[key].get("description", ""))

def get_hosts(files=None):

    if files is None:
        files = [get_path("hosts.yaml")]
    
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
        filepath = get_path("hosts.yaml")
    
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

def write_host_ssh(config):
    # Write the parameters to the ssh config file
    ssh_config = Path("~/.ssh/config").expanduser()
    with ssh_config.open("a") as f:
        f.write("\n".join([
            f"\n\nHost {config['host']}",
            f" User {config['user']}",
            f" HostName {config['hostname']}"
        ]))
        if config.get("jump_through"):
            f.write(f"\n ProxyJump {config['jump_through']}")

def remove_host_ssh_config(host, ssh_config=None):

    if ssh_config is None:
        ssh_config = Path("~") / ".ssh" / "config"

    ssh_config = Path(ssh_config).expanduser()

    with ssh_config.open("r") as f:
        lines = f.readlines()
    
    host_block = False
    empty_lines = 0
    new_lines = []
    line = ""
    for line in lines:
        line = line.rstrip()
        if f"Host {host}" == line:
            host_block = True
        elif line.startswith("Host"):
            host_block = False

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

            returns = [function(host, **kwargs) for host in hosts]
            
            if len(returns) == 1:
                returns = returns[0]

            return returns
        
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
def send_keys(host, t="rsa", bits=None):
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

    config = get_hosts()[host]

    try:
        if config["host_auth_keys"] != "~/.ssh/authorized_keys" or shutil.which("ssh-copy-id") is None:
            process = subprocess.Popen(('cat', public_keys), stdout=subprocess.PIPE)
            output = subprocess.check_output(('ssh', host, f"cat >> {config['host_auth_keys']}"), stdin=process.stdout)
            process.wait()
        else:
            process = subprocess.run(["ssh-copy-id", "-i", public_keys, host])
            process.check_returncode()
        return True
    except:
        return False

def move_key_in_host(host, path):
    subprocess.run(["ssh", host, f"cp ~/.ssh/authorized_keys {path}"])

def _arguments_sendkey(subparser):
    send_keys.argument_gen(subparser)

    subparser.add_argument("-t", default="rsa",
        help="The encryption algorithm used to generate the key. See https://www.ssh.com/ssh/keygen/.")

def setup_host(config=None, use_defaults=False, no_conn=False, **kwargs):
    from .script_management import setup_host_scripts

    if config is None or config == []:
        config = {}

    if not isinstance(config, dict) :
        hosts_dict = get_hosts(config)

        for name, config_vals in hosts_dict.items():
            if "host" not in config_vals:
                config_vals["host"] = name
            setup_host(config=config_vals, use_defaults=use_defaults, no_conn=no_conn, **kwargs)
        return

    current_hosts = get_hosts()

    config.update({key: val for key, val in kwargs.items() if val is not None})

    def _ask_for_value(key, specs):

        default = specs.get("default", lambda key, config: None)(key, config)
        if use_defaults and key not in config:
            config[key] = default

        val = config.get(key)
        if val is None:
            
            description = specs.get("description", "")

            while val is None or val == "?":
                if val is not None:
                    print(f"\t({description})")
                val = input(f" - {key} ({default or ''}): ")
            config[key] = val or default or ""
        else:
            print(f" - {key}: {config[key]}")

    print("Following, we will ask for the parameters of this host:")
    print("Enter '?' for a help message.")
    for key, specs in KNOWN_CONFIG_KEYS.items():
        _ask_for_value(key, specs)

    jump_through = config.get("jump_through")
    if jump_through and jump_through not in current_hosts:
        setup_host(host=jump_through)

    write_host_ssh(config)

    add_hosts({config["host"]: config})

    if no_conn:
        return True

    if send_keys(config["host"]):
        setup_host_scripts(config["host"])
    else:
        print("(cluster-utils) WE COULD NOT SEND THE KEYS. Therefore we will not try to setup scripts in the host.")
        print(" When there is connection, you can try again:")
        print(f"     clu sendkeys {config['host']}")
        print(f"     clu setuphost {config['host']}")

def _file_extension_completer_gen(extension=""):

    def _file_extension_completer(prefix, *args, **kwargs):
        return [str (path) for path in Path().glob(f"{prefix}*.{extension}")]
    
    return _file_extension_completer

def _arguments_setuphost(subparser):
    subparser.add_argument("--config", nargs="*").completer = _file_extension_completer_gen("y?ml")

    add_config_arguments(subparser)

    subparser.add_argument("--use-defaults", action="store_true", help="If a default can be generated, the value for that"\
        " setting won't be asked. This is specially useful when setting up hosts with an incomplete yaml file to avoid prompts,"
        " but possibly not advisable if you are setting it up interactively."
    )

    subparser.add_argument("--no-conn", action="store_true", help="If set, clu understands that it should not try to connect"\
        " to the host and will skip the steps of sending ssh keys and setting up the scripts in the host. Useful when you don't"\
        " have a working connection to them or for testing"
    )

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

SubCommand(lshosts)
SubCommand(send_keys, _arguments_sendkey, name="sendkeys")
SubCommand(setup_host, _arguments_setuphost, name="setuphost")
SubCommand(remove_host, remove_host.argument_gen, name="removehost")
SubCommand(update_host_config, _arguments_update_host, name="updatehostconfig")

