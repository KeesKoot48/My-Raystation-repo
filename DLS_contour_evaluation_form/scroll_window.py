########################################################################
#                                                                      #
# Gui module for DLS contour evaluation by CT RTTs.  
# KeesLandheer
# January 19, 2026
# Python version 3.11
# version 1.0
#                                                                      #
########################################################################

import logging
logger = logging.getLogger(__name__)

from tkinter import Label, StringVar, IntVar, font
from tkinter.ttk import Frame, Label, Button, Radiobutton, Entry, Combobox, Style

import logging
logger = logging.getLogger(__name__)
from System.Windows import MessageBox, MessageBoxButton, MessageBoxImage

# custom library
from raystation.v2025 import get_current

from constants import DLS_Constants
from utility_functions import print_dictionary_with_get, dump_dict_to_json_file


class ScrollableContentFrame(Frame):    
    def __init__(self, master=None, dl_segmentation_data_dict={}, dls_dict = {}, data_loaded=False,**kwargs):
        self.master = master     
        self.dl_segmentation_data_dict = dl_segmentation_data_dict         
        self.gui_dl_segmentation_data_dict = {}
        self.gui_dl_segmentation_data_dict["roi_list"] = []
        self.dls_dict = dls_dict    
        self.data_loaded = data_loaded    
        # custom:
        self.case = get_current('Case')        
        self.patient = get_current('Patient')       
        
        super().__init__(master, **kwargs)    

        # init parameters
        self.pady_indent_level= 5
        self.padx_indent_level1 = 10
        row_count = 0        
        self.pady_indent_level_row= 1
        set_header_column_span = 9
        set_number_of_score_radio_buttons = 4
        set_title_font = ('calibre',20,'bold')
        set_header_font = ('calibre',14,'bold')
        explanation_font = ('calibre',10)
        # entry box fonts
        self.default_font=font.Font(family='calibre',size=10,weight='normal')
        self.custom_font = font.Font(family='calibre',size=10,weight='normal', slant='italic')
        # add the checkbox for level window, the roi button, radiobuttons, and text field.         [    
        self.my_evaluation = {"NC": 0, "NOTHING_ADJUSTED": 1, "LITTLE_ADJUSTED": 2, "MANY_ADJUSTED": 3,"CONTOUR_DELETED_AND_REDRAWN": 4}
        self.score_evaluation_dict = {}
        self.lw_checkbox_state_dict = {}
        self.button_pady_indent = 1        
        style = Style(self)        
        style.configure("TEntry", foreground="black", padding=5)        
        style.configure('Custom.TEntry', foreground='deep pink', padding=5)        
        style.configure('default.TRadiobutton', foreground='deep pink', font=('calibre', 11))
        style.configure('selected.TRadiobutton', foreground='black', font=('calibre', 11))
        
        # add the title and header text
        start_column = 0
        self.rad_dose_label = Label(self,text="Deep Learning Segmentation Evaluation Form",  font=set_title_font)
        self.rad_dose_label.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'nswe', padx = self.padx_indent_level1, pady = self.pady_indent_level)  
        row_count +=1
        self.explanation_text_row1 = "Evaluate the segmentations per contour and overall. For each contour select either (1) Nothing adjusted to"
        self.explanation_text_row2 = "DL contour, (2) Little adjusted, (3) Many adjustments, or (4) DL contour deleted and redrawn."         
        self.explanation_text_row3 = "The lavender contour that becomes visible if you click the roi button is the original DL contour to be assessed."        
        self.explanation_text_row4 = "If any deletion or adjustments were necessary, please provide a brief explanation,."
        row_count +=1
        # explanation text!        
        self.explanation_text_label1 = Label(self,text=self.explanation_text_row1,  font=explanation_font)
        self.explanation_text_label1.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'w', padx = 10, pady = 0)  
        row_count +=1
        self.explanation_text_label2 = Label(self,text=self.explanation_text_row2,  font=explanation_font)
        self.explanation_text_label2.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'w', padx = 10, pady = 0)  
        row_count +=1
        self.explanation_text_label3 = Label(self,text=self.explanation_text_row3,  font=explanation_font)
        self.explanation_text_label3.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'w', padx = 10, pady = 0)  
        row_count +=1
        self.explanation_text_label4 = Label(self,text=self.explanation_text_row4,  font=explanation_font)
        self.explanation_text_label4.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'w', padx = 10, pady = 0)  

        row_count +=3

        # examination combobox. 
        label_left = Label(self,text="Examination name: ", font=explanation_font)
        label_left.grid(row = row_count, column = 0,  columnspan = 2, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level) 

        set_combobox_width = 50
        self.dls_dict_keys_list = list(self.dls_dict)
        # logger.info(f"list of dict keys examination names: " + ", ".join(self.dls_dict_keys_list))        
        self.examination_name= StringVar(self)                
        self.examination_name.set(self.dls_dict_keys_list[0])
        self.gui_dl_segmentation_data_dict["ct_scan"]= lambda: "I am shared but immutable"  
        self.gui_dl_segmentation_data_dict["ct_scan"] = self.examination_name        
        examination_combobox = Combobox(self, width = set_combobox_width, textvariable = self.examination_name)                                            
        
        examination_combobox["values"] = tuple(self.dls_dict_keys_list)
        examination_combobox.grid(row = row_count, column = 2,  columnspan = 6, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level) 
        examination_combobox.bind('<<ComboboxSelected>>', self.callback_examination_combobox)
        row_count +=2

        # add table headers:        
        column_count = 0

        roi_name_column_header_label = Label(self,text="ROI name", font=set_header_font)            
        roi_name_column_header_label.grid(row = row_count, column = column_count,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)  
        column_count +=1
        score_column_header_label = Label(self,text="Adjusted?", font=set_header_font)            
        score_column_header_label.grid(row = row_count, column = column_count,  columnspan = set_number_of_score_radio_buttons, sticky = 'W', padx = 0, pady = self.pady_indent_level)  
        explanation_text_column_header_label = Label(self,text="Typ here you explanation:", font=set_header_font)            
        column_count += set_number_of_score_radio_buttons
        explanation_text_column_header_label.grid(row = row_count, column = column_count,  columnspan = 3, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)  

        self.table_start_row = row_count
        # add the roi button, radiobuttons, and text field. 

        self.button_pady_indent = 1
        self.evaluation_text_width = 55

        my_index = 0        
        for self.current_roi_name in self.dls_dict[self.examination_name.get()]:
            self.gui_dl_segmentation_data_dict["roi_list"].append({})
            row_count +=1                
            column_count = 0
      
            new_variable_evaluation = IntVar(self)            
            if self.data_loaded:
                self.data_roi_list = [next(iter(my_dict)) for my_dict in self.dl_segmentation_data_dict["roi_list"]]        
                print("self.data_roi_list:" + ",".join(self.data_roi_list))
                if self.current_roi_name in self.data_roi_list:
                    try:
                        new_index = self.data_roi_list.index(self.current_roi_name)
                    except ValueError:
                        new_index = -1
                        logger.info(f"Yes self.current_roi_name {self.current_roi_name} in list but index not found.")
                    if ("score" in self.dl_segmentation_data_dict["roi_list"][new_index][self.current_roi_name]): 
                        new_variable_evaluation.set(self.my_evaluation[self.dl_segmentation_data_dict["roi_list"][new_index][self.current_roi_name]["score"]])
                else:
                    logger.info(f"Self.current_roi_name {self.current_roi_name} not in list.")
                    continue
            else:
                new_variable_evaluation.set(self.my_evaluation["NC"])

            # there is no font parameter, only style for the (radio)button. 
            roi_contour_button = Button(self, text = self.current_roi_name, command = lambda roi_name=self.current_roi_name:self.click_roi_contour_button(roi_name))
            roi_contour_button.grid(row = row_count, column = column_count,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.button_pady_indent)  
            column_count += 1  

            self.score_evaluation_dict[self.current_roi_name]=new_variable_evaluation
            # walk through all radiobutton score values.
            list_of_radiobuttons = [None]*(len(self.my_evaluation)-1)            
            for txt, val in self.my_evaluation.items():                                                    
                if txt == "NC":
                    continue                              
                if new_variable_evaluation.get() == 0:
                    my_radiobutton = Radiobutton(self, 
                                                text=val, 
                                                variable=new_variable_evaluation, 
                                                value=val, 
                                                style="default.TRadiobutton",
                                                command=lambda t_index=my_index, v=new_variable_evaluation, all_radiobuttons= list_of_radiobuttons: self.show_choice(t_index,v, all_radiobuttons))                
                else:
                    my_radiobutton = Radiobutton(self, 
                                                text=val, 
                                                variable=new_variable_evaluation, 
                                                value=val, 
                                                style="selected.TRadiobutton",
                                                command=lambda t_index=my_index, v=new_variable_evaluation, all_radiobuttons= list_of_radiobuttons: self.show_choice(t_index,v, all_radiobuttons))                
                my_radiobutton.grid(row = row_count, column = column_count,  columnspan = 1, rowspan=1, sticky = 'w', padx = 0, pady = self.button_pady_indent)                
                list_of_radiobuttons[column_count-1]=my_radiobutton
                column_count +=1
            my_text = StringVar(self)
            self.per_roi_free_text_entry = Entry(self,width = self.evaluation_text_width, textvariable=my_text,font=('calibre',10,'normal'))                                                                     
            self.per_roi_free_text_entry.name = self.current_roi_name
            self.per_roi_free_text_entry.grid(row = row_count, column = column_count,  columnspan = 2, sticky = 'W', padx = self.padx_indent_level1, pady = self.button_pady_indent) 
            self.per_roi_free_text_entry.bind("<FocusIn>", lambda event, the_index=my_index: self.on_focus(event,the_index))
            self.gui_dl_segmentation_data_dict["roi_list"][my_index][self.current_roi_name]={ 
                                "score" :new_variable_evaluation,                                
                                "text" : my_text
            }

            self.default_text = "think e.g. of caudal/cranial spacious/cramped."            
            if self.data_loaded:       
                text_found = self.dl_segmentation_data_dict["roi_list"][new_index][self.current_roi_name]["text"]
                my_text.set(text_found)
                if text_found == self.default_text:
                    self.per_roi_free_text_entry.configure(style="Custom.TEntry")
                    self.per_roi_free_text_entry.configure(font=self.custom_font)
                else:
                    self.per_roi_free_text_entry.configure(style="TEntry") 
                    self.per_roi_free_text_entry.configure(font=self.default_font)                                                           
            else: 
                my_text.set(self.default_text)
                self.per_roi_free_text_entry.configure(style="Custom.TEntry")
                self.per_roi_free_text_entry.configure(font=self.custom_font)

            my_index +=1                                         
        row_count +=1

        self.general_comment = StringVar(self)
        if self.data_loaded:     
            self.general_comment.set(self.dl_segmentation_data_dict["general_comment"])
        else:
            self.general_comment.set("")
        self.gui_dl_segmentation_data_dict["general_comment"]= lambda: "I am shared but immutable"  
        self.gui_dl_segmentation_data_dict["general_comment"] = self.general_comment
        self.general_comment_label = Label(self, text = 'Type here general comments on the segmentation of this patient:', font=set_header_font)
        self.general_comment_label.grid(row = row_count, column = 0,  columnspan = 8, rowspan=1, sticky = 'w', padx = self.padx_indent_level1, pady = 0)          
        row_count +=1
        general_comment_example_text = "E.g.: Segmentation is not optimal because of exceptional anatomy of patient and ct artefacts."
        self.general_comment_example_label = Label(self,text=general_comment_example_text,  font=explanation_font)
        self.general_comment_example_label.grid(row = row_count, column = start_column,  columnspan = set_header_column_span, rowspan=1, sticky = 'w', padx = 10, pady = 0)  
        row_count +=1
        self.general_comment_entry = Entry(self, width = 90, textvariable=self.general_comment,font=('calibre',10,'normal'), justify ="left")
        self.general_comment_entry.name = "general_comment_entry"

        self.general_comment_entry.grid(row = row_count, column = 0,  columnspan = 8, rowspan=1, sticky = 'w', padx = self.padx_indent_level1, pady = self.pady_indent_level)  

        row_count +=1
        self.submit_the_score_button = Button(self, text = "Save all", width=20, command = self.scores_save_button)
        self.submit_the_score_button.grid(row = row_count, column = column_count,  columnspan = 2,rowspan=1, sticky = 'w', padx = self.padx_indent_level1, pady = 15)         
       
    def on_focus(self, event, the_index):
        message = "event widget name is: " + str(event.widget.name)
        logger.info(message)
        if self.gui_dl_segmentation_data_dict["roi_list"][the_index][event.widget.name]["text"].get()==self.default_text: 
            new_text = ""
            self.gui_dl_segmentation_data_dict["roi_list"][the_index][event.widget.name]["text"].set(new_text)
            event.widget.configure(style="TEntry")
            event.widget.configure(font=self.default_font)

    def callback_examination_combobox(self, event):        
        if self.examination_name.get() != self.dls_dict_keys_list[0]:
            logger.info("Another examination is selected")
            message = "Reloading the gui after examination change is not implemented. However, the new examination name " \
            "is saved and if the same rois as for the other examination are used it will work correctly (fingers crossed)."
            MessageBox.Show(message, 'Not yet implemented!', MessageBoxButton.OK, MessageBoxImage.Warning)  
        
    def show_choice(self, t_index, v, list_of_all_radiobuttons):  
        all_states = [None]*len(list_of_all_radiobuttons)
        for my_index,rb in enumerate(list_of_all_radiobuttons):
            my_state = rb.instate(['selected'])            
            all_states[my_index]=my_state
        if any(all_states):
            # change the style to selected.TRadiobutton for all radiobuttons. 
            for rb in list_of_all_radiobuttons:
                rb.configure(style='selected.TRadiobutton')
        for key_description, score_value in self.my_evaluation.items():
            if score_value == v.get():
                current_score_value = key_description         
        my_nested_roi_dict = self.gui_dl_segmentation_data_dict["roi_list"][t_index]
        roi_name = list(my_nested_roi_dict.keys())[0]
        message = f"The current score for roi {roi_name} is {current_score_value}."        
        logger.info(message)         

    def scores_save_button(self):        
        # copy the values from gui_dl_segmentation_data_dict to dl_segmentation_data_dict 
        for key, value in self.gui_dl_segmentation_data_dict.items():
            if key != "roi_list":
                self.dl_segmentation_data_dict[key]=value.get()
               
        # do not overwrite self.dl_segmentation_data_dict["roi_list"] 
        new_dl_segmentation_roi_list_of_dicts = []
        
        list_indexer = 0
        for my_nested_roi_dict in self.gui_dl_segmentation_data_dict["roi_list"]:
            print_dictionary_with_get(my_nested_roi_dict)                               
            new_dl_segmentation_roi_list_of_dicts.append({})            
            for key_roi_name, value_roi_dict in my_nested_roi_dict.items():                                
                new_dl_segmentation_roi_list_of_dicts[list_indexer][key_roi_name]={}
                for key_roi_dict, value_roi_dict1 in value_roi_dict.items():
                    if key_roi_dict == 'score':
                        # save the scoring text (NOT the number) to the store!
                        for key_description, score_value in self.my_evaluation.items():
                            if score_value == value_roi_dict1.get():
                                new_dl_segmentation_roi_list_of_dicts[list_indexer][key_roi_name][key_roi_dict]=key_description
                    else:
                        # i.e. key_roi_dict == 'text':
                        if isinstance(value_roi_dict1, str) or isinstance(value_roi_dict1, int):
                            new_dl_segmentation_roi_list_of_dicts[list_indexer][key_roi_name][key_roi_dict]=value_roi_dict1
                        else:
                            new_dl_segmentation_roi_list_of_dicts[list_indexer][key_roi_name][key_roi_dict]=value_roi_dict1.get()                
            list_indexer +=1

        list_of_roi_names_not_present_in_current_examination = []        
        if self.data_loaded:        
            # overwrite present rois in self.dl_segmentation_data_dict
            for roi_list_index, roi_name in enumerate(self.data_roi_list):
                is_present = False
                for new_index in range(len(new_dl_segmentation_roi_list_of_dicts)):
                    if roi_name == next(iter(new_dl_segmentation_roi_list_of_dicts[new_index])):
                        self.dl_segmentation_data_dict["roi_list"][roi_list_index][roi_name]= new_dl_segmentation_roi_list_of_dicts[new_index][roi_name]
                        is_present = True 
                if not(is_present):
                    list_of_roi_names_not_present_in_current_examination.append(roi_name)
        else:
            self.dl_segmentation_data_dict["roi_list"] = new_dl_segmentation_roi_list_of_dicts

        caseuuid = self.case.GetCaseUuid()                        
        dump_dict_to_json_file( self.dl_segmentation_data_dict, self.patient.PatientID, caseuuid)
        message = "Score has been saved successfully!"
        logger.info(message)
        if list_of_roi_names_not_present_in_current_examination:
            message = "The following rois were present in the cache file, but were not present in the current examination: " \
                    + ", ".join(list_of_roi_names_not_present_in_current_examination) + \
                    ". Probably these rois were removed after the last save of the cache file."
            MessageBox.Show(message, 'Attention', MessageBoxButton.OK, MessageBoxImage.Warning)

    def click_roi_contour_button(self, roi_name):        
        for check_roi_name in self.dls_dict[self.examination_name.get()]:
            self.patient.SetRoiVisibility(RoiName = check_roi_name, IsVisible = False)                    
            self.patient.SetRoiVisibility(RoiName = DLS_Constants.ROI_DLS_COPY_LEADING + check_roi_name + DLS_Constants.ROI_DLS_COPY_SUFFIX, IsVisible = False)            

        self.patient.SetRoiVisibility(RoiName = roi_name, IsVisible = True)       
        self.patient.SetRoiVisibility(RoiName = DLS_Constants.ROI_DLS_COPY_LEADING + roi_name + DLS_Constants.ROI_DLS_COPY_SUFFIX, IsVisible = True)     
