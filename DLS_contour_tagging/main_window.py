########################################################################
#                                                                      #
# Main Gui module for DLS contour evaluation by CT RTTs (and automated tagging).  
# KeesLandheer
# January 19, 2026
# Python versie 3.11
# versie 0.0 (demo and test version)
#                                                                      #
########################################################################
import System
from tkinter import Tk, Canvas
from tkinter.ttk import Scrollbar, Frame

import logging
logger = logging.getLogger(__name__)

# custom library:
from scroll_window import ScrollableContentFrame
from raystation.v2025 import get_current

# outline of the dls_segmentation_data_dict
    # "dls_segmentation_data": {
    #   "username": "Karel", 
	#   "patient_id": "65432", 
	#   "model_id" : "AB123234324",
    #   "ct_scan" : "CT 1 | Vertebrae",
    #   "general_comment" : "",
	#   "roi_list": [		
    #       {
            # "SpinalCord": { Score: 5, text: "excellent result!"},
			# "Heart": { Score: 3, text: "mediocre!"},
	# 	}	
	# 	]
	# }


def get_the_dl_segmented_and_filled_rois(case):     
    # get name of ct scan where structureset is segmented. 

    # dls_roi_dict_list = []
    dls_roi_list = []
    filled_dls_contour_counter = 0

    for structure_set in case.PatientModel.StructureSets:
        if hasattr(structure_set, "ModelGeneratedRoiGeometries"):
            structure_set_ct_scan_name = structure_set.OnExamination.Name
            logger.info(f"The structure set is created on ct scan: {structure_set_ct_scan_name}.")

            for roi in structure_set.ModelGeneratedRoiGeometries:
                if roi.HasContours(): 
                    filled_dls_contour_counter +=1
                    if filled_dls_contour_counter==1:
                        model_id = roi.ModelId

                # get the modelID from the first filled ModelGeneratedRoiGeometries
                dls_roi_list.append(roi.ReferencedRoiGeometry.OfRoi.Name)                
                # local_dls_segmentation_data_dict = {}
                # local_dls_segmentation_data_dict["RoiName"] = roi.ReferencedRoiGeometry.OfRoi.Name            
                # local_dls_segmentation_data_dict["Type"] = roi.ReferencedRoiGeometry.OfRoi.Type
                # local_dls_segmentation_data_dict["ModelId"] = roi.ModelId
                # json data:
                # local_dls_segmentation_data_dict["ModelName"] = roi.ModelMetaData
                # local_dls_segmentation_data_dict["ModelRoiName"] = roi.ModelMetaData
                # local_dls_segmentation_data_dict["ModelGenerationTime"] = roi.ModelSettings
                # dls_roi_dict_list.append(local_dls_segmentation_data_dict)     

    logger.debug("The list of filled rois with contours: " + ", ".join(dls_roi_list))
        
    # for debugging:
    # logger.info(f"dls_roi_dict_list[0]")
    # for key, value in dls_roi_dict_list[0].items():
    #     logger.info(f"{key} : {value}")

    return dls_roi_list, model_id, structure_set_ct_scan_name

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
        self.dls_segmentation_data_dict = {}
        self.structure_set_ct_scan_name = ""

        self.dls_roi_list, self.model_id, self.structure_set_ct_scan_name = get_the_dl_segmented_and_filled_rois(self.case, self.examination)

        # TODO: discuss anonimyze\encrypt the username and patientID for data collection.
        self.dls_segmentation_data_dict["username"] = System.Environment.UserName
        # logger.debug(f"The user is: {self.dls_segmentation_data_dict["username"]}")
        self.dls_segmentation_data_dict["patientid"] = self.patient.PatientID
        # logger.debug(f"The patient ID is: {self.dls_segmentation_data_dict["patientid"]}")  
        self.dls_segmentation_data_dict["model_id"] = self.model_id
        self.dls_segmentation_data_dict["ct_scan"] = self.structure_set_ct_scan_name
        self.dls_segmentation_data_dict["roi_list"] = []

        # fetch the initial visualization state, where applicable.   
        self.roi_initial_visibility_dict = {}        
        self.original_lw = self.examination.Series[0].LevelWindow

        # get initial roi visibility and make all rois invisible.         
        for roi in self.case.PatientModel.RegionsOfInterest:
            self.roi_initial_visibility_dict[roi.Name]= self.patient.GetRoiVisibility(RoiName = roi.Name)            
            self.patient.SetRoiVisibility(RoiName = roi.Name, IsVisible = False)
                
        self.grid_layout_frame = Frame(self)			
        self.grid_layout_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = Canvas(self.grid_layout_frame)
        self.scrollbar = Scrollbar(self.grid_layout_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)\
                
        self.scrollable_content_frame = ScrollableContentFrame(master=self.canvas,dls_segmentation_data_dict=self.dls_segmentation_data_dict, dls_roi_list = self.dls_roi_list)        
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
        # set roi visibility and levelwindow back to as it was at start up.
        self.scrollable_content_frame.scores_save_button()
        self.examination.Series[0].LevelWindow = self.original_lw        
        for key, value in self.roi_initial_visibility_dict.items():
            self.patient.SetRoiVisibility(RoiName = key, IsVisible = value)
        
        self.destroy()  
