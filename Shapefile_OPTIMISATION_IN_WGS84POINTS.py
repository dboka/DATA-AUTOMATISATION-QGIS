import geopandas as gpd
import os
import time

# ====== CEĻI ======
input_path = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\Gatavie Shapefaili LKS 92\18. DAP Sugu noverojumi\DAP sugu noverojumi.shp"
output_folder = os.path.join(os.path.dirname(input_path), "Merged_Polygon_Final")
os.makedirs(output_folder, exist_ok=True)

simplify_tolerance = 0.5   # ļoti maza vienkāršošana, saglabā apļus
default_crs = "EPSG:3059"  # LKS-92
target_crs = "EPSG:4326"   # WGS84 tīmeklim

# ====== APSTRĀDE ======
start = time.time()
filename = os.path.basename(input_path)
print(f"➡️ Apstrāde sākta: {filename}")

try:
    # 1️⃣ Ielasa failu
    gdf = gpd.read_file(input_path)
    if gdf.crs is None:
        gdf.set_crs(default_crs, inplace=True)

    # 2️⃣ Izmet nederīgos un tukšos
    gdf = gdf[gdf.geometry.notnull() & gdf.is_valid].copy()

    # 3️⃣ (Izvēles) neliela vienkāršošana, tikai lai fails būtu mazāks
    print(f"🧹 Mazliet vienkāršo ģeometrijas (tolerance={simplify_tolerance} m)...")
    gdf["geometry"] = gdf["geometry"].simplify(simplify_tolerance, preserve_topology=True)

    # 4️⃣ Apvieno visus vienā (dissolve)
    print("🧩 Apvieno visus 10 m apļus vienā kopīgā laukā...")
    merged = gdf.dissolve()

    # 5️⃣ Pārprojektē uz WGS84
    print("🌍 Pārprojektē uz WGS84 (EPSG:4326)...")
    merged = merged.to_crs(target_crs)

    # 6️⃣ Saglabā kā GeoPackage
    out_path = os.path.join(output_folder, os.path.splitext(filename)[0] + "_merged_apli.gpkg")
    merged.to_file(out_path, driver="GPKG")

    elapsed = round(time.time() - start, 2)
    orig_size = os.path.getsize(input_path) / (1024 * 1024)
    new_size = os.path.getsize(out_path) / (1024 * 1024)
    reduction = (1 - new_size / orig_size) * 100

    print(f"✅ Saglabāts: {out_path}")
    print(f"📉 Izmērs: {orig_size:.1f} MB → {new_size:.1f} MB ({reduction:.1f}% mazāks)")
    print(f"⏱️ Laiks: {elapsed} sekundes\n")

except Exception as e:
    print(f"❌ Kļūda: {e}")
