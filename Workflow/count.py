def replace_dates_in_file(filename, new_start_date_line, new_end_date_line):
	with open(filename, 'r') as file:
		lines = file.readlines()

	with open(filename, 'w') as file:
		for line in lines:
			if line.strip().startswith('start_date'):
				file.write(new_start_date_line + '\n')
			elif line.strip().startswith('end_date'):
				file.write(new_end_date_line + '\n')
			else:
				file.write(line)

import glob, os

#Flag for recreating met_em files
#Only regenerates the smallest file
#in a year
regenerate = True

dir_METEM = '/glade/derecho/scratch/srahimi/conus/era5/met_em_files/'

for iyear in range(1980,1990):

	files = glob.glob(f'./*{iyear}*')

	if len(files) != 1464 and len(files) != 1460:
		print (len(files), iyear, 'PROBLEM')

	#For cross-checks
	#directive = f'ls -lS *{iyear}*| tail -n 5'
	#os.system(directive)

	# Sort files by size, descending
	files_sorted = sorted(files, key=lambda f: os.path.getsize(f), reverse=True)

	# Take the last 5 from the list (i.e., smallest among the top files)
	top_5_files = files_sorted[-5:]

	# Get sizes of those files
	sizes = [os.path.getsize(f) for f in top_5_files]

	if len(sizes) < 2:
		print("Not enough files to compare.")
	else:
		largest = max(sizes)
		smallest = min(sizes)

	# Check if smallest is less than 90% of largest
	if smallest < 0.95 * largest:
		print("The smallest file is less than 90% the size of the largest.")
		print (smallest,largest,iyear)

		if regenerate == True:

			os.chdir(f'../WPS_{iyear}')
			print (top_5_files[-1])

			#  start_date  = '1941-04-01_00:00:00', '1941-04-01_00:00:00',
			#  end_date  = '1941-04-15_00:00:00', '1941-04-15_00:00:00',

			filename = 'namelist.wps'
			new_start_date_line = f" start_date  = '{top_5_files[-1].split('.')[3]}', '{top_5_files[-1].split('.')[3]}',"
			new_end_date_line = f" end_date  = '{top_5_files[-1].split('.')[3]}','{top_5_files[-1].split('.')[3]}',"

			replace_dates_in_file(filename, new_start_date_line, new_end_date_line)
			os.system('qsub metgrid.sh')
	else:
		continue

	os.chdir(dir_METEM)
