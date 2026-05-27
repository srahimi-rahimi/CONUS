import os

for iyear in range(1940,2025):

	directive = 'rm met_em_files/met_em.d01.%s*' %(iyear)
	os.system(directive)
	print (directive)
