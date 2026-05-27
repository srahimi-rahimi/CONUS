import os

for iyear in range(1981,2020):

	file1 = '/glade/derecho/scratch/srahimi/wus/cesm_1031/WPS/metgrid/METGRID.TBL.ARW'
	file2 = 'WPS_%s/metgrid/METGRID.TBL.ARW' %(iyear) 
	directive = 'cp -p %s %s' %(file1, file2)
	os.system(directive)
	print (directive)
