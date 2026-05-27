#Created by S. Rahimi on 5 May 2025
#to iteravely update the namelists
#and submissions scripts based on dates

## start_year                          = 1940,
## start_month                         = 08,

import glob, os

period = 1

if period == 1:
	start_month, end_month = '08', '12'
if period == 2:
	start_month, end_month = '12', '04'
if period == 3:
	start_month, end_month = '04', '08'


dir_here = '/glade/derecho/scratch/srahimi/conus/era5/'
dir_src = f'{dir_here}/src'

dirs = sorted(glob.glob('[1-2]*'))
print (dirs,period)

for idir in dirs:

	fold = open(f'{dir_src}/namelist.input_REAL','r')
	lines_old = fold.readlines()
	os.chdir(idir)
	fnew = open(f'namelist.input','w')

	if period == 1:
		start_year, end_year = int(idir), int(idir)
		print (start_year)
	if period == 2:
		start_year, end_year = int(idir), int(idir)+1
	if period == 3:
		start_year, end_year = int(idir)+1, int(idir)+1

	starty_str = " start_year                          = %s\n" %(start_year)
	endy_str = " end_year                            = %s\n" %(end_year)

	startm_str = " start_month                          = %s\n" %(start_month)
	endm_str = " end_month                          = %s\n" %(end_month)

	#Copy parameters to new namelist
	for ii in lines_old:
                        if not ii.startswith(" start_year") and \
				not ii.startswith(" end_year") and \
				not ii.startswith(" start_month") and \
				not ii.startswith(" end_month"):
                                fnew.writelines(ii)
                        if ii.startswith(" start_year"):
                                fnew.writelines(starty_str)
                        if ii.startswith(" end_year"):
                                fnew.writelines(endy_str)
                        if ii.startswith(" start_month"):
                                fnew.writelines(startm_str)
                        if ii.startswith(" end_month"):
                                fnew.writelines(endm_str)

	fold.close()
	fnew.close()


	print (idir,start_year,start_year)

	os.chdir('../')
