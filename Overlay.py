import geopandas as gpd
import os
import time

# ====== CEĻI ======
input_folder = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\Layers"
output_file = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\Saule_overlay_fast.gpkg"

# ====== KRĀSU NOTEIKUMI (visi lowercase + bez atstarpēm) ======
layer_colors = {
    "csp_blivi_apdzivotas_teritorijas_optimized_dissolved.gpkg": "green",
    "vvd_atkritumu_poligoni_optimized_dissolved.gpkg": "green",
    "vvd_piesarnotas_vietas_optimized_dissolved.gpkg": "yellow",
    "vvd_potenciali_piesarnotas_vietas_optimized_dissolved.gpkg": "yellow",
    "dap_iadt_ainavas_optimized_dissolved.gpkg": "yellow",
    "dap_iadt_optimized_dissolved.gpkg": "red",
    "dap_mikroliegumi_un_buferzonas_optimized_dissolved.gpkg": "red",
    "dap_potencialas_natura_2000_teritorijas_optimized_dissolved.gpkg": "orange",
    "dap_ipasi_aizsargajamie_biotopi_optimized_dissolved.gpkg": "orange",
    "dap_aizsargajamie_koki_optimized_dissolved.gpkg": "yellow",
    "dap_iadt_dabas_pieminekli_optimized_dissolved.gpkg": "red",
    "dap_sugu_atradnes_optimized_dissolved.gpkg": "yellow",
    "dap_nacionalas_ainavu_telpas_optimized_dissolved.gpkg": "orange",
    "vmd_mezi_optimizeti.gpkg": "yellow"
}

# ====== SĀKUMS ======
print(f"\n🌞 SĀKAM ĀTRĀ SAULE OVERLAY PROCESU (bez union) ...\n")

os.makedirs(os.path.dirname(output_file), exist_ok=True)
files = [f for f in os.listdir(input_folder) if f.endswith(".gpkg")]
all_layers = []

for i, file in enumerate(files, start=1):
    path = os.path.join(input_folder, file)
    key = file.lower().replace(" ", "_")
    color = layer_colors.get(key, "grey")

    start = time.time()
    print(f"➡️ [{i}/{len(files)}] Ielādē: {file} ({color})")

    try:
        gdf = gpd.read_file(path)

        # Pārprojektē, ja nepieciešams
        gdf = gdf.to_crs("EPSG:3059")

        # Saglabā metadatus
        gdf["color"] = color
        gdf["source"] = file

        # Tikai mežiem un biotopiem simplify (mazāk sver)
        if "biotop" in file.lower() or "mez" in file.lower():
            print("   🔹 Simplify ģeometrijas (30 m tolerance)...")
            gdf["geometry"] = gdf["geometry"].simplify(30, preserve_topology=True)

        # Labo ģeometrijas
        gdf["geometry"] = gdf["geometry"].buffer(0)

        all_layers.append(gdf)

        elapsed = round(time.time() - start, 2)
        size_mb = round(os.path.getsize(path) / (1024 * 1024), 1)
        print(f"   📊 {len(gdf)} elementi, {size_mb} MB, {elapsed} sek.\n")

    except Exception as e:
        print(f"⚠️ Kļūda ar {file}: {e}\n")

# ====== APVIENO VISUS (bez union) ======
if all_layers:
    print("🔄 Apvieno visus slāņus ar concat (bez ģeometrijas sadalīšanas)...")
    final = gpd.GeoDataFrame(pd.concat(all_layers, ignore_index=True), crs="EPSG:3059")

    # Saglabā rezultātu
    print("💾 Saglabā rezultātu...")
    final.to_file(output_file, driver="GPKG")

    size_mb = round(os.path.getsize(output_file) / (1024 * 1024), 1)
    print(f"\n🎯 PABEIGTS! Saglabāts: {output_file} ({size_mb} MB)\n")
else:
    print("\n⚠️ Netika atrasts neviens derīgs slānis apvienošanai.\n")
