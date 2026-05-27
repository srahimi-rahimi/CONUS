import os
import subprocess as sb
import numpy as np
import string

dir_here = '/glade/derecho/scratch/srahimi/conus/era5/'
dir_src = f'{dir_here}/src'

sub_directories = list(string.ascii_uppercase[:9])
print (sub_directories)

StartingYearsOfChunks = np.arange(1940,2021,10)

print (len(sub_directories))
print (len(StartingYearsOfChunks))
istart = 0

for count_directory, idirectory in enumerate(sub_directories):

	print (idirectory)

	directive = 'mkdir %s' %(idirectory)
	os.system(directive)

	os.chdir(idirectory)

	directive = 'mkdir real wrf'
	os.system(directive)

	#Now go into these directories and run setup.py, creating
	#subdirectories where needed

	#Real directory
	os.chdir('real')

	#Link the control files
	directive = 'cp -p %s/link_METEM.py ./' %(dir_src)
	os.system(directive)

	directive = 'cp -p %s/template_REAL ./' %(dir_src)
	os.system(directive)

	directive = 'cp -p %s/multi_REAL.py ./' %(dir_src)
	os.system(directive)

	directive = 'cp -p %s/name_REAL.py ./' %(dir_src)
	os.system(directive)

	for iyear in range(istart,10):

		directive = 'mkdir %s' %(iyear+StartingYearsOfChunks[count_directory])
		os.system(directive)

		os.chdir('%s' %(iyear+StartingYearsOfChunks[count_directory]) )

		directive = 'cp -p %s/setup.sh ./' %(dir_src)
		os.system(directive)

		directive = 'cp -p %s/real.sh ./' %(dir_src)
		os.system(directive)

		directive = 'bash setup.sh'
		os.system(directive)

		directive = 'mkdir real1 real2 real3'
		os.system(directive)

		os.chdir('../')

	istart = 0

	#WRF
	os.chdir(dir_here+'/'+idirectory)
	os.chdir('wrf')

	directive = 'mkdir 6hourly hourly spinup'
	os.system(directive)

	directive = 'cp -p %s/setup.sh ./' %(dir_src)
	os.system(directive)

	directive = 'bash setup.sh'
	os.system(directive)

	directive = 'cp -p %s/namelist.input_WRF ./namelist.input'  %(dir_src)
	os.system(directive)

	directive = 'cp -p %s/wrf.sh ./' %(dir_src)
	os.system(directive)

	os.chdir(dir_here)
	#break
