#!/bash/bin

siestasub(){
	SIESTA_RUN_SCRIPT=${SIESTA_RUN_SCRIPT:-"$CLUSTER_UTILS_ROOT"/scripts/run_siesta.sh}
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

        SYSTEM=$SYSTEM jobsub -J "$SYSTEM" "$@" $SIESTA_RUN_SCRIPT
}
