########################################################################
#                                                                      #
# --- ROI Manipulation and Comparison Helpers ---
# module part of DLS contour evaluation by CT RTTs (and automated tagging).  
# Kees Landheer
# Python version 3.11
# version 1.0
#                                                                      #
########################################################################

import logging
logger = logging.getLogger(__name__)

import numpy as np
from inspect import stack

# custom.
from constants import DLS_Constants

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

def coordinate_to_array(point):
    """Converts RS coordinate dict {'x':, 'y':, 'z':} to numpy array [z, y, x]."""
    return np.array([point.get("z", 0), point.get("y", 0), point.get("x", 0)])

def array_to_coordinate(array):
    """Converts numpy array [z, y, x] to RS coordinate dict {'x':, 'y':, 'z':}."""
    return {"x": array[2], "y": array[1], "z": array[0]}

# PrimaryShape voor voxelroi: number_of_voxels_array, corner_array, voxel_size_array, voxel_values_3darray
def get_triangle_mesh_as_numpy_arrays(roi_geometry):
    """Get the triangle_mesh roi primary shape data as numpy arrays. """
    #TODO: how to initialize?
    indices_array = None
    is_closed_array = None
    vertices_array = None
    triangle_mesh_parameters = None

    src_roi_name = ""
    try:
        src_roi_name = (
            roi_geometry.OfRoi.Name if roi_geometry.OfRoi else roi_geometry.ModelRoiName
        )
        if (not roi_geometry or not roi_geometry.PrimaryShape or not roi_geometry.HasContours()):
            logger.info(
                f"Warning: ROI '{src_roi_name}' has no primary shape or contours."
                " Cannot create temporary ROI."
            )
            return src_roi_name,indices_array, is_closed_array, vertices_array, triangle_mesh_parameters

        if hasattr(roi_geometry.PrimaryShape, "Vertices"):
            logger.info("Triangle MESH representation found.")
            # this is a int32 numpy array.
            indices_array = roi_geometry.PrimaryShape.Indices
            is_closed = roi_geometry.PrimaryShape.IsClosed
            vertices_list = roi_geometry.PrimaryShape.Vertices   
            length_of_vertices_list = len(vertices_list)                      
            logger.info(f"Is closed {src_roi_name} is {is_closed}")
            if is_closed:
                logger.info(f"The number of triangles (F) {indices_array.size/3} is #F = 2#V - 4")
                logger.info(f"The number of vertices #V is {length_of_vertices_list}, thus #F = 2#V - 4 = {2*length_of_vertices_list-4}.")
            else:
                logger.info(f"The roi of {src_roi_name} is NOT CLOSED.")                        
            triangle_mesh_parameters = roi_geometry.PrimaryShape.TriangleMeshParameters
              
            logger.info(f"triangle_mesh_parameters {triangle_mesh_parameters}")            
            
            if indices_array.size > 0 and is_closed and len(vertices_list) > 0:  
                # vertices_list of Point3 float for the mesh corners in centimeters. 
                vertices_array = np.zeros((len(vertices_list), 3), dtype=np.float32)
                for ind, vertex in enumerate(vertices_list):
                    vertices_array[ind,:] = coordinate_to_array(vertex)  
                is_closed_array = np.array([is_closed], dtype=bool)
            else:     
                logger.info(
                    f"Warning: Missing triangle mesh data for ROI '{src_roi_name}'."
                    " Maybe the contour is not closed. Cannot save the triangle mesh contour."
                ) 

    except Exception as e:
        logger.info(f"ERROR: Failed to get triangle mesh roi of '{src_roi_name}': {e}")    

    return src_roi_name,indices_array, is_closed_array, vertices_array, triangle_mesh_parameters

def get_voxelroi_as_numpy_arrays(roi_geometry):
    """Get the voxel roi primary shape data as numpy arrays. """
    #initialize
    number_of_voxel_array = np.empty((3,), dtype=int)
    corner_array = np.empty((3,), dtype=float)
    voxel_size_array = np.empty((3,), dtype=float)
    voxel_values_array = None

    src_roi_name = ""
    stack_for_caller = stack()
    caller_name = stack_for_caller[2].function if len(stack_for_caller) > 2 else None
    # logger.info(f"The caller name is {caller_name}.")    
    try:
        src_roi_name = (
            roi_geometry.OfRoi.Name if roi_geometry.OfRoi else roi_geometry.ModelRoiName
        )
        if (not roi_geometry or not roi_geometry.PrimaryShape or not roi_geometry.HasContours()):
            logger.info(
                f"Warning: ROI '{src_roi_name}' has no primary shape or contours."
                " Cannot create temporary ROI."
            )
            return src_roi_name,number_of_voxel_array, corner_array, voxel_size_array, voxel_values_array

        if hasattr(roi_geometry.PrimaryShape, "VoxelSize"):
            logger.info("Voxels representation found.")
            voxel_size = roi_geometry.PrimaryShape.VoxelSize
            corner = roi_geometry.PrimaryShape.Corner
            number_of_voxels = roi_geometry.PrimaryShape.NrVoxels
            voxel_values_array = roi_geometry.PrimaryShape.VoxelValues  # This might be large

            if not all([voxel_size, corner, number_of_voxels is not None]):
                logger.info(
                    f"Warning: Missing voxel data for ROI '{src_roi_name}'."
                    " Cannot create temporary copy."
                ) 
            else:        
                number_of_voxel_array = coordinate_to_array(number_of_voxels)            
                voxel_size_array = coordinate_to_array(voxel_size)
                # Corner in RS is bottom-left-posterior; center calculation needs care
                corner_array = coordinate_to_array(corner) + (
                    0.5 * voxel_size_array
                )  # Voxel center corner
            if caller_name == "process_structure_set":
                logger.info(f"For {src_roi_name} the number of voxel array: {number_of_voxel_array}")
                logger.info(f"The voxel size: {voxel_size_array}")
                logger.info(f"The corner array: {corner_array}")
                logger.info(f"The shape of the voxel_values_array array: {voxel_values_array.shape}")                        

    except Exception as e:
        logger.info(f"ERROR: Failed to get voxel roi of '{src_roi_name}': {e}")    

    return src_roi_name, number_of_voxel_array, corner_array, voxel_size_array, voxel_values_array

def get_contour_roi_as_numpy_arrays(roi_geometry):
    """Get the contour roi primary shape data as numpy arrays. """
    # initialization (more sophistication? see get_voxelroi_as_numpy_arrays)
    contours_arrays = None
    is_closed_array = None
    line_type_array = None
    line_types_list = ['PolyLine', 'CardinalSpline', 'CubicBSpline']

    src_roi_name = ""
    stack_for_caller = stack()
    caller_name = stack_for_caller[2].function if len(stack_for_caller) > 2 else None
    # logger.debug(f"The caller name is {caller_name}.")    
    try:
        src_roi_name = (
            roi_geometry.OfRoi.Name if roi_geometry.OfRoi else roi_geometry.ModelRoiName
        )
        if (not roi_geometry or not roi_geometry.PrimaryShape or not roi_geometry.HasContours()):
            logger.info(
                f"Warning: ROI '{src_roi_name}' has no primary shape or contours."
                " Cannot create temporary ROI."
            )
            return src_roi_name,contours_arrays,is_closed_array,line_type_array
        
        if hasattr(roi_geometry.PrimaryShape, "Contours"):
            logger.info("Contours representation found.")
            contours_list = roi_geometry.PrimaryShape.Contours
            is_closed = roi_geometry.PrimaryShape.IsClosed
            line_type = roi_geometry.PrimaryShape.LineType            
            length_of_contours_list = len(contours_list)            
            is_closed_array = np.array([is_closed], dtype=bool)   
            line_type_array = np.array([line_type], dtype=str)
            logger.info(f"Is closed {src_roi_name} is {is_closed}.")
            logger.info(f"The line type of {src_roi_name} is {line_type}.")
            logger.info(f"The length of the contours_list for {src_roi_name} is {length_of_contours_list}.")            
            
            if length_of_contours_list > 0 and is_closed and line_type in line_types_list:  
                # a contour: list of Point3 float in centimeters. 
                # initialize and allocate a numpy array based on length_of_contours_list
                contours_arrays = np.empty(length_of_contours_list, dtype=object)
                for list_number, my_contour_list in enumerate(contours_list):
                    # logger.info(f"The length of my_contour_list is {len(my_contour_list)}.")
                    contour_array = np.zeros((len(my_contour_list), 3), dtype=np.float32)
                    for ind, contour_point in enumerate(my_contour_list):
                        contour_array[ind,:] = coordinate_to_array(contour_point)           
                    contours_arrays[list_number]=contour_array 
            else:     
                logger.info(
                    f"Warning: Missing contour data for ROI '{src_roi_name}'."
                    " Maybe the contour is not closed. Cannot save the contour."
                ) 

    except Exception as e:
        logger.info(f"ERROR: Failed to get contour roi of '{src_roi_name}': {e}")    

    return src_roi_name,contours_arrays,is_closed_array,line_type_array


def copy_roi_geometry_from_voxels(patient_model, examination, roi_geometry, temp_roi_name):
        
    (src_roi_name, 
     number_of_voxel_array, 
     corner_array, 
     voxel_size_array, 
     voxel_values_array) = get_voxelroi_as_numpy_arrays(roi_geometry)

    try:
        copied_roi = patient_model.CreateRoi(
            Name=temp_roi_name, Color=DLS_Constants.TEMP_ROI_COLOR, Type="Undefined"
        )

        voxel_values_rle = run_length_encode_to_list(voxel_values_array)
        if voxel_values_rle is None:
            logger.info(f"Warning: RLE failed for ROI '{src_roi_name}'.")
            copied_roi.DeleteRoi()
            return None        

        number_of_voxel_dict = {temp_roi_name: array_to_coordinate(number_of_voxel_array)}
        corner_dict = {temp_roi_name: array_to_coordinate(corner_array)}
        voxel_size_dict = {temp_roi_name: array_to_coordinate(voxel_size_array)}
        voxel_values_dict = {temp_roi_name: voxel_values_rle}

        patient_model.SetVoxelValuesForRois(
            Examination=examination,
            VoxelCountForRoi=number_of_voxel_dict,
            CornerCenterForRoi=corner_dict,  # API expects center of the corner voxel
            VoxelSizeForRoi=voxel_size_dict,
            VoxelValuesForRoi=voxel_values_dict,
        )
    except Exception as e:
        logger.info(
            f"ERROR: Failed to create temporary ROI '{temp_roi_name}'"
            f" from ROI '{src_roi_name}': {e}"
        )
        # Attempt cleanup if ROI object exists
        try:
            if patient_model.RegionsOfInterest[temp_roi_name]:
                patient_model.RegionsOfInterest[temp_roi_name].DeleteRoi()
        except Exception as cleanup_e:
            logger.info(
                f"ERROR: Failed to cleanup temporary ROI '{temp_roi_name}' after"
                f" error: {cleanup_e}"
            )
        return None
    
    logger.info(f"Successfully created temporary ROI '{temp_roi_name}' from voxels.")
    return copied_roi

def process_structure_set(structure_set, patient_model):
    """Processes all relevant ROIs within a single structure set."""
    # initialization      
    examination = structure_set.OnExamination  
    examination_name = examination.Name
    names_of_all_rois_list = []
    names_of_copied_dls_rois_list = []
    names_of_existing_dls_rois_list = []

    for roi in structure_set.RoiGeometries:
        names_of_all_rois_list.append(roi.OfRoi.Name)

    logger.debug(f"The list of rois for examination {examination_name}: " + ",".join(names_of_all_rois_list))

    # 1. Process DLS ROIs
    for roi_dls in structure_set.ModelGeneratedRoiGeometries:
        roi_fix_name = roi_dls.ReferencedRoiGeometry.OfRoi.Name
        dls_roi_name = DLS_Constants.ROI_DLS_COPY_LEADING + roi_fix_name + DLS_Constants.ROI_DLS_COPY_SUFFIX
        if dls_roi_name in names_of_all_rois_list:
            names_of_existing_dls_rois_list.append(dls_roi_name)
            continue

        logger.info(f"Processing dls ROI for: {roi_fix_name}")                       
        roi_dls_copy = copy_roi_geometry_from_voxels(
            patient_model, examination, roi_dls, dls_roi_name
        )
        if roi_dls_copy is None:
            logger.info(f"Warning: Could not process dls ROI '{roi_fix_name}'")
            continue
        logger.info(f"dls ROI succesfully processed:'{roi_fix_name}'")      

        names_of_copied_dls_rois_list.append(dls_roi_name)

    logger.info(f"The following dl contouring structures already existed: " + ",".join(names_of_existing_dls_rois_list))
    logger.info(f"The following dl contouring structures were copied: " + ",".join(names_of_copied_dls_rois_list))    
    logger.info(f"Finished processing Structure Set on Examination: {examination_name}")
    return names_of_copied_dls_rois_list