# Evidence for the Lasagna bootstrap PR

| file | what it is |
|---|---|
| `before.txt` | The failure without the patch: the bootstrap command and its captured output, trimmed. Taken from `../before.log` (same run). |
| `after-real-data.txt` | With the patch: a Lasagna command run on public scroll data, its captured output, and a numeric summary of what it wrote. |
| `before.png`, `after-real-data.png` | Terminal screenshots **rendered from the two text files above** (not screen captures). |
| `render_terminal.py` | The renderer (Pillow, dark background, Menlo 15 px, 120 columns, long lines wrapped). |
| `summarize_mask.py` | The script behind the numeric summary in `after-real-data.txt`. |

The PNGs were produced with exactly:

```bash
python3 -I render_terminal.py before.txt before.png
python3 -I render_terminal.py after-real-data.txt after-real-data.png
```

## How the text files were made

- Host paths were replaced by `/work/...`: `/work/villa-before` and `/work/villa-after` are the two villa worktrees, `/work/data/PHerc0826` the downloaded public data, `/work/run` the output directory of the real-data run, `/work/tools/python` the uv-managed Python, `/work/user` the home directory. Nothing else in the captured output was edited.
- Lines starting with `#` and the `$ ...` command lines were added to label the transcript; the commands are the ones recorded for each run. `[exit code: ...]` lines come from the recorded exit status (and, for the real-data run, start/end times and wall time measured outside the container).
- `before.txt` omits the 56 install lines in the middle (torch, volume-cartographer, vc_reader, vc_object_store, all successful), marked `[... 56 lines omitted ...]`; the full output is `../before.log`.
- In `after-real-data.txt`, the summary script prints JSON; it is shown one key per line.

## The real-data run

- **Code:** villa `97fb9336c` with `0001-lasagna-bootstrap-install-gpu-manager.patch`, Lasagna venv `.venv-verif-201145` created by the patched bootstrap (the run behind `../after.log`).
- **Data:** public PHerc0826 Lasagna channels for volume `20250821151701` (`PHerc0826.lasagna.json`; `grad_mag`, `nx`, `ny` as OME-Zarr level 2, i.e. 4x downsampled; the `cos` channel was not downloaded).
- **Crop:** fullres z 10000-11000 (level-2 z 2500-2750) over the whole level-2 xy plane (2043 x 2043). Only 6608 of the slab's 32768 chunks had been downloaded, all within fullres y 3200-6527, x 128-7167; the tool reports the other 26160 chunks of the slab as missing and masks them out, which is why the summary also gives the kept fraction within the downloaded chunks.
- **Command:** `scripts/zarr_threshold_masks.py create <grad_mag zarr> --array 2 --z-range 10000,11000 --device cpu --zarr-output keep_mask.zarr -o vis`, inside the vc3d image built at the same commit, `docker run --network none --memory 24g --cpus 8`, no GPU.
- **Result:** exit code 0, 206.5 s wall time. It wrote a uint8 keep/mask-out zarr of 250 x 2043 x 2043 voxels (values 0 and 255), one JPG and one layered TIFF preview. Kept: 14.1 % of the slab, 69.7 % within the downloaded chunks; mean `grad_mag` 103.7 where kept vs 29.5 where masked inside the downloaded chunks. The outputs are derived from scroll data and are not included; the sha256 over the mask zarr's files is in the summary.
- **Not run:** `fit.py` was tried first, on CPU (no GPU was available for this run), with `--seed 3500 4700 10500` and a copy of the manifest whose `umbilicus_json` points at the published PHerc0826 umbilicus file (the published manifest leaves it empty and the cylinder init requires it). It stops in its data loader (`fit_data.load_3d_streaming` → `SparseChunkGroupCache`, which creates a `torch.cuda.Stream`) with `ValueError: Expected a cuda device, but got: cpu`, so the fit needs a CUDA GPU. That path was not tested here. (Reading the code, its streaming loader skips `cos` unless a stage needs it.)
