import geopandas as gpd
import os
import time

# ====== IESTATĪJUMI ======
input_folder = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\GEOPACKAGE"
output_folder = os.path.join(input_folder, "GEOJSON_READY")

os.makedirs(output_folder, exist_ok=True)

target_crs = "EPSG:4326"  # tīmekļa (WGS84) koordinātu sistēma
max_size_mb = 10           # slieksnis: konvertē tikai failus, kas mazāki par 10 MB

# ====== PALĪGFUNKCIJA ======
def get_file_size_mb(path):
    """Atgriež faila izmēru MB."""
    return os.path.getsize(path) / (1024 * 1024)

# ====== GALVENAIS ======
files = [f for f in os.listdir(input_folder) if f.lower().endswith(".gpkg")]
print(f"\n📦 Atrasti {len(files)} GPKG faili mapē.\n")

for i, file in enumerate(files, start=1):
    start = time.time()
    input_path = os.path.join(input_folder, file)
    file_size_mb = get_file_size_mb(input_path)
    output_path = os.path.join(output_folder, os.path.splitext(file)[0] + ".geojson")

    if file_size_mb <= max_size_mb:
        try:
            print(f"➡️ [{i}/{len(files)}] {file} ({file_size_mb:.2f} MB) → Konvertē uz GeoJSON...")

            gdf = gpd.read_file(input_path)

            # Ja CRS nav definēts, uzstāda uz LKS-92
            if gdf.crs is None:
                gdf.set_crs(epsg=3059, inplace=True)

            # Pārprojektē uz WGS84
            gdf = gdf.to_crs(target_crs)

            # Saglabā GeoJSON
            gdf.to_file(output_path, driver="GeoJSON")

            elapsed = round(time.time() - start, 2)
            print(f"✅ Saglabāts: {os.path.basename(output_path)} ({elapsed} sek.)\n")

        except Exception as e:
            print(f"⚠️ Kļūda ar {file}: {e}\n")

    else:
        print(f"⏭️ [{i}/{len(files)}] {file} ({file_size_mb:.2f} MB) pārsniedz 10 MB — izlaižam šoreiz.\n")

print("\n🎯 Pabeigts! Mazie (<10 MB) GPKG faili pārveidoti uz GeoJSON mapē 'GEOJSON_READY_SIMPLE'.\n")
