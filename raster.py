import os
import geopandas as gpd
import rasterio
from rasterio import features
import numpy as np

# ====== IESTATĪJUMI ======
input_folder = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\Layers"
output_raster = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\Saule_raster_overlay_10mversionlogic.tif"
output_legend = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\Saule_raster_legendversionlogic.csv"

pixel_size = 10
crs = "EPSG:3059"

# ====== FAILI UN KRĀSAS ======
file_colors = {
    "DAP Aizsargajamie koki_optimized_dissolved.gpkg": "yellow",
    "DAP IADT ainavas_optimized_dissolved.gpkg": "yellow",
    "DAP IADT dabas pieminekli_optimized_dissolved.gpkg": "red",
    "DAP Ipasi aizsargajamie biotopi_optimized_dissolved.gpkg": "orange",
    "DAP mikroliegumi un buferzonas_optimized_dissolved.gpkg": "red",
    "DAP Nacionalas ainavu telpas_optimized_dissolved.gpkg": "orange",
    "DAP potencialas natura 2000 teritorijas_optimized_dissolved.gpkg": "orange",
    "DAP Sugu atradnes_optimized_dissolved.gpkg": "yellow",
    "Īpaši aizsargājamas dabas teritorijas (zonējums nav vērts union)_optimized_dissolved.gpkg": "red",
    "VMD_mezi_optimizeti.gpkg": "yellow",
    "VVD Atkritumu poligoni_optimized_dissolved.gpkg": "green",
    "VVD Piesarnotas vietas_optimized_dissolved.gpkg": "yellow",
    "VVD Potenciali piesarnotas vietas_optimized_dissolved.gpkg": "yellow"
}

# ====== KRĀSU VĒRTĪBAS ======
color_values = {
    "green": 1,
    "yellow": 2,
    "orange": 3,
    "red": 4
}

# ====== KOMBINĀCIJAS NOTEIKUMI ======
def combine_colors(v1, v2):
    """Apvieno divas krāsu vērtības pēc noteikumiem."""
    if v1 == 0: return v2
    if v2 == 0: return v1

    # Sarkanajam ir visaugstākā prioritāte
    if v1 == 4 or v2 == 4:
        return 4

    # Divi oranžie -> sarkans
    if v1 == 3 and v2 == 3:
        return 4

    # Oranžs + dzeltens/zaļš -> oranžs
    if 3 in (v1, v2):
        return 3

    # Divi dzelteni -> oranžs
    if v1 == 2 and v2 == 2:
        return 3

    # Dzeltenais + zaļš -> dzeltenais
    if 2 in (v1, v2):
        return 2

    # Pretējā gadījumā saglabā lielāko
    return max(v1, v2)


# ====== ROBEŽU NOTEIKŠANA ======
bounds = []
for file in file_colors:
    path = os.path.join(input_folder, file)
    if os.path.exists(path):
        gdf = gpd.read_file(path).to_crs(crs)
        bounds.append(gdf.total_bounds)

if not bounds:
    raise Exception("❌ Nav atrasts neviens fails ar datiem!")

minx = min(b[0] for b in bounds)
miny = min(b[1] for b in bounds)
maxx = max(b[2] for b in bounds)
maxy = max(b[3] for b in bounds)

width = int((maxx - minx) / pixel_size)
height = int((maxy - miny) / pixel_size)
transform = rasterio.transform.from_origin(minx, maxy, pixel_size, pixel_size)

# ====== IZVEIDO TUKŠU RASTRU ======
final_raster = np.zeros((height, width), dtype=np.uint8)

# ====== APSTRĀDE ======
for i, (filename, color) in enumerate(file_colors.items(), start=1):
    path = os.path.join(input_folder, filename)
    if not os.path.exists(path):
        print(f"⚠️ Nav atrasts: {filename}")
        continue

    value = color_values[color]
    print(f"➡️ [{i}/{len(file_colors)}] Rasterizē: {filename} ({color})")

    gdf = gpd.read_file(path).to_crs(crs)
    shapes = ((geom, value) for geom in gdf.geometry if geom is not None)

    layer_raster = features.rasterize(
        shapes=shapes,
        out_shape=(height, width),
        transform=transform,
        fill=0,
        dtype=np.uint8
    )

    # Izmanto kombinācijas funkciju
    vectorized_combine = np.vectorize(combine_colors)
    final_raster = vectorized_combine(final_raster, layer_raster)

# ====== SAGLABĀ RASTRU ======
with rasterio.open(
    output_raster,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype="uint8",
    crs=crs,
    transform=transform,
) as dst:
    dst.write(final_raster, 1)

# ====== LEĢENDA ======
with open(output_legend, "w", encoding="utf-8") as f:
    f.write("value,color,meaning\n")
    for c, v in color_values.items():
        meaning = {
            1: "Pieļaujama teritorija",
            2: "Nosacīti pieļaujama (kompensējama)",
            3: "Ierobežota attīstība",
            4: "Aizliegta attīstība"
        }[v]
        f.write(f"{v},{c},{meaning}\n")

print(f"\n✅ Raster overlay pabeigts!\n💾 Saglabāts: {output_raster}\n📋 Legenda: {output_legend}")
