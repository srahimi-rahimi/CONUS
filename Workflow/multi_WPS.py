#Created by S. Rahimi on 21 Feb. 2024
#to run multiple metgrid jobs on a single
#Derecho node

'''#!/bin/bash
#PBS -N <job name>
#PBS -l select=1:ncpus=128:mpiprocs=128:ompthreads=1
#PBS -l walltime=05:00:00
#PBS -A WYOM0136
#PBS -j oe
#PBS -q main

( cd WPS_01; mpiexec -n 32 --cpu-bind list:0-31   ./metgrid.exe  > metgrid.out; mv met_em* ./met_em_files ) &'''

#Uses template_sh

#Submits 4 scripts years  to 1 Derecho node

#Creates a cmdfile for each batch of jobs

#Changes directories in each job

import numpy as np
import os
import glob

exp_name = 'WPS'

bogey = 'xxx'

run = True

cores = 32

dirs = sorted(glob.glob('WPS_*'))

inc = 4 #How many submissions per node

#Date range
year1, year2 = 1990, 2025

for count_year, year_main in enumerate(np.arange(year1, year2+1,inc)):

	#Open template_sh
	fold = open('template_sh','r')
	lines_old = fold.readlines()

	#Onde cmd file per increment
	sh_file = 'batch%s%s.sh' %(year_main,year_main+inc-1)
	fsh = open(sh_file,"w")

	for iline in lines_old:

		if bogey in iline:
			fsh.writelines('#PBS -N %s\n' %(year_main))
		else:
			fsh.writelines(iline)

	fsh.writelines(' \n')
	for count_dir in range( 0, inc ):

		#print (count_dir)
		iyear = year_main + count_dir

		#navigate to each of these directories
		#to run a MPI job

		#Write to sh file
		#cd WPS_01; mpiexec -n 32 --cpu-bind list:0-31   ./metgrid.exe  > metgrid.out; mv met_em* ./met_em_files ) &
		fsh.writelines('( cd %s_%s ; mpiexec -n 32 --cpu-bind list:%s-%s ./metgrid.exe  > metgrid.out ; mv met_em* ../met_em_files ) &\n' %(exp_name,iyear,count_dir*cores,(count_dir+1)*cores-1))

	fsh.writelines('wait')

	fsh.close()


	#Submit
	print (year_main)
	if run == True:
		os.system('qsub %s' %(sh_file))
