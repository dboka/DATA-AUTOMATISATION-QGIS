import geopandas as gpd
import os
import time
from shapely.geometry import Polygon, MultiPolygon

# ====== IESTATĪJUMI ======
input_gpkg = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\READY GPKG\VMD_mezi_optimizeti.gpkg"
output_gpkg = os.path.splitext(input_gpkg)[0] + "_SUPER_SIMPLE.gpkg"

layer_name = None
tolerance = 300     # sākotnējā vienkāršošanas precizitāte metros (jo lielāka, jo gludāks un mazāks fails)
round_precision = 4 # cik ciparus aiz komata atstāt
target_crs = "EPSG:4326"

# ====== PALĪGFUNKCIJAS ======
def count_coords(geom):
    """Saskaita koordinātu punktus."""
    if geom.geom_type == "Polygon":
        return len(geom.exterior.coords)
    elif geom.geom_type == "MultiPolygon":
        return sum(len(p.exterior.coords) for p in geom.geoms)
    else:
        return 0

def simplify_geom(geom, tol):
    """Vienkāršo ģeometriju ar noteiktu toleranci."""
    try:
        return geom.simplify(tol, preserve_topology=True)
    except Exception as e:
        print(f"⚠️ Nevarēja vienkāršot ar toleranci {tol}: {e}")
        return geom

def round_coords(geom, ndigits):
    """Noapaļo koordinātas, lai samazinātu izmēru."""
    if geom.geom_type == "Polygon":
        return Polygon([(round(x, ndigits), round(y, ndigits)) for x, y in geom.exterior.coords])
    elif geom.geom_type == "MultiPolygon":
        return MultiPolygon([
            Polygon([(round(x, ndigits), round(y, ndigits)) for x, y in poly.exterior.coords])
            for poly in geom.geoms
        ])
    else:
        return geom

# ====== APSTRĀDE ======
start = time.time()
print(f"\n🌲 Sāk apstrādi: {os.path.basename(input_gpkg)}")

gdf = gpd.read_file(input_gpkg, layer=layer_name)
print(f"➡️ Ielasīts {len(gdf)} objekts ar CRS: {gdf.crs}")

# Tīrība un projekcija
gdf = gdf.to_crs(target_crs)
geom = gdf.geometry.iloc[0].buffer(0)
print(f"🟢 Sākotnējās koordinātas: {count_coords(geom)}")

# ====== AGRESĪVĀ SIMPLIFIKĀCIJA ======
for i in range(3):  # atkārto 3 reizes ar pieaugošu toleranci
    t0 = time.time()
    geom = simplify_geom(geom, tolerance)
    geom = geom.buffer(0)  # novērš iespējamos caurumus
    n_coords = count_coords(geom)
    print(f"✅ {i+1}. kārta: tolerance={tolerance}, koordinātas pēc vienkāršošanas: {n_coords}")
    tolerance *= 2  # katru reizi palielina toleranci
    print(f"⏱️ Ilgums: {round(time.time() - t0, 2)} sek.\n")

# ====== KOORDINĀTU APAĻOŠANA ======
geom = round_coords(geom, round_precision)
print(f"🎯 Pēc noapaļošanas: ~{count_coords(geom)} koordinātas")

# ====== SAGLABĀŠANA ======
optimized_gdf = gpd.GeoDataFrame(geometry=[geom], crs=target_crs)
optimized_gdf.to_file(output_gpkg, driver="GPKG")

elapsed = round(time.time() - start, 2)
print(f"\n✅ DARBS PABEIGTS! Saglabāts kā: {output_gpkg}")
print(f"⏱️ Kopējais ilgums: {elapsed} sek.\n")
