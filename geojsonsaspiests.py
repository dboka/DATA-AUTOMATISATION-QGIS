import gzip, shutil

src = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\READY GPKG\VMD_mezi_optimizeti_FAST.geojson"
dst = src + ".gz"

with open(src, "rb") as f_in:
    with gzip.open(dst, "wb", compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)

print("✅ Saspiests fails:", dst)