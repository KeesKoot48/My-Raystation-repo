########################################################################
#                                                                      #
# Use for offline analysis of the exported voxelrois by the main script:
# DLS_contour_evaluation_form.py. 
# This script imports the voxel rois on case.Examinations[0]. This can be 
# used for analysis with RayStation functions, or the voxel roi can be 
# converted to 2d contoursets or the structure set can be exported to Dicom 
# format as RTSTRUCT (2d transversal contour sets).  
# See also the RayStation Reference Manual chapter 11 Volume Handling.
# KeesLandheer
# May 4, 2026
# Python version 3.11
# version 1.0
#                                                                      #
########################################################################

# read the numpy arrays in the .npz file and create the roi.

import numpy as np
from os import path

from raystation.v2025 import get_current
import System, clr
clr.AddReference('System.Drawing')

# TEMP_ROI_COLOR = System.Drawing.Color.FromArgb(128, 128, 255)
TEMP_ROI_COLOR = System.Drawing.Color.FromArgb(255, 0, 0)

# --- ROI Manipulation and Comparison Helpers ---
def run_length_encode_to_list(data):
    """Run-length encodes a numpy array."""
    if data is None or len(data) == 0:
        return None
    data = np.asarray(data)
    n = len(data)
    y = data[1:] != data[:-1]  # Find where value changes
    indices = np.append(np.where(y), n - 1)  # Indices of the *last* element of each run
    runs = np.diff(np.append(-1, indices))  # Calculate run lengths
    # Combine run lengths and the values corresponding to those runs
    encoded = np.ravel(np.column_stack((runs, data[indices])))
    return encoded

# def coordinate_to_array(point):
#     """Converts RS coordinate dict {'x':, 'y':, 'z':} to numpy array [z, y, x]."""
#     return np.array([point.get("z", 0), point.get("y", 0), point.get("x", 0)])

def array_to_coordinate(array):
    """Converts numpy array [z, y, x] to RS coordinate dict {'x':, 'y':, 'z':}."""
    return {"x": array[2], "y": array[1], "z": array[0]}

def main():
    # folder with the .npz numpy binary files. 
    path_to_binary_files = r"C:\Test-Kees\DL_segmentation\DL_contouren\prostaat_loge_dls_f3d35e92-3300-4573-9e69-d960599d6064"
    case = get_current("Case")     

    # arrays of voxelroi: number_of_voxels, corner_in_pt_coordinates_cm, voxel_size_cm, voxel_values
    # filename_adj = 'prostaat_loge_dls_f3d35e92-3300-4573-9e69-d960599d6064_dl_adjusted_Bladder_voxelroi.npz'
    filename_adj = 'prostaat_loge_dls_f3d35e92-3300-4573-9e69-d960599d6064_dl_original__Bladder__dls_tmp_voxelroi.npz'
    if filename_adj.endswith("_voxelroi.npz"):
        with np.load(path.join(path_to_binary_files,filename_adj)) as data:
            simple_cube_number_of_voxels_array = data['number_of_voxels']
            simple_cube_corner_array = data['corner_in_pt_coordinates_cm']
            simple_cube_voxel_size_array = data['voxel_size_cm']
            simple_cube_voxel_values_array = data['voxel_values']

        # temp_roi_name = "adj_Bladder"
        temp_roi_name = "orig_Bladder"
        try:
            copied_roi = case.PatientModel.CreateRoi(Name=temp_roi_name, Color=TEMP_ROI_COLOR, Type="Undefined")            
            print(f"Successfully created temporary ROI {temp_roi_name}.")
        except Exception as cleanup_e:
            print(f"ERROR: Failed to create roi {temp_roi_name} error: {cleanup_e}.")   

        voxel_values_rle = run_length_encode_to_list(simple_cube_voxel_values_array)
        if voxel_values_rle is None:
            print(f"Warning: RLE failed for ROI '{temp_roi_name}'.")
            copied_roi.DeleteRoi()
            return None

        number_of_voxel_dict = {temp_roi_name: array_to_coordinate(simple_cube_number_of_voxels_array)}
        corner_dict = {temp_roi_name: array_to_coordinate(simple_cube_corner_array)}
        voxel_size_dict = {temp_roi_name: array_to_coordinate(simple_cube_voxel_size_array)}
        voxel_values_dict = {temp_roi_name: voxel_values_rle}

        try:
            case.PatientModel.SetVoxelValuesForRois(
                Examination=case.Examinations[0],
                VoxelCountForRoi=number_of_voxel_dict,
                CornerCenterForRoi=corner_dict,  # API expects center of the corner voxel
                VoxelSizeForRoi=voxel_size_dict,
                VoxelValuesForRoi=voxel_values_dict,
            )
            print(f"Successfully created temporary ROI '{temp_roi_name}' from voxels.")
        except Exception as cleanup_e:
            copied_roi.DeleteRoi()  # Clean up partially created ROI
            print(
                f"ERROR: Failed to create the voxel ROI '{temp_roi_name}' "
                f" error: {cleanup_e}"
            )   

if __name__ == "__main__":
  main()