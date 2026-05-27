#Created by S. Rahimi on 29 May 2024
#to run multiple real.exe jobs on a single
#Derecho node

#FOR REAL.EXE - Updated CONUS workflow

'''#!/bin/bash
#PBS -N <job name>
#PBS -l select=1:ncpus=128:mpiprocs=128:ompthreads=1
#PBS -l walltime=05:00:00
#PBS -A WYOM0136
#PBS -j oe
#PBS -q main

( cd 1980; mpiexec -n 32 --cpu-bind list:0-31   ./real.exe  > real.out) &'''


#Uses template_REAL

#Submits 4 scripts years  to 1 Derecho node

#Creates a cmdfile for each batch of jobs

#Changes directories in each job

import numpy as np
import os
import glob

period = 1

bogey = 'xxx'

run = True

cores = 32

dirs = sorted(glob.glob('[1-2]*') )
print (dirs)

inc = 4 #How many submissions per node

#Date range
year1, year2 = 1980, 2020

for count_year, year_main in enumerate(np.arange(year1, year2+1,inc)):

	#Open template_*
	fold = open('template_REAL','r')
	lines_old = fold.readlines()

	#Onde cmd file per increment
	sh_file = 'batch_REAL_%s%s.sh' %(year_main,year_main+inc-1)
	fsh = open(sh_file,"w")

	for iline in lines_old:

		if bogey in iline:
			fsh.writelines('#PBS -N %s\n' %(year_main))
		else:
			fsh.writelines(iline)

	fsh.writelines(' \n')
	for count_dir in range( 0, inc ):

		print (count_dir)
		iyear = year_main + count_dir

		#navigate to each of these directories
		#to run a MPI job

		#Write to sh file
		fsh.writelines('( cd %s ; mpiexec -n 32 --cpu-bind list:%s-%s ./real.exe  > real.out ; mv wrf*d01 real%s ) &\n' %(iyear,count_dir*cores,(count_dir+1)*cores-1,period))

	fsh.writelines('wait')

	fsh.close()


	#Submit
	print (year_main)
	if run == True:
		os.system('qsub %s' %(sh_file))
