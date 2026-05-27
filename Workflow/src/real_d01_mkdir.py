import os

year1, year2 = 1995, 2019
for iyear in range(year1,year2+1):

	directive = 'mkdir 08%s' %(iyear)
	os.system(directive)
