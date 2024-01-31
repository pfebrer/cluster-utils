#!/bin/bash

source $ENV_LOADER

ulimit -l unlimited
ulimit -s unlimited
ulimit -n 51200

SIESTA=${SIESTA:-siesta}
SYSTEM=${SYSTEM:-$1}
SIESTA_MPIRUN=${SIESTA_MPIRUN:mpirun}

${SIESTA_MPIRUN} $SIESTA < $SYSTEM'.fdf' > $SYSTEM'.out' 
