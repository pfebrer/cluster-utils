#!/bash/bin

siestasub(){
	local SIESTA_RUN_SCRIPT=${SIESTA_RUN_SCRIPT:-$(cluget runner siesta)}
	local ENV_LOADER=${SIESTA_ENV_LOADER:-$(cluget env_loader siesta)}

	# Get the fdf file name 
        if [ $# == 0 ] || [[ ! "$(ls *.fdf)" =~ "$1" ]];
        then
		local fdfs=$(ls *.fdf)
                local SYSTEM=${fdfs//.fdf}
                for f in $fdfs; do
                        included=$(grep include $f)
                        included=${included#%include}
                        included=${included%.fdf*}
                        included=${included// }
                        SYSTEM=${SYSTEM/${included}/}
                done
		_clureport "$(echo $SYSTEM) will be used as the input fdf."
        else
                SYSTEM=$1
                shift
        fi
        SYSTEM=$(echo ${SYSTEM%.fdf})

	if [[ -z ${SYSTEM// } ]]; then return 1; fi

        ENV_LOADER=$ENV_LOADER SYSTEM=$SYSTEM JOB_NAME=$SYSTEM jobsub "$@" $SIESTA_RUN_SCRIPT
}
