import os
import subprocess

input_gpkg = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\Saule Union\solar_overlay_FASTEST_clean.gpkg"
output_mbtiles = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\Saule Union\solar_overlay_FASTEST_clean.mbtiles"

# 🟢 Te pielāgo savu QGIS instalācijas versiju un ceļu
qgis_path = r"C:\Program Files\QGIS 3.40.7"

# ✅ Pievienojam visus vajadzīgos ceļus
os.environ["PATH"] += (
    fr";{qgis_path}\bin"
    fr";{qgis_path}\apps\gdal-plugins"
    fr";{qgis_path}\apps\gdal38\bin"
    fr";{qgis_path}\apps\Qt5\bin"
)
os.environ["GDAL_DATA"] = fr"{qgis_path}\share\gdal"
os.environ["PROJ_LIB"] = fr"{qgis_path}\share\proj"

# 🧩 GDAL komanda
cmd = [
    "gdal_translate",
    "-of", "MBTILES",
    "-co", "TILE_FORMAT=PNG",
    input_gpkg,
    output_mbtiles
]

print("🚀 Konvertēju uz MBTiles...")
subprocess.run(cmd)
print(f"✅ Gatavs: {output_mbtiles}")
