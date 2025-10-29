import os
import subprocess
import geopandas as gpd
import gzip
import shutil
import time

# ====== IESTATĪJUMI ======
input_gpkg = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\READY GPKG\VMD_mezi_optimizeti.gpkg"
simplify_percent = "5%"   # Cik agresīvi vienkāršot: 10%, 5%, 2%, 1%

# ====== CEĻI ======
base_dir = os.path.dirname(input_gpkg)
basename = os.path.splitext(os.path.basename(input_gpkg))[0]
geojson_path = os.path.join(base_dir, f"{basename}.geojson")
simplified_path = os.path.join(base_dir, f"{basename}_FAST.geojson")
compressed_path = simplified_path + ".gz"

# ====== 1️⃣ KONVERTĒ NO GPKG UZ GEOJSON ======
start_time = time.time()
print(f"\n🌲 Konvertē: {basename}.gpkg → GeoJSON ...")
gdf = gpd.read_file(input_gpkg)
gdf.to_file(geojson_path, driver="GeoJSON")
size_geojson = round(os.path.getsize(geojson_path) / 1e6, 2)
print(f"✅ Izveidots GeoJSON ({size_geojson} MB)\n")

# ====== 2️⃣ VIENKĀRŠO AR MAPSHAPER ======
print(f"⚙️ Vienkāršo ar mapshaper ({simplify_percent}) ...")
cmd = [
    "mapshaper",
    geojson_path,
    "-simplify", simplify_percent,
    "keep-shapes",
    "-o", "format=geojson", simplified_path
]
subprocess.run(cmd, check=True)
size_simple = round(os.path.getsize(simplified_path) / 1e6, 2)
print(f"✅ Vienkāršots GeoJSON: {size_simple} MB\n")

# ====== 3️⃣ SASPIEŽ AR GZIP ======
print("🗜️ Saspaida ar gzip ...")
with open(simplified_path, "rb") as f_in:
    with gzip.open(compressed_path, "wb", compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)

size_compressed = round(os.path.getsize(compressed_path) / 1e6, 2)
print(f"✅ Saspiests: {compressed_path}")
print(f"📉 {size_simple} MB → {size_compressed} MB\n")

# ====== 4️⃣ IZDZĒŠ STARPPOSMA FAILUS ======
print("🧹 Tīra starpfailus ...")
for path in [geojson_path, simplified_path]:
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Dzēsts: {os.path.basename(path)}")

# ====== 5️⃣ KOPSAVILKUMS ======
elapsed = round(time.time() - start_time, 2)
print("\n🎯 DARBS PABEIGTS!")
print(f"Ievade: {os.path.basename(input_gpkg)}")
print(f"Rezultāts: {os.path.basename(compressed_path)}")
print(f"Gala izmērs: {size_compressed} MB")
print(f"Kopējais samazinājums: {round((1 - size_compressed / size_geojson) * 100, 2)}%")
print(f"⏱️ Kopējais ilgums: {elapsed} sek.\n")
