########################################################################
#                                                                      #
# --- Export VoxelRois in seperate Thread as .npz files  ---
# module part of DLS contour evaluation by CT RTTs (and automated tagging).  
# Kees Landheer
# Python version 3.11
# version 1.0
#                                                                      #
########################################################################

# When the CT-RTT closes the evaluation form, we ask patience to the user to 
# finish the export of the contours. If the user has no patience, the export 
# thread is killed (softly).

import logging
logger = logging.getLogger(__name__)

from os import path, makedirs, listdir
from numpy import savez

from threading import Thread

# custom.
from constants import DLS_Constants, SaveLocation
from dls_roi_processing import get_voxelroi_as_numpy_arrays, get_contour_roi_as_numpy_arrays

class ExportContoursThread(Thread):
    """Thread for exporting the dl structures as voxel roi (both the adjusted and the original dl roi)."""

    def __init__(self, 
                case,
                queue, 
                stopping_event,                 
                primary_examination_name,
                patient_id
                ):
        super().__init__()
        self.case = case        
        self.queue = queue
        self.stopping_event = stopping_event        
        self.primary_examination_name = primary_examination_name
        self.patient_id = patient_id

    def stop_thread_prematurely(self):
        """Check if the stopping event is set and mark thread as stopped."""
        is_event_set = self.stopping_event.is_set()
        if is_event_set:  
            logging.info("The stopping event was triggered and the Exporting voxel roi thread is stopped prematurely.")          
        return is_event_set
    
    def save_roi_as_voxelroi(self, roi_geometry, src_roi_name, name_tag= ""):        
        filename = '{patient_id}_{case_uid}_{name_tag}_{src_roi_name}_voxelroi.npz'.format(
                    patient_id = self.patient_id, 
                    case_uid=self.case_uuid,
                    name_tag = name_tag, 
                    src_roi_name=src_roi_name)
        export_path = path.join(self.new_folder_path, filename)                        
        if filename not in self.files_list:
            roi_geometry.SetRepresentation(Representation="Voxels")
            (roi_name, 
            number_of_voxel_array, 
            corner_array_cm, 
            voxel_size_array_cm, 
            voxel_values_array) = get_voxelroi_as_numpy_arrays(roi_geometry)   
            savez(export_path, 
            number_of_voxels= number_of_voxel_array, 
            corner_in_pt_coordinates_cm=corner_array_cm, 
            voxel_size_cm = voxel_size_array_cm, 
            voxel_values = voxel_values_array)
            logger.info(f"Successfully saved {name_tag} voxel roi {src_roi_name} (aka {roi_name}) as .npz file to disk.")

    def save_roi_as_contours2D(self, roi_geometry, src_roi_name, name_tag= ""):        
        filename = '{patient_id}_{case_uid}_{name_tag}_{src_roi_name}_contourset_roi.npz'.format(
                    patient_id = self.patient_id, 
                    case_uid=self.case_uuid,
                    name_tag = name_tag, 
                    src_roi_name=src_roi_name)
        export_path = path.join(self.new_folder_path, filename)                        
        if filename not in self.files_list:
            roi_geometry.SetRepresentation(Representation="Contours")
            (roi_name, 
            contours_arrays,
            is_closed_array,
            line_type_array) = get_contour_roi_as_numpy_arrays(roi_geometry)   
            savez(export_path, 
            contours_array_cm= contours_arrays, 
            is_closed_array=is_closed_array, 
            line_type_array = line_type_array)
            logger.info(f"Successfully saved {name_tag} contours2D roi {src_roi_name} (aka {roi_name}) as .npz file to disk.")

    def run(self):
        """Thread execution: export voxel roi for the original dl segmented rois and the adjusted ROIs.
        The Voxel values are in the range 0-255 depending on how much of the voxel is covered by the ROI (0 - none, 255 - full coverage)."""
        logger.info("The export rois thread has started.")
        
        structure_set = self.case.PatientModel.StructureSets[self.primary_examination_name]

        # initialization
        is_structure_set_with_dl_contours = False
        self.export_path = SaveLocation.DLS_EXPORT_ROI_DIRECTORY        
        self.case_uuid = self.case.GetCaseUuid()
        roi_dl_name_list = []
        self.files_list = []

        # create a folder with patient_id and case_uuid if it does not yet exist. 
        self.new_folder_path = path.join(self.export_path, '{patient_id}_{case_uid}'.format(
                            patient_id = self.patient_id, 
                            case_uid=self.case_uuid)) 
        logger.info(f"The new folder path is {self.new_folder_path}.")  
        if not path.exists(self.new_folder_path):  
                # to kill the process when the gui window was manually closed.  
                if self.stop_thread_prematurely():
                    logger.info("Stop thread prematurely.0")
                    return                  
                # create patient and case specific folder for saving the contours.
                makedirs(self.new_folder_path)
        else:
            # make a list with the files in the folder. 
            self.files_list = listdir(self.new_folder_path)
            logger.info("The existing files list in the export folder: " + ",".join(self.files_list))

        if hasattr(structure_set, "ModelGeneratedRoiGeometries"):
            for roi_dls in structure_set.ModelGeneratedRoiGeometries:                
                # to kill the process when the gui window was manually closed.  
                if self.stop_thread_prematurely():
                    logger.info("Stop thread prematurely.1")
                    return
                if roi_dls.HasContours(): 
                    is_structure_set_with_dl_contours = True              
                    # You need the geometry (ReferencedRoiGeometry) for SetRepresentation
                    roi_fix_geometry = roi_dls.ReferencedRoiGeometry                    
                    # the manually adjusted contour is the ReferencedRoiGeometry.                     
                    roi_fix_name = roi_fix_geometry.OfRoi.Name      
                    roi_dl_name_list.append(DLS_Constants.ROI_DLS_COPY_LEADING + roi_fix_name + DLS_Constants.ROI_DLS_COPY_SUFFIX)
                    if roi_fix_geometry.HasContours():
                        print("UNCOMMENT TO SWITCH ON SAVING")
                        self.save_roi_as_voxelroi(roi_fix_geometry, roi_fix_name, name_tag= "dl_adjusted")
                    else:
                        logger.info(f"Roi {roi_fix_name} does not have contours. It is empty, and thus we cannot save the contours.")
        
                    # self.save_roi_as_contours2D(roi_fix_geometry, roi_fix_name, name_tag= "dl_adjusted")

        # saving the original dl contours.
        if is_structure_set_with_dl_contours:
            for roi_dls in structure_set.RoiGeometries:
                # to kill the process when the gui window was manually closed.  
                if self.stop_thread_prematurely():
                    logger.info("Stop thread prematurely.2")
                    return
                roi_dls_name = roi_dls.OfRoi.Name
                if roi_dls_name in roi_dl_name_list:
                    print("UNCOMMENT TO SWITCH ON SAVING")
                    self.save_roi_as_voxelroi(roi_dls, roi_dls_name, name_tag= "dl_original")
                    # self.save_roi_as_contours2D(roi_dls, roi_dls_name, name_tag= "dl_original")

        message = "The voxel roi of all rois have been exported."      
        logger.info(message)
        self.queue.put(message)
