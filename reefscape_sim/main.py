import numpy as np
import omni.isaac
import omni.kit.commands
import omni.usd
import omni.replicator.core as rep
from omni.isaac.core.utils.semantics import add_update_semantics
from pxr import Gf, Sdf, UsdGeom, Usd
from omni.replicator.isaac.scripts.writers import PoseWriter, YCBVideoWriter

import io
from os import listdir
from os.path import isfile, join
from omni.replicator.core import Writer, AnnotatorRegistry, BackendDispatch

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

base_field_prim_path = "/World/FE_2025/tn__FE2025_c9/tn__FullFidelityField_rHD"
coral_prim_paths = [(base_field_prim_path + "/Coral/Mesh_" + str(i)) for i in range(0, 150)]
coral_dynamic_prim_paths = [(base_field_prim_path + "/Coral/Mesh_" + str(i)) for i in range(126, 155)]
coral_static_prim_paths = [(base_field_prim_path + "/Coral/Mesh_" + str(i)) for i in range(0, 6)]
algae_static_prim_paths = [(base_field_prim_path + "/Algae/Mesh_" + str(i)) for i in range(0, 6)]
algae_prim_paths = [(base_field_prim_path + "/Algae/Mesh_" + str(i)) for i in range(0, 55)]

potential_look_prims = [
    base_field_prim_path + "/Barge/RedCageInner",
    base_field_prim_path + "/Barge/RedCageMiddle",
    base_field_prim_path + "/Barge/RedCageOuter",
    base_field_prim_path + "/Barge/BlueCageInner",
    base_field_prim_path + "/Barge/BlueCageMiddle",
    base_field_prim_path + "/Barge/BlueCageOuter",
    base_field_prim_path + "/StationBlueHigh",
    base_field_prim_path + "/StationBlueLow",
    base_field_prim_path + "/StationRedHigh",
    base_field_prim_path + "/StationRedLow",
    base_field_prim_path + "/ReefBlue",
    base_field_prim_path + "/ReefRed",
] + coral_static_prim_paths + coral_dynamic_prim_paths + algae_prim_paths

for coral_prim_path in coral_dynamic_prim_paths:
    coral = stage.GetPrimAtPath(coral_prim_path)
    if not coral.GetAttribute("xformOp:rotateXYZ"):
        UsdGeom.Xformable(coral).AddRotateXYZOp()
camera = rep.create.camera()
with rep.trigger.on_frame(rt_subframes=10):
    with camera:
        rep.modify.pose(
            position=rep.distribution.uniform((-8.5, -4.2, 0.3), (8.5, 4.2, 3.5)),
            look_at=rep.distribution.choice(potential_look_prims)
        )

    square_light = rep.get.prim_at_path("/Environment/RectLight")
    with square_light:
        rep.modify.visibility(rep.distribution.choice(choices=[True, False]))
    dome_light = rep.get.prim_at_path("/Environment/DomeLight")
    with dome_light:
        rep.modify.attribute(name="inputs:colorTemperature", value=rep.distribution.normal(4500.0, 1500.0))
        rep.modify.attribute(name="inputs:intensity", value=rep.distribution.uniform(0.0, 800.0))
        rep.modify.attribute(name="inputs:color", value=rep.distribution.uniform((0.8, 0.8, 0.8), (1.0, 1.0, 1.0)))

    for i in range(0, 6):
        coral = rep.get.prim_at_path(coral_static_prim_paths[i])
        algae = rep.get.prim_at_path(algae_static_prim_paths[i])
        visible = rep.distribution.choice(choices=[True, False, False, False, False, False])
        rep.modify.visibility(visible, input_prims=coral)
        rep.modify.visibility(visible, input_prims=algae)
    for coral_prim_path in coral_prim_paths:
        if coral_prim_path not in coral_static_prim_paths:
            coral = rep.get.prim_at_path(coral_prim_path)
            with coral:
                rep.modify.visibility(rep.distribution.choice(choices=[True, False, False, False, False, False, False, False, False, False]))
    for coral_prim_path in coral_dynamic_prim_paths:
        coral = rep.get.prim_at_path(coral_prim_path)
        with coral:
            rep.modify.pose(rotation=rep.distribution.uniform((0, 0, 0), (0, 360, 0)))
    for algae_prim_path in algae_prim_paths:
        if algae_prim_path not in algae_static_prim_paths:
            algae = rep.get.prim_at_path(algae_prim_path)
            with algae:
                rep.modify.visibility(rep.distribution.choice(choices=[True, False, False, False, False]))
    

# Will render 512x512 images
render_product = rep.create.render_product(camera, (512, 512))

# Get a YOLO Writer and initialize its defaults
writer = rep.WriterRegistry.get("KittiWriter")
writer.initialize(
    output_dir=f"C:\\dev\\Omniverse\\Reefscape\\outv3\\",
    bbox_height_threshold=5,
    fully_visible_threshold=0.75,
    omit_semantic_type=True
)
# Attach render_product to the writer
writer.attach([render_product])

# Run the simulation graph
rep.orchestrator.run(num_frames=9000)