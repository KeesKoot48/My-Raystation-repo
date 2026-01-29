########################################################################
#                                                                      #
# Gui module for DLS contour evaluation by CT RTTs (and automated tagging).  
# KeesLandheer
# January 19, 2026
# Python versie 3.11
# versie 0.0 (demo and test version)
#                                                                      #
########################################################################

from tkinter import Label, StringVar, IntVar, BooleanVar, Checkbutton
from tkinter.ttk import Frame, Label, Button, Radiobutton, Entry

import logging
logger = logging.getLogger(__name__)

# custom library
from raystation.v2025 import get_current, await_user_input

class ScrollableContentFrame(Frame):    
    def __init__(self, master=None, dls_segmentation_data_dict=None, dls_roi_list = None, **kwargs):
        self.master = master     
        self.dls_segmentation_data_dict = dls_segmentation_data_dict         
        self.dls_roi_list = dls_roi_list        
        # custom:
        self.patient = get_current('Patient')
        self.case = get_current('Case')
        super().__init__(master, **kwargs)    

        # init parameters
        self.pady_indent_level= 5
        self.padx_indent_level1 = 10
        row_count = 0        
        self.pady_indent_level_row= 1
        set_header_column_span = 8
        set_number_of_score_radio_buttons = 5

        # add the title and header text
        start_column = 0
        self.rad_dose_label = Label(self,text="Deep Learning Segmentation Evaluation Form",  font=('calibre',20,'bold'))
        self.rad_dose_label.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'nswe', padx = self.padx_indent_level1, pady = self.pady_indent_level)  
        row_count +=1
        self.explanation_text_row1 = "Evaluate the segmentation per contour and in general. You can assing the scores (1) bad,"
        self.explanation_text_row2 = "(2) insufficient, (3) mediocre, (4) there is room for improvement or (5) excellent," 
        self.explanation_text_row3 = "and type an explanation. Scoring and typing are optional. Dont forget to press save!"
        self.explanation_text_label1 = Label(self,text=self.explanation_text_row1,  font=('calibre',12))
        self.explanation_text_label1.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'w', padx = 10, pady = 0)  
        row_count +=1
        self.explanation_text_label2 = Label(self,text=self.explanation_text_row2,  font=('calibre',12))
        self.explanation_text_label2.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'w', padx = 10, pady = 0)  
        row_count +=1
        self.explanation_text_label3 = Label(self,text=self.explanation_text_row3,  font=('calibre',12))
        self.explanation_text_label3.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'w', padx = 10, pady = 0)  

        row_count +=3

        # add table headers:
        set_header_font = ('calibre',14,'bold')
        column_count = 0
        lw_column_header_label = Label(self,text="L/w", font=set_header_font)            
        lw_column_header_label.grid(row = row_count, column = column_count,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)  
        column_count +=1
        roi_name_column_header_label = Label(self,text="ROI name", font=set_header_font)            
        roi_name_column_header_label.grid(row = row_count, column = column_count,  columnspan = 1, sticky = 'W', padx = 0, pady = self.pady_indent_level)  
        column_count +=1
        score_column_header_label = Label(self,text="Score", font=set_header_font)            
        score_column_header_label.grid(row = row_count, column = column_count,  columnspan = set_number_of_score_radio_buttons, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)  
        explanation_text_column_header_label = Label(self,text="Typ your explanation on the score:", font=set_header_font)            
        column_count += set_number_of_score_radio_buttons
        explanation_text_column_header_label.grid(row = row_count, column = column_count,  columnspan = 5, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)  

        self.table_start_row = row_count

        # add the checkbox for level window, the roi button, radiobuttons, and text field. 
        self.my_evaluation = list(range(6))
        self.score_evaluation_dict = {}
        self.text_evaluation_dict = {}
        self.lw_checkbox_state_dict = {}
        self.button_pady_indent = 1
        self.evaluation_text_width = 45

        my_index = 0
        for self.current_roi_name in self.dls_roi_list:
            self.dls_segmentation_data_dict["roi_list"].append({})
            self.dls_segmentation_data_dict["roi_list"][my_index][self.current_roi_name]=lambda: "I am shared but immutable"               
            row_count +=1                
            column_count = 0
            self.has_check_lw = BooleanVar(self)              
            self.lw_checkbox_state_dict[self.current_roi_name]= self.has_check_lw
            self.has_check_lw.set(False)  
            lw_checkbox = Checkbutton(self, variable=self.has_check_lw)               
            lw_checkbox.grid(row = row_count, column = column_count,  columnspan = 1, sticky = 'W', padx = 10, pady = self.button_pady_indent)  
            column_count +=1
            # there is no font parameter, only style for the (radio)button. 
            roi_contour_button = Button(self, text = self.current_roi_name, command = lambda roi_name=self.current_roi_name:self.click_roi_contour_button(roi_name))
            roi_contour_button.grid(row = row_count, column = column_count,  columnspan = 1, sticky = 'W', padx = 0, pady = self.button_pady_indent)  
            column_count += 1        
            new_variable_evaluation = IntVar(self)
            new_variable_evaluation.set(self.my_evaluation[0])
            self.score_evaluation_dict[self.current_roi_name]=new_variable_evaluation           
            for val in self.my_evaluation[1:]:                                                    
                my_radiobutton = Radiobutton(self, text=str(val), variable=new_variable_evaluation, value=val, 
                    command=lambda v=new_variable_evaluation: self.show_choice(v))                
                my_radiobutton.grid(row = row_count, column = column_count,  columnspan = 1, rowspan=1, sticky = 'w', padx = 0, pady = self.button_pady_indent)                
                column_count +=1
            my_text = StringVar(self, "")
            self.text_evaluation_dict[self.current_roi_name]=my_text
            self.per_roi_free_text_entry = Entry(self,width = self.evaluation_text_width, textvariable=my_text,font=('calibre',10,'normal'))                                                                     
            self.per_roi_free_text_entry.grid(row = row_count, column = column_count,  columnspan = 2, sticky = 'W', padx = self.padx_indent_level1, pady = self.button_pady_indent) 
            self.dls_segmentation_data_dict["roi_list"][my_index][self.current_roi_name]={ 
                                "score" :new_variable_evaluation,
                                "text" : my_text
            }
            my_index +=1

        row_count +=1

        text_in_container = "Bijv.: Affected by patient anatomy or imaging artefacts."
        self.general_comment = StringVar(self, text_in_container)        
        self.dls_segmentation_data_dict["general_comment"]= lambda: "I am shared but immutable"  
        self.dls_segmentation_data_dict["general_comment"] = self.general_comment
        self.general_comment_label = Label(self, text = 'Typ here general comments on the segmentation of the patient:', font=set_header_font)
        self.general_comment_label.grid(row = row_count, column = 0,  columnspan = 8, rowspan=1, sticky = 'w', padx = self.padx_indent_level1, pady = self.pady_indent_level)          
        row_count +=1
        self.general_comment_entry = Entry(self, width = 2*self.evaluation_text_width, textvariable=self.general_comment,font=('calibre',10,'normal'), justify ="left")
        self.general_comment_entry.name = "general_comment_entry"
        # TODO: discuss if initially scrolling to this general entry field is nice. 
        # self.general_comment_entry.focus()
        self.general_comment_entry.grid(row = row_count, column = 0,  columnspan = 8, rowspan=1, sticky = 'w', padx = self.padx_indent_level1, pady = self.pady_indent_level)  

        row_count +=1
        self.submit_the_score_button = Button(self, text = "Save everything.", width=20, command = self.scores_save_button)
        self.submit_the_score_button.grid(row = row_count, column = column_count,  columnspan = 2,rowspan=1, sticky = 'w', padx = self.padx_indent_level1, pady = 15)         


    # TODO: remove. 
    def show_choice(self, v):  
        current_score_value = v.get()
        message = f"the current score set is {current_score_value}."
        logger.info(message)        

    def scores_save_button(self):
        # TODO: this needs imporving anyway, this is too cumbersome!
        # sla de lijst in json\excel?? format op.        
        for key1, value1 in self.dls_segmentation_data_dict.items():
            if key1 == "general_comment":
                print(f"{key1} : {value1.get()}")
            elif key1 == "roi_list":
                for roi_dict in self.dls_segmentation_data_dict["roi_list"]:            
                    for key2, value_dict in roi_dict.items():
                        print(f"{key2}")
                        for key3, value in value_dict.items():
                            print(f"{key3} : {value.get()}")            
            else:
                print(f"{key1} : {value1},")
        # self.dls_segmentation_data_dict
        # for key, value in self.score_evaluation_dict.items():
        #     score_value = value.get()
        #     logger.info(f"roi {key}, score: {score_value}")
        # for key, value in self.text_evaluation_dict.items():
        #     text_value = value.get()
        #     logger.info(f"roi {key}, text: {text_value}")
        message = "Score opgeslagen!"
        logger.info(message)


    def click_roi_contour_button(self, roi_name):        
        for check_roi_name in self.dls_roi_list:
            self.patient.SetRoiVisibility(RoiName = check_roi_name, IsVisible = False)            

        self.patient.SetRoiVisibility(RoiName = roi_name, IsVisible = True)       
        
        is_checkbox = self.lw_checkbox_state_dict[roi_name].get()         
        logger.debug(f"the checkbox state of {roi_name} is:{is_checkbox}")
        if is_checkbox:
            # custom method:
            await_user_input("Adjust Level/window preset and press play to resume.")