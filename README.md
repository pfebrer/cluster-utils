# Some people do yoga, others use `cluster-utils`

*Have you ever gone crazy trying to remember all the ways in which your different clusters work?*

*And after the assigned period ends, you will need to use a different one.*

![](https://sa1s3optim.patientpop.com/assets/images/provider/photos/2125909.jpg)

`cluster-utils` is a set of utilities to make your life easier with hpc clusters. The main goal is that you can use the **same interface for all clusters that you work on**, while helping you keep your **workspace clean**.

It consists of mainly four parts:
- **Commands** ([code](commands), [docs](#commands)): The commands that are supposed to work on all clusters that you use.
- **Scripts** ([code](scripts), [docs](#commands)): Scripts that are specific to each cluster. `cluster-utils` keeps them well organized so that they can be found when needed.
- **Cluster manager** ([docs](#cluster-manager)): It helps you setting up and removing clusters for access through ssh. More importantly, it allows you to **mount all your clusters in a very organied and secure way**.
- **The `clusterutils` CLI** ([code](cli)), which helps glueing everything together. It is heavily used internally, but you probably won't need to use it much, as the things you want to do are made available by the commands (first point in this list). 

Different clusters are (brace yourself) very different in their specifications (libraries, module loading, permissions, etc), that's why:
- The core of `cluster-utils` (i.e. commands and CLI) is written in shell scripts that focus on **sticking to the most standard things**.
- The package installation **doesn't require any permission**. It only adds one line to `~/.bashrc` to trigger its activation when you login. (in case you aren't even allowed to write to your home directory, we recommend you to start a revolution).

# Make it personal

We also acknowledge that **you may have special needs that are not fulfilled by the provided scripts**. That's why the `CLUSTER_UTILS_USERSCRIPTS` environment variable [is defined](activate), which points to a folder that needs to have the same structure as [the scripts folder](scripts). When looking for scripts, `cluster-utils` will **prefer the ones that you have defined over the provided ones if it finds them**. 

By default, the user specific folder is expected to be in the first level of the package as `user-scripts`. The reason for this is that there should be a "clean" version of `cluster-utils`, which we all share (https://github.com/pfebrer/cluster-utils/master) and then a branch for each person, where `user-scripts` is defined. In this way you can **keep your personalized version on github** (to instantly clone it to/update it from any cluster, keeping all of them in sync) **without interfering with the main version**.

Although there's this possibility to easily customize the package for yourself, **it would be great that we can collaborate to gather sharable scripts** and incorporate them in the shared version. In this way, anyone that is given access to unexplored territory (a new cluster) may be lucky enough to find that `cluster-utils` already contains scripts for them to succesfully submit calculations, saving them both wasted time and money spent on therapies to compensate for the thousands of failed attempts at doing science.

# How to install it

Just download or clone this repo

```
git clone https://github.com/pfebrer/cluster-utils.git
```

Then execute the install script
```
cluster-utils/install
```

Similarly run the uninstall script to uninstall:
```
clusterutils/uninstall
```

# Commands

Following you can find a brief description of the commands that `cluster-utils` provides to you:

### Slurm related

- `jobdir`: **Returns the directory from where a given job has been submitted**. If more than one job matches your selection, the path for each one is returned.
There are two ways to call it:
  * With the **job ID** (only one argument): `jobdir 12745`
  * Specifying options that are **valid for squeue**: `jobdir -u your_username`
 
- `jobcd`: **Uses `jobdir` to retrieve a directory and then cds into it.** It works exactly the same as `jobdir`, but note that if multiple directories are obtained, `jobcd` uses the first one.

- `jobsub`: Generic command that uses sbatch to submit a job. It only adds `--export=ALL` so that your job script can use environment variables. Probably not worth to use by itself, but serves as a common command that job submitting commands can use.

### Siesta related

- `siestasub`: Useful command to launch a siesta calculation. Calls `jobsub` to submit the siesta script. This script is defined by `SIESTA_RUN_SCRIPT` environment variable, which defaults to `siesta`. The script is loaded doing `clusterutils getrunner $SIESTA_RUN_SCRIPT`. `siestasub` has two ways of working:
  * **Explicit fdf**: `siestasub mystruct` or `siestasub mystruct.fdf` or `siestasub path/to/mystruct[.fdf]` It will submit the job using the specified fdf as input.
  * **Not specifying fdf**: Go to a directory and type `siestasub`. It will find the fdf file, even in case there are multiple fdfs it will decide which is the main one (checking the `%include` statements). In case there are multiple unrelated fdfs, there's nothing we can do to guess correctly.
  
  Note that in both cases, `SIESTA_RUN_SCRIPT` will be able to access the `SYSTEM` env variable, which is the name of the fdf file without extension.
  
  You can pass all the extra options for the job that `jobsub` accepts. For example: `siestasub -p farm4`.
  
  Also, you can set environment variables that `SIESTA_RUN_SCRIPT` uses. E.g. `SIESTA=/path/to/siesta siestasub` in case of the provided `run_siesta` script.

# Scripts

Following, you will find all the scripts that are already provided by the package.

### Generic

*This scripts will be used if no equally named script is provided for the specific cluster*

- `run_siesta.sh`: Loads the appropiate environment (defined by `SIESTA_ENV_LOADER`, default to `siesta` and obtained doing `clusterutils getenvloader $SIESTA_ENV_LOADER`) and then runs siesta using the following environment variables:
  * `SIESTA`: Path to siesta, defaults to `siesta`.
  * `SYSTEM`: The name of the input fdf file, without extension.

### ICN2 HPCQ cluster

*Scripts used when in the hpcq cluster*

- `load_siesta.sh`: Loads the appropiate environment for an intel (maybe gnu too, idk?) compilation of siesta to run in the hpcq.

# Cluster manager

*Keep it clean but powerful.*

### Managing ssh keys

Whenever you get access to a new cluster, use:

```
clusterutils setupcluster
```

to set it up. Follow the instructions, and you will end up with **ssh keys configured for password-less access** to your new cluster.

*But that's not all!*

If your time in a cluster is over, don't keep its configuration, you need to move on! Use

```
clusterutils removecluster <Your cluster>
```

to **remove it from your ssh configuration**. It will also get unmounted and its mountpoint removed (see next section to understand this).

### Managing mounts

This functionality uses [`fuse`](https://github.com/libfuse/libfuse) and [`sshfs`](https://github.com/libfuse/sshfs), so please install them in your computer.
On linux: `sudo apt-get install sshfs fuse`.
On MacOS: Download and install the macFUSE package from [the latest release](https://github.com/osxfuse/osxfuse/releases/).

> Just in case you are not familiar with the term "mount", the idea is to have a directory in your computer that lets you access the remote cluster just as if it
was part of your filesystem. The files are not really in your computer, so it doesn't take up extra space.*

Having your clusters mounted is very powerful, because there's **no need to copy each file that you need to process**. However, it can be a bit messy if your
connection is weak (terminal freezes), you have your mountpoints all over the computer (unorganized) and you have the mountpoints unprotected (dangerous for your cluster content). These problems are solvable, but you need to know what you are doing.

Luckily `cluster-utils` manages all these problems for you:
- **Avoids terminal freezes** by telling sshfs to give up on the connection if it is failing to connect.
- **Keeps everything organized** in a single folder defined by `CLUSTER_UTILS_MOUNTS`, which defaults to `cluster-utils/mounts`.
- **Implements security barriers** so that you don't accidentally remove the contents of your cluster:
    * On activation, `cluster-utils` **sets the `rm` alias to `rm --one-file-system`**. In this way, if a recursive deletion accidentally gets to a mounted cluster, it is not going to remove it (you will get an error message). It also sets `alias sudo="sudo "` to make sure that sudo also sees the alias ([explanation](https://askubuntu.com/a/22043))
    * Also it removes **write permissions from the mounts directory**. It only sets them back temporarily when mountpoints need to be added/removed. This will not protect your content, but at least it will trigger a warning asking if you want to continue the recursive deletion inside the mountpoints (in which case you will not say "y" or "YES" or "Y"). The alias protection is enough, but you are never too safe when it comes to your (potentially lifetime) scientific work.
    
    These two safety measures protect you from `rm -r *` outside your mounts directory. The second measure even protects you from doing `rm -r *` inside the mounts directory (not totally, it will trigger a warning, the rest is on you). However this does not protect you from `rm -r my_cluster/*`, so please don't do it unless you really want to remove all your work from the cluster (it goes without saying, but it's better to warn about the limits of your protection anyway).
    
**Extra**: backup management feature coming soon!

But enough about security! Mounting your cluster is as simple as (once you have [set it up](#managing-ssh-keys)):

```
clusterutils mount <Your cluster>
```

Have fun accessing all your cluster contents from your computer!

A very nice feature that you can use is,from inside a mounted folder, type:

```
clusterutils fssh
```

if you want to go to the corresponding folder in the cluster.

Lastly, run `cluster unmount <Your cluster>` if you wish to unmount it.

