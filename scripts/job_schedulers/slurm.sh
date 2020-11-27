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
	sbatch --export=ALL --no-requeue "$@"
}
