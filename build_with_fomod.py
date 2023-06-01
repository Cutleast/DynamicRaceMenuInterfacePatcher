"""
This script builds the DRIP.exe and packs
all its dependencies with a FOMOD in one folder
for installing as a mod.
"""

import shutil
from pathlib import Path

dist_folder = Path("main.dist").resolve()
fomod_folder = Path("fomod").resolve()
output_folder = Path("DRIP_with_fomod").resolve() / "fomod"

print("Packing with FOMOD...")
if output_folder.is_dir():
    shutil.rmtree(output_folder)
    print("Deleted already existing output folder.")

print("Copying FOMOD...")
shutil.copytree(fomod_folder, output_folder, dirs_exist_ok=True)

print("Copying DRIP...")
shutil.copytree(dist_folder, output_folder / "DRIP", dirs_exist_ok=True)

print("Done!")
