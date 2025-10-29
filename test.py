import subprocess
import geopandas as gpd
import os
import time

# ====== IESTATĪJUMI ======
input_gpkg = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\READY GPKG\DAP Ipasi aizsargajamie biotopi_optimized_dissolved.gpkg"
intermediate_geojson = os.path.splitext(input_gpkg)[0] + "_TEMP.geojson"
output_geojson = os.path.splitext(input_gpkg)[0] + "_FAST.geojson"

simplify_percent = "2%"  # <- vienkāršošanas intensitāte
target_crs = "EPSG:4326"

# ====== SOLIS 1: KONVERTĒ UZ GEOJSON ======
start = time.time()
print(f"\n🌍 Konvertē: {os.path.basename(input_gpkg)} → GeoJSON ...")

gdf = gpd.read_file(input_gpkg)
if gdf.crs is None:
    gdf.set_crs(epsg=3059, inplace=True)
gdf = gdf.to_crs(target_crs)
gdf.to_file(intermediate_geojson, driver="GeoJSON")

size_mb = os.path.getsize(intermediate_geojson) / (1024 * 1024)
print(f"✅ Izveidots GeoJSON ({size_mb:.2f} MB)")

# ====== SOLIS 2: VIENKĀRŠO AR MAPSHAPER ======
print(f"\n⚙️ Vienkāršo ar mapshaper ({simplify_percent}) ...")
cmd = [
    "mapshaper",
    intermediate_geojson,
    "-simplify", simplify_percent,
    "keep-shapes",
    "-o", "format=geojson", output_geojson
]

try:
    subprocess.run(cmd, check=True)
    print(f"✅ Saglabāts kā: {output_geojson}")
except subprocess.CalledProcessError as e:
    print(f"❌ Kļūda vienkāršošanā: {e}")

# ====== PABEIGUMS ======
elapsed = round(time.time() - start, 2)
print(f"\n🎯 Pabeigts! Kopējais ilgums: {elapsed} sek.\n")
