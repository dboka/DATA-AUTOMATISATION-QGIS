import os
import geopandas as gpd
import time

# ====== IESTATĪJUMI ======
input_gpkg = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\Gatavie Shapefaili LKS 92\5. CSP blivi apdzivotas teritorijas (pilsetas)\Optimizētie Shapefaili\CSP_BAT_dati_pilsetas.gpkg" # <- norādi savu GeoPackage
layer_name = None  # ja zināms slāņa nosaukums, ieraksti te, piemēram "layer1"; ja None, tiks nolasīts pirmais
tolerance = 1      # vienkāršošanas precizitāte metros
target_crs = "EPSG:4326"

output_gpkg = os.path.splitext(input_gpkg)[0] + "_optimized.gpkg"

# ====== FUNKCIJA ======
def optimize_layer(input_gpkg, output_gpkg, layer_name=None):
    start_time = time.time()
    print(f"\n🚀 Sākam apstrādi failam: {os.path.basename(input_gpkg)}\n")

    try:
        # Nolasām GeoPackage (ja zināms slānis — norādi ar layer=layer_name)
        gdf = gpd.read_file(input_gpkg, layer=layer_name) if layer_name else gpd.read_file(input_gpkg)

        print(f"➡️ Ielasīts {len(gdf)} objektu no slāņa")

        # Noņem fid ja eksistē
        if "fid" in gdf.columns:
            gdf = gdf.drop(columns=["fid"])

        # Salabo ģeometrijas
        gdf["geometry"] = gdf["geometry"].buffer(0)

        # Vienkāršo ģeometrijas
        gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)

        # Apvieno (dissolve)
        gdf = gdf.dissolve()

        # Pārprojektē
        gdf = gdf.to_crs(target_crs)

        # Saglabā
        gdf.to_file(output_gpkg, driver="GPKG")

        elapsed = round(time.time() - start_time, 2)
        print(f"✅ Gatavs! Saglabāts kā: {output_gpkg} ({elapsed} sek.)\n")

    except Exception as e:
        print(f"⚠️ Kļūda apstrādājot failu: {e}\n")

# ====== IZPILDE ======
optimize_layer(input_gpkg, output_gpkg, layer_name)