import os

for iyear in range(1990,2025):

	directive = 'mv WPS_%s/met_em* met_em_files' %(iyear)
	os.system(directive)
	print (directive)
