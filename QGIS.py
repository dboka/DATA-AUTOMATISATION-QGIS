import os
import geopandas as gpd
import time

# ====== IESTATĪJUMI ======
input_folder = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\Gatavie Shapefaili LKS 92\33. AM Radars GREEN LEVEL no 2028" # <- nomaini uz savu mapi
output_folder = os.path.join(input_folder, "Optimizetie_shapefaili")
tolerance = 1 # vienkāršošanas precizitāte metros
target_crs = "EPSG:4326"  # tīmeklim piemērota koordinātu sistēma

os.makedirs(output_folder, exist_ok=True)

# Iegūst sarakstu ar visiem shapefailiem
files = [f for f in os.listdir(input_folder) if f.lower().endswith(".shp")]
total_files = len(files)

print(f"\n🚀 Sākam apstrādi ({total_files} shapefaili kopā)\n")

# ====== FUNKCIJA ======
def optimize_shapefile(filepath, index):
    try:
        start_time = time.time()
        filename = os.path.basename(filepath)
        print(f"➡️ [{index}/{total_files}] Apstrādā: {filename}")

        # Ielasa datus
        gdf = gpd.read_file(filepath)

        # Ja eksistē kolonna 'fid', noņem to
        if "fid" in gdf.columns:
            gdf = gdf.drop(columns=["fid"])

        # Salabo ģeometrijas (novērš topoloģiskās kļūdas)
        gdf["geometry"] = gdf["geometry"].buffer(0)

        # Vienkāršo ģeometrijas
        gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)

        # Apvieno visus poligonus (dissolve)
        gdf = gdf.dissolve()

        # Pārprojektē uz WGS84
        gdf = gdf.to_crs(target_crs)

        # Saglabā rezultātu GeoPackage formātā
        out_name = os.path.splitext(filename)[0] + "_optimized_dissolved.gpkg"
        out_path = os.path.join(output_folder, out_name)
        gdf.to_file(out_path, driver="GPKG")

        elapsed = round(time.time() - start_time, 2)
        print(f"✅ [{index}/{total_files}] Gatavs: {filename} ({elapsed} sek.)\n")

    except Exception as e:
        print(f"⚠️ Kļūda apstrādājot {filename}: {e}\n")

# ====== GALVENAIS CIKLS ======
for i, file in enumerate(files, start=1):
    full_path = os.path.join(input_folder, file)
    optimize_shapefile(full_path, i)

print(f"\n🎯 DARBS PABEIGTS — {total_files} shapefaili saglabāti mapē “Optimizetie_shapefaili”.\n")
