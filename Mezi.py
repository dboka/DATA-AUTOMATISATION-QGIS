import os
import time
import geopandas as gpd
import pandas as pd  # <-- Šis bija pazudis!

# ====== IESTATĪJUMI ======
input_folder = r"\\fs02\PD\KMN\_KLIMATS\KEM\Enerģētika\VMD"  # <- mape ar apakšmapēm (Austrumi, Dienvidi, utt.)
output_folder = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\Gatavie Shapefaili LKS 92\26. VMD Inventarizeto mezu zeme"
output_file = os.path.join(output_folder, "VMD_mezi_optimizeti.gpkg")

tolerance = 3
target_crs = "EPSG:4326"  # vai nomaini uz "EPSG:3059", ja vajag LKS-92

# ====== SAGATAVOŠANA ======
os.makedirs(output_folder, exist_ok=True)
all_files = []

# Atrod visus shapefailus (arī apakšmapēs)
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.lower().endswith(".shp"):
            all_files.append(os.path.join(root, file))

total_files = len(all_files)
print(f"\n🌲 Atrasti {total_files} shapefaili apstrādei no {input_folder}\n")

# ====== FUNKCIJA ======
def process_shapefile(filepath, index):
    try:
        start_time = time.time()
        filename = os.path.basename(filepath)
        print(f"➡️ [{index}/{total_files}] Apstrādā: {filename}")

        # Ielasa shapefailu
        gdf = gpd.read_file(filepath)

        # Noņem kolonnu 'fid', ja tā eksistē
        if "fid" in gdf.columns:
            gdf = gdf.drop(columns=["fid"])

        # Salabo ģeometrijas
        gdf["geometry"] = gdf["geometry"].buffer(0)

        # Vienkāršo ģeometrijas
        gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)

        # Pārprojektē
        gdf = gdf.to_crs(target_crs)

        elapsed = round(time.time() - start_time, 2)
        print(f"✅ [{index}/{total_files}] Gatavs: {filename} ({elapsed} sek.)\n")

        return gdf

    except Exception as e:
        print(f"⚠️ Kļūda ar {filepath}: {e}\n")
        return None


# ====== APSTRĀDE ======
processed_layers = []
for i, file in enumerate(all_files, start=1):
    gdf = process_shapefile(file, i)
    if gdf is not None and not gdf.empty:
        processed_layers.append(gdf)
# ====== APVIENOŠANA ======
if processed_layers:
    print("🔄 Apvieno visus shapefailus vienā GeoDataFrame...")
    combined_gdf = gpd.GeoDataFrame(pd.concat(processed_layers, ignore_index=True), crs=target_crs)

    print("🧩 Pārbauda un labo ģeometrijas pirms Dissolve...")
    combined_gdf["geometry"] = combined_gdf["geometry"].buffer(0)

    # Izmet nederīgās ģeometrijas, ja tās joprojām paliek
    combined_gdf = combined_gdf[combined_gdf.is_valid]

    print("🧩 Veic galīgo Dissolve (apvienošanu)...")
    try:
        combined_gdf = combined_gdf.dissolve()
    except Exception as e:
        print(f"⚠️ Dissolve neizdevās: {e}")
        print("➡️ Izmanto drošo režīmu ar shapely.unary_union ...")
        from shapely.ops import unary_union
        merged_geom = unary_union(combined_gdf.geometry)
        combined_gdf = gpd.GeoDataFrame(geometry=[merged_geom], crs=target_crs)

    print("💾 Saglabā rezultātu GeoPackage failā...")
    combined_gdf.to_file(output_file, driver="GPKG")

    print(f"\n🎯 DARBS PABEIGTS — Saglabāts: {output_file}\n")
else:
    print("\n⚠️ Netika atrasts neviens derīgs slānis apvienošanai.\n")
