import json

def create_zip_js_file():
    input_path = 'Auto Contacting/frontend/2024_Gaz_zcta_national.txt'
    output_path = 'Auto Contacting/frontend/zip_coordinates.js'
    
    zip_coords = {}
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            header = f.readline().strip().split('\t')
            header = [h.strip() for h in header]
            
            try:
                zip_col_index = header.index('GEOID')
                lat_col_index = header.index('INTPTLAT')
                lon_col_index = header.index('INTPTLONG')
            except ValueError as e:
                print(f"Error: Missing required column in header - {e}")
                return

            for line in f:
                parts = line.strip().split('\t')
                if len(parts) > max(zip_col_index, lat_col_index, lon_col_index):
                    zip_code = parts[zip_col_index].strip()
                    try:
                        lat = float(parts[lat_col_index].strip())
                        lon = float(parts[lon_col_index].strip())
                        if len(zip_code) == 5 and zip_code.isdigit():
                            zip_coords[zip_code] = {'lat': lat, 'lon': lon}
                    except (ValueError, IndexError):
                        continue

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('const zipCoordinates = ')
            json.dump(zip_coords, f)
            f.write(';')
            
        print(f"Successfully created {output_path} with {len(zip_coords)} zip codes.")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    create_zip_js_file()
