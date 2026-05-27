import os

# Base path where the directories are located
base_path = '/glade/derecho/scratch/srahimi/conus/era5/'

# Loop through the years
for year in range(1980, 1990):
    dir_name = f"WPS_{year}"
    file_path = os.path.join(base_path, dir_name, "metgrid.sh")
    
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Replace the string
        new_content = content.replace("WYOM0169", "WYOM0200")
        
        # Write the new content back to the file
        with open(file_path, 'w') as file:
            file.write(new_content)
        
        print(f"Updated {file_path}")
    except FileNotFoundError:
        print(f"{file_path} not found. Skipping.")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
