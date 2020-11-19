#!/bash/bin

siestasub(){
	local SIESTA_RUN_SCRIPT=${SIESTA_RUN_SCRIPT:-$(clusterutils getrunner siesta)}
	local ENV_LOADER=${SIESTA_RUN_SCRIPT:-$(clusterutils getenvloader siesta)}

	# Get the fdf file name 
        if [ $# == 0 ] || [[ ! "$(ls *.fdf)" =~ "$1" ]];
        then
                local fdfs=$(ls *.fdf)
                local SYSTEM=$fdfs
                for f in $fdfs; do
                        included=$(grep include $f)
                        included=$(echo ${included/"%include"/})
                        SYSTEM=${SYSTEM/$included/}
                done
		clusterutils report "$(echo $SYSTEM) will be used as the input fdf."
        else
                SYSTEM=$1
                shift
        fi
        SYSTEM=$(echo ${SYSTEM%.fdf})

	if [[ -z ${SYSTEM// } ]]; then return 1; fi

        ENV_LOADER=$ENV_LOADER SYSTEM=$SYSTEM jobsub -J "$SYSTEM" "$@" $SIESTA_RUN_SCRIPT
}
