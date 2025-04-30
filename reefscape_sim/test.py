import numpy as np
import omni.isaac
import omni.kit.commands
import omni.usd
import omni.replicator.core as rep
from omni.isaac.core.utils.semantics import add_update_semantics
from pxr import Gf, Sdf, UsdGeom, Usd
from omni.replicator.isaac.scripts.writers import PoseWriter, YCBVideoWriter
# from yolo_writer import YoloWriter

import io
from os import listdir
from os.path import isfile, join
from omni.replicator.core import Writer, AnnotatorRegistry, BackendDispatch
import random

def get_current_stage() -> Usd.Stage:
    return omni.usd.get_context().get_stage()

stage = get_current_stage()
replicator_prim_path = "/Replicator"

# Check if the Replicator prim exists
replicator_prim = stage.GetPrimAtPath(replicator_prim_path)
if replicator_prim.IsValid():
    # Remove the Replicator prim and its children
    stage.RemovePrim(replicator_prim_path)
    print(f"Cleared existing Replicator prim at: {replicator_prim_path}")
else:
    print(f"No existing Replicator prim found at: {replicator_prim_path}")

materials = rep.get.material(path_pattern="World/Looks/[a-zA-Z0-9_]+$")
branches = rep.get.prims(path_pattern="Branches/.+?/Mesh")

mat_paths = []
for material in materials.get_outputs()['prims']:
    mat_paths.append(material.pathString)

with branches:
    mats = rep.random.choice(mat_paths)
    rep.modify.material(mats)
with reef_bases:
    mats = rep.random.choice(mat_paths)
    rep.modify.material(mats)
with ground:
    mats = rep.random.choice(mat_paths)
    rep.modify.material(mats)

# with rep.trigger.on_frame(rt_subframes=5):
    # pass