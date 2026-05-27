#Created on 29 May 2024 by S. Rahimi
#to sybolically link met_em files within
#08* subdirectories

import os
import glob

met_em_path = '/glade/derecho/scratch/srahimi/conus/era5/met_em_files/'

dirs = sorted(glob.glob('[1-2]*'))

for idir in dirs:

	os.chdir(idir)

	year = int(idir)
	print (year)

	directive = 'ln -sf %s/met_em.d01.%s* ./' %(met_em_path,year)	
	os.system(directive)

	directive = 'ln -sf %s/met_em.d01.%s* ./' %(met_em_path,year+1)
	os.system(directive)
	
	os.chdir('../')
