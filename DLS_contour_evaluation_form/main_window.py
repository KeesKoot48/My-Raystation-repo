########################################################################
#                                                                      #
# Main Gui module for DLS contour evaluation by CT RTTs  
# KeesLandheer
# January 19, 2026
# Python version 3.11
# version 1.0
#                                                                      #
########################################################################
from time import perf_counter
from sys import exit

# for getting the windows username.
import System
from System.Windows import MessageBox, MessageBoxButton, MessageBoxImage, MessageBoxResult
from tkinter import Tk, Canvas
from tkinter.ttk import Scrollbar, Frame

# used for opening the second thread that exports the voxelrois to numpy array files (.npz). 
from threading import Event
from queue import Queue, Empty

# for progress messages. 
from raystation import set_progress

import logging
logger = logging.getLogger(__name__)

from raystation.v2025 import get_current

# custom library:
from scroll_window import ScrollableContentFrame
from dls_roi_processing import process_structure_set
from constants import DLS_Constants
from export_contours import ExportContoursThread
from utility_functions import open_json_file_as_dict
# contents of the json data container, called dl_segmentation_data_dict.
    # "dl_segmentation_data": {     
	#   "patient_id": "65432", 
	#   "model_id" : "AB123234324",
    #   "ct_scan" : "CT 1 | Vertebrae",
    #   "general_comment" : "",
	#   "roi_list": [		
    #       {
            # "SpinalCord": { Score: 0, text: ""},
			# "Heart": { Score: 3, text: ""},
	# 	}	
	# 	],
    #   "treatment_site": "1:_2026-03-06_prostate",
    #   "username": "Karel"
	# }

def get_the_dl_segmented_and_filled_rois(case):     
    # initialize:
    # dictionary with examination name : dls_roi_list. 
    examination_name_dls_roi_list_dict = {}
    model_id = -1
    number_of_structuresets = len(case.PatientModel.StructureSets)
    list_of_structure_set_counters = [0]*number_of_structuresets

    # check for each structure set if it contains dl segmented structures. 
    for ss_number, structure_set in enumerate(case.PatientModel.StructureSets):
        if hasattr(structure_set, "ModelGeneratedRoiGeometries"):
            number_of_modelgenerated_roigeometries = structure_set.ModelGeneratedRoiGeometries.Count     
            #initialize:
            dls_roi_list = []
            first_has_contours = True      

            list_of_structure_set_counters[ss_number]=number_of_modelgenerated_roigeometries
            counter = 0
            for roi in structure_set.ModelGeneratedRoiGeometries:                
                if roi.HasContours():
                    # if the roi is not editable (i.e. locked) the contour cannot be exported (and definitely not converted to Voxelroi representation). 
                    if not roi.ReferencedRoiGeometry.IsRoiGeometryEditable():
                        message = f"Some rois in the structure set are locked (at least roi {roi.ReferencedRoiGeometry.OfRoi.Name}), therefore this script cannot be executed and will close."
                        MessageBox.Show(message, 'Structure set is locked!', MessageBoxButton.OK, MessageBoxImage.Error)  
                        logger.info(message)
                        exit(message)                   
                    dls_roi_list.append(roi.ReferencedRoiGeometry.OfRoi.Name)       
                    if first_has_contours:
                        examination_name = structure_set.OnExamination.Name
                        start = perf_counter()
                        names_of_copied_dls_rois_list = process_structure_set(
                            structure_set=structure_set,
                            patient_model=case.PatientModel,
                        )   
                        end = perf_counter()
                        logger.info(f"Copying the dls structure {examination_name} set took: {end - start:.3f} seconds.")                                                       
                        first_has_contours = False                    
                        model_id = roi.ModelId

                if (counter == number_of_modelgenerated_roigeometries-1):                        
                    examination_name_dls_roi_list_dict[structure_set.OnExamination.Name]= dls_roi_list                                
                    logger.debug(f"The list of adjusted filled rois for examination {examination_name} with contours: " + ", ".join(dls_roi_list))    
                    logger.debug(f"The list of copied original filled rois for examination {examination_name} with contours: " + ", ".join(names_of_copied_dls_rois_list))
                counter +=1
        else:
            logger.info(f"Skipping Structure Set on {structure_set.OnExamination.Name} (no MGRs).")
            continue 

    # check if all values are zeros          
    if all(x == 0 for x in list_of_structure_set_counters):
        # in fact the list structure_set.ModelGeneratedRoiGeometries is Empty!
        message = "No dl segmented rois were found for this case. The script will close."
        MessageBox.Show(message, 'No segmented rois found!', MessageBoxButton.OK, MessageBoxImage.Error) 
        logger.info(message)
        exit(message) 

    return examination_name_dls_roi_list_dict, model_id

class RootWindow(Tk):		
    def __init__(self):		
        super().__init__()
        # position the window in the upper right corner. 
        screen_width = self.winfo_screenwidth()         				
        self.window_width = 720
        self.window_height = 250
        if (screen_width > self.window_width):            
            self.window_x = screen_width - self.window_width -5
        else:
            self.window_x =1
        self.window_y = 10
        self.geometry('%dx%d+%d+%d' % (self.window_width, self.window_height, self.window_x, self.window_y)) 
        self.title("DLS evaluation form")

        # custom: 
        self.case = get_current('Case')
        self.examination = get_current('Examination')
        self.patient = get_current('Patient')

        self.model_id = -1
        self.dl_segmentation_data_dict = {}
        self.structure_set_ct_scan_name = ""
        self.is_dl_segmentation_data_present_in_dict = False
        self.is_wait_for_cue = False
        self.is_contours_exported = False
        self.primary_examination_name = ""

        # initialization for 2nd thread.
        self.queue = Queue()
        self.stopping_event = Event()
        self.export_contours_thread = None

        set_progress('Find dl segmented contours and create the original structures.')
        self.examination_name_dls_roi_list_dict, self.model_id = get_the_dl_segmented_and_filled_rois(self.case)

        number_of_examinations_with_countours = len(self.examination_name_dls_roi_list_dict)
        logger.info(f"number of examination with countours: {number_of_examinations_with_countours}.")

        if number_of_examinations_with_countours > 0:
            self.primary_examination_name = next(iter(self.examination_name_dls_roi_list_dict))
            logger.info(f"primary_examination_name {self.primary_examination_name}.")
        
        # for now we assume that there is only one examination with contours and we export its contours here in a seperate thread.  
        # if more than 1 key in examinations drop down: wait for the gui and selection and then export (not yet implemented).                 
        if number_of_examinations_with_countours > 1:
            logger.info("There is more than one examination with a dl structure set.")
        self.export_contours_thread = ExportContoursThread(
            case = self.case,
            queue=self.queue,
            stopping_event=self.stopping_event, 
            primary_examination_name = self.primary_examination_name,
            patient_id=self.patient.PatientID                       
        )
        self.export_contours_thread.start()      

        self.periodiccall()  
        # else:
        #     logger.info("Postpone spinning up the export thread.")               

        set_progress('Load present evaluation form input, if present.')
        caseuuid = self.case.GetCaseUuid()  
        self.dl_segmentation_data_dict = open_json_file_as_dict(self.patient.PatientID, caseuuid)
        if self.dl_segmentation_data_dict:
            self.is_dl_segmentation_data_present_in_dict = True       
        
        if not self.is_dl_segmentation_data_present_in_dict:
            self.dl_segmentation_data_dict["username"] = System.Environment.UserName
            self.dl_segmentation_data_dict["patient_id"] = self.patient.PatientID
            # logger.debug(f"The patient ID is: {self.dl_segmentation_data_dict["patientid"]}")               
            self.dl_segmentation_data_dict["model_id"] = self.model_id  
            self.dl_segmentation_data_dict["treatment_site"] = self.case.CaseName
            self.dl_segmentation_data_dict["Raystation_version"] = self.patient.ModificationInfo.SoftwareVersion if hasattr(self.patient.ModificationInfo, 'SoftwareVersion') else 'unknown'
            self.dl_segmentation_data_dict["ct_scan"] = self.structure_set_ct_scan_name
            self.dl_segmentation_data_dict["roi_list"] = [] 
        
        # also if loaded it should be overwritten. 
        self.dl_segmentation_data_dict["number_of_examinations_with_dl_contours"] = number_of_examinations_with_countours
        # fetch the initial visibility state, where applicable.   
        self.roi_initial_visibility_dict = {}                

        # get initial roi visibility and make all rois invisible.         
        for roi in self.case.PatientModel.RegionsOfInterest:
            self.roi_initial_visibility_dict[roi.Name]= self.patient.GetRoiVisibility(RoiName = roi.Name)            
            self.patient.SetRoiVisibility(RoiName = roi.Name, IsVisible = False)
                
        self.grid_layout_frame = Frame(self)			
        self.grid_layout_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = Canvas(self.grid_layout_frame)
        self.scrollbar = Scrollbar(self.grid_layout_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)\
                
        set_progress('Launch the evaluation form window and start giving feedback.')        
        self.scrollable_content_frame = ScrollableContentFrame(master=self.canvas,dl_segmentation_data_dict=self.dl_segmentation_data_dict, 
                                                               dls_dict = self.examination_name_dls_roi_list_dict, data_loaded = self.is_dl_segmentation_data_present_in_dict)        
        self.scrollable_content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # create window resizing configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid_layout_frame.columnconfigure(0, weight=1)
        self.grid_layout_frame.rowconfigure(0, weight=1)

        # pack widgets onto the window
        self.canvas.create_window((0, 0), window=self.scrollable_content_frame, anchor="nw")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # bind the callbacks. 
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # vertical scroll    
    def _on_mousewheel(self,event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")    

    # close the script window and stop the application.
    def on_closing(self):
        # set roi visibility back to as it was at start up.
        self.scrollable_content_frame.scores_save_button()        
        # 
        # if necessary, wait for the export to finish and then delete the temporary rois. 
        if not self.is_wait_for_cue and not self.is_contours_exported:
            if self.stop_the_script():                
                return        
            
        for key, value in self.roi_initial_visibility_dict.items():
            self.patient.SetRoiVisibility(RoiName = key, IsVisible = value)

        # clean up original dls structures. 
        for examination_remove_name, dls_remove_roi_list in self.examination_name_dls_roi_list_dict.items():
            for check_roi_name in dls_remove_roi_list:
                dls_temp_roi_name = DLS_Constants.ROI_DLS_COPY_LEADING + check_roi_name + DLS_Constants.ROI_DLS_COPY_SUFFIX                            
                try: 
                    if self.case.PatientModel.RegionsOfInterest[dls_temp_roi_name]:
                        self.case.PatientModel.RegionsOfInterest[dls_temp_roi_name].DeleteRoi()
                        logger.debug(f"Roi {dls_temp_roi_name} of examination {examination_remove_name} was successfully deleted.")
                except Exception as cleanup_e:
                    logger.info(
                        f"ERROR: Failed to cleanup original dl ROI '{dls_temp_roi_name}' after"
                        f" error: {cleanup_e}"
                    )

        examination_name = self.examination.Name   
        logger.debug(f"Current examination name: {examination_name}")     
        if examination_name != self.primary_examination_name:
            message = "The current examination is not the primary examination with the structure set. " \
            "Are you aware? This means that the structure set of the current examination is not used for the evaluation " \
            "form and the analysis. If this happened accidentally, please ask a researcher to check the collected data."
            logger.info(message)
            # MessageBox.Show(message, 'Something is wrong!', MessageBoxButton.OK, MessageBoxImage.Error)

        self.destroy()  

    def stop_the_script(self):   
        # 3 situations exist: 
        # (1) the client thread is not yet initialized (None) 
        # (2) only the main thread is active, 
        # (3) the main and client threads are active (and need to be terminated).        
        if self.export_contours_thread is None:            
            logger.info("Stop the script, threadedclient does not exist (anymore).")
            exit()               
        elif not(self.export_contours_thread.is_alive()):
            logger.info("Stop the script, client thread is no longer alive")
            exit()      
        else:
            # this will stop the export roi thread prematurely. 
            # message = "Kunt u a.u.b. een momentje wachten? Het exporteren van de rois is nog niet afgerond. Als u Ja klikt " \
            # "geven we een seintje zodra het exporteren klaar is."
            message = "Can you wait a moment please? Exporting all rois has not been finished yet. If you press Yes we will " \
            "notify you when the export has finished."
            answer = MessageBox.Show(message, 'Exporting the rois not yet finished!', MessageBoxButton.YesNo, MessageBoxImage.Warning) 
            if answer == MessageBoxResult.No:                 
                self.stopping_event.set()            
                message = 'The user closed the script. Wait a moment for the script to finish. I will give a notification when script has finished.'                    
                set_progress(message)
                logger.info(message)
            else:
                self.is_wait_for_cue = True
        # logger.debug(f"Wait for cue is: {self.is_wait_for_cue}.")
        return self.is_wait_for_cue                

    def periodiccall(self):
        self.checkqueue()        
        if self.export_contours_thread.is_alive():
            self.after(1000, self.periodiccall)
        else:
            self.stopping_event.clear()
            message= "Exporting the rois has been successfully completed."
            set_progress(message)
            logger.info(message)

    def checkqueue(self):
        while self.queue.qsize():
            try:
                message = self.queue.get(0)                
                if message.startswith("The voxel roi of all rois have been exported."):
                    self.is_contours_exported = True
                    # for debugging
                    if self.is_wait_for_cue:
                        message = "All rois have been exported successfully. We continue with tidying up and closing the script gracefully."
                        logger.info(message)
                        MessageBox.Show(message, 'All rois have been exported successfully!', MessageBoxButton.OK, MessageBoxImage.Warning)                                                                        
                        self.on_closing()                    
                    else:
                        self.stopping_event.set()
            except Empty:
                pass
    
    
