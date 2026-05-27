#Created by S. Rahimi on 21 Feb. 2024
#to parralellize WPS

#Updates the namelist.wps and submission
#template

#Doe not submit to queue -- only launch_cf
#does that (see multi.py)

import subprocess as sb
import os
import shutil

only_namelist = True

#WPS located in
dir = "/glade/derecho/scratch/srahimi/conus/era5/"

#binaries located in
binary_dir = '/glade/derecho/scratch/srahimi/ERA5/Qbinaries/binary_files/'

cur_dir = dir

#How long are your chunks?
parallel_increment = 1

year1, year2 = 1990, 2025

bogey = 'xxx'

for count, iyear in enumerate(range(year1,year2,parallel_increment)):

 os.chdir(dir)

 #Create directories

 dir_new = dir+"WPS_%s" %("{0:0=2d}".format(iyear))
 directive = "cp -R %s%s %s" %(dir,"WPS",dir_new)
 print (dir_new)

 if not only_namelist:
     os.system(directive)

 os.chdir(dir_new)

 #Link binaries
 if not only_namelist:
     for iiyear in range(iyear,iyear+parallel_increment+1):
      directive = "ln -sf %sFILE:%s* ./" %(binary_dir,iiyear)
      os.system(directive)

 #Update the namelist.wps file
 file_orig = cur_dir+"template_WPS"

 fo = open(file_orig,"r")
 lines_old = fo.readlines()

 new_file = "namelist.wps"
 fnew_namelist = open(dir_new+"/"+new_file,"w")

 #start_date = '2000-07-01_00:00:00',
 startd_str = " start_date  = '%s-03-15_00:00:00',\n" %(iyear+1)
 endd_str = " end_date  = '%s-08-01_00:00:00',\n" %(iyear+1)

 for jj in lines_old:
     if not jj.startswith(" start_date ") and not jj.startswith(" end_date "):
      fnew_namelist.writelines(jj)
     if jj.startswith(" start_date "):
      fnew_namelist.writelines(startd_str)
     if jj.startswith(" end_date "):
      fnew_namelist.writelines(endd_str)

 fnew_namelist.close()
 fo.close()

 #Return to the parent codes directory
 os.chdir(cur_dir)
