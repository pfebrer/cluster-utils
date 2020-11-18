#!/bin/bash

ENV_LOADER=${SIESTA_ENV_LOADER:-$CLUSTER_UTILS_ROOT/scripts/load_intelsiesta.sh}
source $ENV_LOADER

ulimit -l unlimited
ulimit -s 51200
ulimit -n 51200

SIESTA=${SIESTA:-siesta}
SYSTEM=${SYSTEM:-$1}

'mpirun' $SIESTA < $SYSTEM'.fdf' > $SYSTEM'.out' 
