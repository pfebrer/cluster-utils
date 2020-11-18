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

siestasub(){
	# Get the fdf file name 
        if [ $# == 0 ] || [[ ! "$(ls *.fdf)" =~ "$1" ]];
        then
                fdfs=$(ls *.fdf)
                SYSTEM=$fdfs
                for f in $fdfs; do
                        included=$(grep include $f)
                        included=$(echo ${included/"%include"/})
                        SYSTEM=${SYSTEM/$included/}
                done
        else
                SYSTEM=$1
                shift
        fi
        SYSTEM=$(echo ${SYSTEM%.fdf})

        jobsub -J "$SYSTEM" "$@" $CLUSTER_UTILS_ROOT/scripts/run_siesta.sh $SYSTEM
}
