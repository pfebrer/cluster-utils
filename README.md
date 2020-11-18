# Cluster-utils
Set of utilities to make your life easier with hpc clusters.

# How to install it

Just download or clone this repo

```
git clone https://github.com/pfebrer/cluster-utils.git
```

Then execute the install script
```
cluster-utils/install
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

- `siestasub`: Useful command to launch a siesta calculation. Calls `jobsub` to submit the siesta script defined by the `SIESTA_RUN_SCRIPT` environment variable, which defaults to [scripts/run_siesta.sh](scripts/run_siesta.sh). It has two ways of working:
  * **Explicit fdf**: `siestasub mystruct` or `siestasub mystruct.fdf` or `siestasub path/to/mystruct[.fdf]` It will submit the job using the specified fdf as input.
  * **Not specifying fdf**: Go to a directory and type `siestasub`. It will find the fdf file, even in case there are multiple fdfs it will decide which is the main one (checking the `%include` statements). In case there are multiple unrelated fdfs, there's nothing we can do to guess correctly.
  
  Note that in both cases, `SIESTA_RUN_SCRIPT` will be able to access the `SYSTEM` env variable, which is the name of the fdf file without extension.
  
  You can pass all the extra options for the job that `jobsub` accepts. For example: `siestasub -p farm4`.
  
  Also, you can set environment variables that `SIESTA_RUN_SCRIPT` uses. E.g. `SIESTA=/path/to/siesta siestasub` in case of the provided `run_siesta` script.

# Scripts

Scripts that are provided by the package:
- `run_siesta.sh`: Loads the appropiate environment (defined by `SIESTA_ENV_LOADER`, default to [scripts/load_intelsiesta.sh](scripts/load_intelsiesta.sh) and then runs siesta using the following environment variables:
  * `SIESTA`: Path to siesta, defaults to `siesta`.
  * `SYSTEM`: The name of the input fdf file, without extension.

- `load_intelsiesta.sh`: Loads the appropiate environment for an intel compilation of siesta to run in the hpcq.
