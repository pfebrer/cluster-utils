#!/bin/sh
#PBS -q main
#PBS -j oe
#PBS -l walltime=72:00:00
#PBS -l select=48:ncpus=1:mpiprocs=1:mem=30000mb
#PBS -W group_list=2019089_HPCCOM_ICN2
#PBS -r y

source $ENV_LOADER

NSLOTS=`wc -l < $PBS_NODEFILE`

echo "------------------ Job Info --------------------"
echo "jobid : $PBS_JOBID"
echo "jobname : $PBS_JOBNAME"
echo "submit dir : $PBS_O_WORKDIR"
echo "exec dir : $PBS_JOBDIR"
echo "queue : $PBS_O_QUEUE"
echo "user : $PBS_O_LOGNAME"
echo "threads : $OMP_NUM_THREADS"
echo "Path_O: $PBS_O_PATH"
echo "NODES: $NSLOTS"
echo "Cores: $(($NSLOTS * $OMP_NUM_THREADS))"
CORES=$(($NSLOTS * $OMP_NUM_THREADS))

cat $PBS_NODEFILE
echo "------------------ Work dir --------------------"
echo $PBS_O_WORKDIR
cd ${PBS_O_WORKDIR}

# Define the scratch directory
#
SCR=/SCRATCH/icn2/2019089_HPCCOM_ICN2/$PBS_JOBNAME-$PBS_JOBID

mkdir $SCR
# Copy relevant data files only to the master node's scratch.
# In SIESTA only the master node should be allowed to do I/O.
# Your mileage might vary with other codes.
#
cp * $SCR
#
#
echo "$SCR" >> WHERE_TO_FIND_FILES

cd $SCR

mpirun -np $CORES $SIESTA < $SYSTEM.fdf > $SYSTEM.out

mv $SCR/* $PBS_O_WORKDIR
rmdir $SCR
