#!/bin/bash

jobdir(){
	ARGS="$@"
        if [ $# == 1 ]; then ARGS="-j $1"; fi
	squeue --noheader $ARGS --format "%Z"
}

jobcd(){
	JOBDIR=$(jobdir "$@")
	cd $JOBDIR
}

jobsub(){

	JOB_NAME=${JOB_NAME:-job}

	if which sbatch 2>/dev/null; then
		sbatch --export=ALL --no-requeue -J $JOB_NAME "$@"
	else
		qsub -V -N $JOB_NAME "$@"
	fi

}
