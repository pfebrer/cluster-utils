APPS_ROOT=/data/apps
export LD_LIBRARY_PATH=/opt/mellanox/mxm/lib
export LIBRARY_PATH=/opt/mellanox/mxm/lib
export CPATH=/opt/mellanox/mxm/include
source ${APPS_ROOT}/intel/composer_xe_2013.3.163/bin/compilervars.sh intel64
source ${APPS_ROOT}/intel/composer_xe_2013_sp1.2.144/bin/compilervars.sh intel64
source ${APPS_ROOT}/intel/composer_xe_2013_sp1.2.144/mkl/bin/mklvars.sh intel64
export PATH=/data/apps/ompi/4.0.1-intel13/bin/:$PATH
