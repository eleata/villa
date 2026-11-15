# Numeric summary of the real-data run: mask vs grad_mag over z 10000-11000 (level 2), PHerc0826.
import json, sys, os, hashlib, numpy as np
from vc_reader.reader import open_zarr
salida, gm_path = sys.argv[1], sys.argv[2]
m = open_zarr(f"{salida}/keep_mask.zarr")
g = open_zarr(gm_path)
mask = np.asarray(m[:, :, :])
z0 = 2500
gm = np.asarray(g[z0:z0 + mask.shape[0], :, :])
# chunks present on disk in the source slab (the rest were never downloaded)
present = np.zeros_like(mask, dtype=bool)
for zc in range(z0 // 32, (z0 + mask.shape[0] - 1) // 32 + 1):
    d = f"{gm_path}/{zc}"
    if not os.path.isdir(d):
        continue
    for yc in os.listdir(d):
        for xc in os.listdir(f"{d}/{yc}"):
            zs, ze = max(zc * 32, z0) - z0, min(zc * 32 + 32, z0 + mask.shape[0]) - z0
            present[zs:ze, int(yc) * 32:int(yc) * 32 + 32, int(xc) * 32:int(xc) * 32 + 32] = True
keep = mask > 0
h = hashlib.sha256()
for root, _, files in sorted(os.walk(f"{salida}/keep_mask.zarr")):
    for f in sorted(files):
        p = os.path.join(root, f); h.update(os.path.relpath(p, salida).encode()); h.update(open(p, "rb").read())
out = {
    "mask_shape_zyx_level2": list(mask.shape), "mask_values": sorted(int(v) for v in np.unique(mask)),
    "voxels": int(mask.size), "keep_voxels": int(keep.sum()), "keep_frac": round(float(keep.mean()), 4),
    "voxels_in_downloaded_chunks": int(present.sum()),
    "keep_frac_within_downloaded_chunks": round(float(keep[present].mean()), 4),
    "grad_mag_mean_kept": round(float(gm[keep].mean()), 2),
    "grad_mag_mean_masked_within_downloaded": round(float(gm[~keep & present].mean()), 2),
    "grad_mag_nonzero_frac_kept": round(float((gm[keep] > 0).mean()), 4),
    "kept_bbox_fullres_zyx": {ax: [int(i.min()) * 4 + o, int(i.max()) * 4 + 3 + o] for ax, i, o in zip("zyx", np.nonzero(keep), (z0 * 4, 0, 0))},
    "keep_mask_zarr_files": sum(len(f) for _, _, f in os.walk(f"{salida}/keep_mask.zarr")),
    "keep_mask_zarr_sha256_tree": h.hexdigest(),
}
print(json.dumps(out, indent=1))
