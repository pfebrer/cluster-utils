_clupath(){
    echo "${CLUSTER_UTILS_ROOT}/$1"
}

cluload(){
    local env_loader=$(cluget env_loader $1)

    if [ ! -z "${env_loader// }" ]; then
        _clureport "Loading environment <$1> from ${env_loader}..."
        source "${env_loader}"
        if $?; 
        then _clureport "Succeeded." 
            else _clureport "Failed"
        fi
    else
        _clureport "No environment loader was found for <$1>"
    fi
}

_clugethost(){
    HOSTNAME=$(hostname)

    _cluparsehost $HOSTNAME
}

_cluparsehost(){
    case $1 in
        hpcq*)
            echo hpcq
        ;;
        *)
            echo unknown
        ;;
    esac
}

cluget(){
    # What does the user want (a runner script, an env loader, etc...)
    local what=$1

    # Call .parsedir, which will define the following variables:
    # $directory, $userdirectory, $prefix
    _cluparseget "$what"

    # Define all the candidates (the order of the candidates matter)
    # The order defined here is:
    # 	1. User directory, cluster-specific
    #	2. Cluster-utils provided, cluster-specific
    #	3. User directory, generic
    #	4. Cluster-utils provided, generic.
    #	5. spec provided was a full path to the file
    # local candidates=" ${userdirectory}/${CLUSTER_UTILS_HOST}/${prefix}_$2.sh"
    # candidates+=" $(_clupath ${directory}/${CLUSTER_UTILS_HOST}/${prefix}_$2.sh)"
    # candidates+=" ${userdirectory}/${prefix}_$2.sh"
    # candidates+=" $(_clupath ${directory}/${prefix}_$2.sh)"
    # candidates+=" $2"

    # local winner=

    # for candidate in $candidates; do
    #     if [ -f $candidate ]; then
    #         winner=$candidate
    #         break
    #     fi
    # done

    #_clureport debug "Requested ${what} <$2> on ${CLUSTER_UTILS_HOST}. Found: ${winner}. Candidates were: ${candidates}"

    echo "$(_clupath ${directory}/${prefix}_$2.sh)"
}

_cluparseget(){
    directory=
    prefix=
    case $1 in
        runner)
            directory=scripts/runners
            userdirectory="$CLUSTER_UTILS_USERSCRIPTS"/runners
            prefix=run
        ;;
        env_loader)
            directory=scripts/env_loaders
            userdirectory="$CLUSTER_UTILS_USERSCRIPTS"/env_loaders
            prefix=load
        ;;
    esac
}

_clureport(){
    :
    #echo CLUSTER-UTILS: "$@"
}

_clupyoptions(){
    echo "${CLUSTER_UTILS_PYTHON} python3 python"
}

_clupycomplete(){
    local bin_dir
    local py_bin
    local argcomplete_bin

    for possiblepy in $(_clupyoptions); do
        py_bin="$(which "${possiblepy}" 2>/dev/null)"
        bin_dir="$(dirname "${py_bin}")"
        argcomplete_bin="${bin_dir}/register-python-argcomplete"
        if [ -x "${argcomplete_bin}" ]; then
            eval "$("${argcomplete_bin}" clu)"
        fi
    done

}

clucd(){
    cd "${CLUSTER_UTILS_MOUNTS}/$1"
}


