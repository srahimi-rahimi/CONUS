#!/bin/bash
#PBS -N G
#PBS -A WYOM0200
#PBS -q main
#PBS -l walltime=12:00:00
#PBS -l job_priority=premium
#PBS -l select=18:ncpus=128:mpiprocs=128
#PBS -o log.oe

export WRF_CHEM=0
export EM_CORE=1
export WRF_EM_CORE=1
export WRFIO_NCD_LARGE_FILE_SUPPORT=1
export WRF_KPP=0
export YACC="/glade/u/apps/gust/23.04/opt/bin/yacc -d"
export FLEX_LIB_DIR="/glade/u/apps/gust/23.04/opt/lib"

module --force purge
module load ncarenv/23.06
module load intel-classic/2023.0.0
module load hdf5/1.12.2
module load cray-mpich/8.1.25
module load ncview/2.1.8
module load craype/2.7.20
module load netcdf/4.9.2
module load ncarcompilers/1.0.0

#mpiexec ./wrf.exe

#: <<'BLOCK'
ml conda
conda activate dynamics
rm wrf*d01
python update_namelist.py ./namelist.input
python set_restart_interval.py ./
python link.py ./
conda deactivate
module unload conda

if mpiexec ./wrf.exe; then
  echo "wrf.exe a success, auto-restarting...."
  qsub wrf.sh #auto-restart

else
  echo "wrf.exe failed (exit code $?); Exitting"
  exit 1
fi
#BLOCK
