# create classes of the different tabs in the main window.
from tkinter import messagebox, Label, Entry, Frame, Button, StringVar
from tkinter.ttk import Combobox
from tkinter.filedialog import asksaveasfilename 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from types import LambdaType
from os import path
from enum import Enum

# custom
from citor.utilities import print_dictionary, dump_dict_to_json_file, open_json_file
from citor.constants import TestScriptsConstants, PredictorValueConstants,  TextFormatConstants, SaveLocation
from citor.CITOR_profile_head_and_neck import CitorProfile
from citor.enum_module import sex_dictionary, TumorSite,TreatmentModality, \
    BaselineToxicityPatient, BaselineToxicityPhysician, PostOperative, EnumEncoder

def update_external_citordata_datasource(ids):   
    is_okcancel1 = messagebox.askokcancel(title="Yes or No",message="Do you want to save the new citor info in a json?")
    if is_okcancel1:
        dump_dict_to_json_file(ids.citor_info, ids.patient_raystation_info_dict["Patient"].PatientID)

#######################################################################################
#
# BASIC INPUT AND BASELINE, tab1		
#
#######################################################################################
class TabBasicInputAndBaseline(Frame):    
    def __init__(self, master=None, ids = None, citorprofile = CitorProfile, cnf={}, **kwargs):
        self.ids= ids
        self.CitorProfile = citorprofile
        super().__init__(master, cnf, **kwargs)    

        # init parameters
        padx_indent_level1 = 10
        padx_indent_level2 = 20
        pady_indent_level1= 5
        pady_indent_level2 = 20

        button_font_size = 10
        
        row_count = 0
        set_combobox_width = 25
        self.basic_input_variable_dict={}
        self.postoperative_explain_label_text = StringVar()
        self.number_no_roi_present_var = StringVar(self, self.ids.citor_info["prediction_and_evaluation"][self.ids.citor_info["patient_and_plan"]["PlanName"]]["number_no_roi_present"])

        self.comboboxes_enum_list = [TumorSite, TreatmentModality, PostOperative]
        self.comboboxes_enum_dict = {enum.__name__ : enum for enum in self.comboboxes_enum_list}
        self.comboboxeslist = [enum.__name__ for enum in self.comboboxes_enum_list]        

        basic_input_label = Label(self,text="Basis invoergegevens: ",  font=('calibre',20,'bold'))
        basic_input_label.grid(row = row_count, column = 0,  columnspan = 2, rowspan=3, sticky = 'w', padx = padx_indent_level1, pady = pady_indent_level2)  


        # keys are from self.ids.citor_info["patient_characteristics"] and the values are the widget label text.  
        self.basic_input_dict = {
            'Age_in_years' : "Leeftijd: ", 
            'Patient_sex' : "Geslacht: ",
            'Weight_in_kg' : "Gewicht in kg: (Geef Enter na invullen)",
            'TumorSite' : "Tumorlocatie: ",
            'TreatmentModality': "Behandelingsmodaliteit: ",
            'PostOperative' : "Post-operatieve bestraling: "            
            }

        row_count +=3        

        for key in self.basic_input_dict.keys():        
            row_count +=1
            label_left = Label(self,text=self.basic_input_dict[key])
            label_left.grid(row = row_count, column = 0,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1) 
            if key == "Age_in_years":    
                self.basic_input_variable_dict[key]=StringVar(self,str(self.ids.citor_info["patient_characteristics"][key])+ " jaar")   
                label_right = Label(self,textvariable=self.basic_input_variable_dict[key])
                label_right.grid(row = row_count, column = 1,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1) 
                if (self.ids.citor_info["patient_characteristics"][key] == -1):
                    self.basic_input_variable_dict[key].set("onbekend")
            elif key == "Patient_sex":
                self.basic_input_variable_dict[key]= StringVar(self, sex_dictionary[self.ids.citor_info["patient_characteristics"][key].name])                
                label_right = Label(self,textvariable= self.basic_input_variable_dict[key])
                label_right.grid(row = row_count, column = 1,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1) 
            elif key == "Weight_in_kg":  
                self.basic_input_variable_dict[key]= StringVar(self, str(self.ids.citor_info["patient_characteristics"][key]))
                self.weight_entry = Entry(self,width = set_combobox_width-1, textvariable=self.basic_input_variable_dict[key],font=('calibre',10,'normal'))                             
                self.weight_entry.name = "Weight_in_kg"                
                self.weight_entry.focus()
                self.weight_entry.grid(row = row_count, column = 1,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1) 
                self.weight_entry.bind("<Return>", self.callback_basic_input_combobox)
            elif key in self.comboboxeslist:
                self.basic_input_variable_dict[key]= StringVar(self, self.ids.citor_info["patient_characteristics"][key].name)                
                new_combobox = Combobox(self, width = set_combobox_width, textvariable = self.basic_input_variable_dict[key])                
                new_combobox.name = key                        
                new_combobox["values"] = [e.name for e in self.comboboxes_enum_dict[key]]
                new_combobox.grid(row = row_count, column = 1,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1) 
                new_combobox.bind('<<ComboboxSelected>>', self.callback_basic_input_combobox)                

        # add label next to Postoperative combobox.          
        self.postoperative_explain_label = Label(self,textvariable=self.postoperative_explain_label_text, fg='red')
        self.postoperative_explain_label.grid(row = row_count, column = 2,  columnspan = 2, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1) 
        self.postoperative_explain_label.grid_remove()
      
        # baseline
        row_count +=2
        self.baseline_label = Label(self,text="Baseline EORTC",  font=('calibre',20,'bold'))
        self.baseline_label.grid(row = row_count, column = 0,  columnspan = 2, rowspan=3, sticky = 'w', padx = padx_indent_level1, pady = pady_indent_level2)  
        row_count +=3

        self.dict_of_baseline_EORTC_questions = {
        "Q31_mouth_pain": "Have you had pain in your mouth?",
        "Q32_jaw_pain": "Have you had pain in your jaw?",
        "Q33_mouth_soreness": "Have you had soreness in your mouth?",
        "Q34_throat_pain": "Have you had a painful throat?",
        "Q38_choking": "Have you choked when swallowing?",
        "Q41_dry_mouth": "Have you had a dry mouth?",
        "Q42_sticky_saliva": "Have you had sticky saliva?",
        "Q53_trouble_talking_to_people": "Have you had trouble talking to other people?",
        "Q54_trouble_talking_on_phone": "Have you had trouble talking on the telephone?",
        "Q10_rest_needed": "Did you need to rest?",
        "Q12_feeling_weak": "Have you felt weak?",
        "Q14_nauseated": "Have you felt nauseated?",
        "Q15_vomiting": "Have you vomited?",
        "Q18_tired": "Were you tired?"
        }

        self.baseline_keys = self.ids.citor_info['baseline'].keys()
        self.baseline_physician_rated_dict = {"PhR_aspiration":"Aspiration","PhR_dysphagia":"Dysphagia", "PhR_xerostomia":"Xerostomia"}        
        
        # Create EORTC baseline combo boxes:
        self.baseline_variable={} # list of StringVar
        self.baseline_EORTC_comboboxes_list=[] # a list of combobox objects. 
        self.combobox_baseline_values =  [e.name for e in BaselineToxicityPatient]
      
        row_count_temp = row_count

        for key, value in self.dict_of_baseline_EORTC_questions.items():               
            question_label_left = Label(self,text=value)
            self.baseline_variable[key]=StringVar(self, self.ids.citor_info["baseline"][key].name) 
            new_combobox = Combobox(self, width = set_combobox_width, textvariable = self.baseline_variable[key])
            new_combobox.name = key
            new_combobox["values"] = self.combobox_baseline_values 
            new_combobox.bind('<<ComboboxSelected>>', self.callback_baseline_EORTC_combobox)
            # placement:
            if (row_count-row_count_temp) ==1:      
                row_count_temp = row_count
                question_label_left.grid(row = row_count, column = 2,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1)                         
                new_combobox.grid(row = row_count, column = 3,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1)                         
            else:
                row_count +=1         
                question_label_left.grid(row = row_count, column = 0,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1)                         
                new_combobox.grid(row = row_count, column = 1,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1)                                         


        # physician_rated baseline combo boxes:
        row_count +=1
        self.basic_input_label = Label(self,text="Baseline Physician-rated",  font=('calibre',20,'bold'))
        self.basic_input_label.grid(row = row_count, column = 0,  columnspan = 2, rowspan=3, sticky = 'w', padx = padx_indent_level1, pady = pady_indent_level2)  
        row_count +=2
        
        self.baseline_physician_rated_comboboxes_list=[] # a list of combobox objects. 
        self.combobox_baseline_physician_rated_values = [e.name for e in BaselineToxicityPhysician]
                                    
        for key, value in self.baseline_physician_rated_dict.items():                     
            question_label_left = Label(self,text=value)
            # the value of the combobox is apparently not stored in the textvariable.....
            self.baseline_variable[key]=StringVar(self,self.ids.citor_info["baseline"][key].name) 
            new_combobox = Combobox(self, width = set_combobox_width, textvariable = self.baseline_variable[key])
            new_combobox.name = key
            new_combobox["values"] = self.combobox_baseline_physician_rated_values   
            new_combobox.bind('<<ComboboxSelected>>', self.callback_baseline_physician_rated_combobox)
            # placement:
            row_count +=1   
            question_label_left.grid(row = row_count, column = 0,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1)             
            new_combobox.grid(row = row_count, column = 1,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1)             

        self.recount()

        row_count +=5                         
        radiation_dose_parameters_status_left_label = Label(self,text="Aantal oar van de citor die niet zijn ingetekend (aka no roi present): ")
        radiation_dose_parameters_status_left_label.grid(row = row_count, column = 0,  columnspan = 2, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level1)             
        self.radiation_dose_parameters_status_right_label = Label(self,textvariable=self.number_no_roi_present_var)
        self.radiation_dose_parameters_status_right_label.grid(row = row_count, column = 2,  columnspan = 1, sticky = 'W', padx = padx_indent_level1, pady = pady_indent_level1)             

    def recount(self):      
        number_no_roi_present = sum(1 for v in self.ids.citor_OAR_dict.values() if (v == "no roi present"))
        self.number_no_roi_present_var.set(str(number_no_roi_present))
        self.ids.citor_info["prediction_and_evaluation"][self.ids.citor_info["patient_and_plan"]["PlanName"]]["number_no_roi_present"]=number_no_roi_present

    def update_citor_info_displayed(self):
        for key in self.basic_input_variable_dict.keys():
            if isinstance(self.ids.citor_info["patient_characteristics"][key], Enum):
                self.basic_input_variable_dict[key].set(self.ids.citor_info["patient_characteristics"][key].name)                
            else:
                self.basic_input_variable_dict[key].set(str(self.ids.citor_info["patient_characteristics"][key]))
        for key in self.baseline_variable.keys():
            self.baseline_variable[key].set(self.ids.citor_info["baseline"][key].name)

    # this method is called from mygui.py
    def update_citor_info_callback(self):
        self.ids.citor_info["patient_characteristics"]["Weight_in_kg"] = self.weight_entry.get()
        # update_citor_info_displayed should not be necessary. 
        self.update_citor_info_displayed()                       
        update_external_citordata_datasource(self.ids)

    def callback_basic_input_combobox(self, event):                   
        message1 = "event widget name is: " + str(event.widget.name)
        print(message1)                
        if event.widget.name in self.comboboxeslist:
            current_value = event.widget.get()
            my_enum = self.comboboxes_enum_dict[event.widget.name]
            self.ids.citor_info["patient_characteristics"][event.widget.name]= my_enum[current_value]
            if event.widget.name == "PostOperative":
                if current_value=='YES':
                    self.postoperative_explain_label.grid() 
                    self.postoperative_explain_label_text.set("The NTCP models applied are for primary radiotherapy.")                                  
                elif current_value=='NO':
                    self.postoperative_explain_label.grid_remove()
            message2 = "the current value is: " + str(current_value)
        else:
            weight_in_kg = event.widget.get() 
            try:
                Weight_in_kg = round(float(weight_in_kg),1)   
                self.ids.citor_info["patient_characteristics"]["Weight_in_kg"] = Weight_in_kg                      
                message2 = "The weight of this patient is: " + str(Weight_in_kg) + "kg."
            except ValueError:
                message2 = "Sorry, I didn't understand that. Enter a new value in kg." 
        print(message2)

    # callback for when the combobox value is changed. 
    def callback_baseline_EORTC_combobox(self, event):           
        current_value = event.widget.get()    
        if event.widget.name in self.baseline_keys: 
            self.ids.citor_info["baseline"][event.widget.name]= BaselineToxicityPatient[current_value]       
            message = "the current value of " +  str(event.widget.name)  +  " is: " + str(BaselineToxicityPatient[current_value])
            print(message)            

    def callback_baseline_physician_rated_combobox(self, event):           
        current_value = event.widget.get()   
        if event.widget.name in self.baseline_physician_rated_dict.keys(): 
            self.ids.citor_info["baseline"][event.widget.name]=BaselineToxicityPhysician[current_value]  
            message = "the current value is: " + str(BaselineToxicityPhysician[current_value])        
            print(message)
            
           
  
#######################################################################################
#
# CITOR PROFILE, tab2		
#
#######################################################################################
class TabCitorProfile(Frame):    
    def __init__(self, master=None, ids = None, cnf={}, **kwargs):
        self.ids= ids
        super().__init__(master, cnf, **kwargs)       

        # initialize a figure for the Citor profile.                 
        set_ScaleFactor = 0.95
        set_figure_width = 10*set_ScaleFactor
        set_figure_height = 10*set_ScaleFactor        
        self.figure = Figure(figsize=(set_figure_width, set_figure_height))

        plot_canvas = FigureCanvasTkAgg(self.figure, master=self)
        plot_canvas.draw()
        self.ax = plot_canvas.figure.subplots()          

        # initialize the citor profile.       
        self.CitorProfile = CitorProfile(self.ids, self.ax)    
        self.CitorProfile.create_citor_profile_heatmap()

        padx_indent_level1 = 2
        padx_indent_level2 = 10
        pady_indent_level= 4

        # init parameters
        row_count = 0
        # add labels and entrys to give a prospective and retrospective textual analysis.  
        set_combobox_width = 120
        rowspan_profile = 25
        self.rowconfigure(0, weight=rowspan_profile)
        plot_canvas.get_tk_widget().grid(row = row_count, column = 0,  rowspan=1, columnspan = 8, sticky = 'nw', padx = 0, pady = pady_indent_level) 

        self.prospective_variable = StringVar(self, self.ids.citor_info["prediction_and_evaluation"][self.ids.citor_info["patient_and_plan"]["PlanName"]]["Prospective"])
        self.retrospective_variable = StringVar(self, self.ids.citor_info["prediction_and_evaluation"][self.ids.citor_info["patient_and_plan"]["PlanName"]]["Retrospective"])

        row_count +=1
        self.left_label_prospective = Label(self, text = 'Prospectief', font=('calibre',12,'bold'))
        self.left_label_prospective.grid(row = row_count, column = 0,  columnspan = 1, rowspan=1, sticky = 'w', padx = padx_indent_level2, pady = pady_indent_level)          
        self.right_prospective_entry = Entry(self, width = set_combobox_width-1, textvariable=self.prospective_variable,font=('calibre',10,'normal'), justify ="right")
        self.right_prospective_entry.name = "Prospectief"
        self.right_prospective_entry.grid(row = row_count, column = 1,  columnspan = 7, rowspan=1, sticky = 'w', padx = padx_indent_level1, pady = pady_indent_level)  
        self.right_prospective_entry.bind("<Return>", self.give_evaluation_text)

        row_count +=1
        self.left_label_retrospective = Label(self, text = 'Retrospectief', font=('calibre',12,'bold'))
        self.left_label_retrospective.grid(row = row_count, column = 0,  columnspan = 1, rowspan=1, sticky = 'w', padx = padx_indent_level2, pady = pady_indent_level)  

        self.right_retrospective_entry = Entry(self, width = set_combobox_width-1, textvariable=self.retrospective_variable,font=('calibre',10,'normal'), justify ="right")
        self.right_retrospective_entry.name = "Retrospectief"
        self.right_retrospective_entry.grid(row = row_count, column = 1,  columnspan = 7, rowspan=1, sticky = 'w', padx = padx_indent_level1, pady = pady_indent_level)  
        self.right_retrospective_entry.bind("<Return>", self.give_evaluation_text)

        row_count +=1
        self.save_screenshot_button = Button(self, text = 'Save Citor Profile screenshot and text', bd = '5', \
                                                             font=('calibre',12,'bold'), command = self.save_screenshot_citor_profile)
        self.save_screenshot_button.grid(row = row_count, column = 0,  columnspan = 3, rowspan=1, sticky = 'sw', padx = padx_indent_level2, pady = pady_indent_level)  

        if TestScriptsConstants.IS_TESTING_ENVIRONMENT:
            self.reset_citorprofile_button = Button(self, text = 'Reset the Citor Profile', bd = '5', \
                                                                font=('calibre',12,'bold'), command = self.CitorProfile.reset_citor_profile_heatmap)
            self.reset_citorprofile_button.grid(row = row_count, column = 3,  columnspan = 1, rowspan=1, sticky = 'w', padx = padx_indent_level1, pady = pady_indent_level)  

            self.redraw_citorprofile_button = Button(self, text = 'Redraw the Citor Profile', bd = '5', \
                                                                font=('calibre',12,'bold'), command = self.CitorProfile.redraw_citor_profile_heatmap)
            self.redraw_citorprofile_button.grid(row = row_count, column = 4,  columnspan = 1, rowspan=1, sticky = 'w', padx = padx_indent_level1, pady = pady_indent_level)  
        
    def give_evaluation_text(self, event):                              
        message1 = "event widget name is: " + str(event.widget.name)        
        print(message1)        
        current_value = event.widget.get()
        if event.widget.name == "Prospectief": 
            self.ids.citor_info["prediction_and_evaluation"][self.ids.citor_info["patient_and_plan"]["PlanName"]]["Prospective"] = current_value
        elif event.widget.name =="Retrospectief":
            self.ids.citor_info["prediction_and_evaluation"][self.ids.citor_info["patient_and_plan"]["PlanName"]]["Retrospective"] = current_value

    def save_screenshot_citor_profile(self):
        # write away the evaluation data to the store. 
        self.ids.citor_info["prediction_and_evaluation"][self.ids.citor_info["patient_and_plan"]["PlanName"]]["Prospective"] = self.right_prospective_entry.get()
        self.ids.citor_info["prediction_and_evaluation"][self.ids.citor_info["patient_and_plan"]["PlanName"]]["Retrospective"]= self.right_retrospective_entry.get()
        update_external_citordata_datasource(self.ids)
        files = [('Tif', '*.tif'), 
            ('Png', '*.png')] 
        file = asksaveasfilename(title='save citor profile', filetypes=files, defaultextension=files, initialdir=SaveLocation.CITOR_SCREENSHOT_DIRECTORY)          
        if file !="":
            file_split_ext = path.split(file)
            file_split_ext = [path.join(file_split_ext[0], path.splitext(file_split_ext[1])[0]), path.splitext(file_split_ext[1])[1]]
            patientID = self.ids.patient_raystation_info_dict["Patient"].PatientID            
            mypath = path.abspath(file_split_ext[0] + "_patid_" + str(patientID) + "_planname_" + str(self.ids.patient_raystation_info_dict["Plan"].Name) + file_split_ext[1])
            self.figure.savefig(mypath, dpi='figure')
            print("Saved screenshot citor profile.")
 
#######################################################################################
#
# Radiation Dose Parameters, tab3		
#
#######################################################################################

class TabRadiationDose(Frame):    
    def __init__(self, master=None, ids = None, cnf={}, **kwargs):
        self.ids= ids        
        super().__init__(master, cnf, **kwargs)    

        # init parameters
        self.pady_indent_level= 5
        self.padx_indent_level1 = 10
        row_count = 0
        set_combobox_width = 20             

        self.rad_dose_label = Label(self,text="Radiation Dose Parameters",  font=('calibre',20,'bold'))
        self.rad_dose_label.grid(row = row_count, column = 0,  columnspan = 3, rowspan=2, sticky = 'w', padx = 10, pady = 20)  
        row_count +=2

        # table headers:
        set_header_font = ('calibre',12,'bold')
        header_labels = ["OAR citor","OAR NL HH","D_mean (Gy)", "V40 (fraction)","Volume (cm³)"]
        for i in range(len(header_labels)):
            column = Label(self,text=header_labels[i], font=set_header_font)            
            column.grid(row = row_count, column = i,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)    

        self.table_start_row = row_count
        # making the labels for the OAR NL HH:
        self.labeltext_dictionary_dose_parameters = {}
        for key, value in self.ids.citor_OAR_dict.items():
            row_count +=1            
            organ_label_citor_left = Label(self,text=key)
            organ_label_citor_left.grid(row = row_count, column = 0,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)             
            organ_label_nl_right = Label(self,text=value)
            organ_label_nl_right.grid(row = row_count, column = 1,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)                           
            self.labeltext_dictionary_dose_parameters[key]= {}
            # d_mean
            my_string_var_dmean = StringVar("")            
            self.labeltext_dictionary_dose_parameters[key]["Dmean_Gy"]= my_string_var_dmean
            organ_label_d_mean = Label(self,textvariable=my_string_var_dmean)            
            organ_label_d_mean.grid(row = row_count, column = 2,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)                         
            # V40_fraction            
            my_string_var_V40_fraction = StringVar("")            
            self.labeltext_dictionary_dose_parameters[key]["V40_fraction"]= my_string_var_V40_fraction
            organ_label_V40 = Label(self,textvariable=my_string_var_V40_fraction)            
            organ_label_V40.grid(row = row_count, column = 3,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)             
            # Volume           
            my_string_var_Volume = StringVar("")
            self.labeltext_dictionary_dose_parameters[key]["Volume_cm3"]= my_string_var_Volume
            organ_label_Volume_cm3 = Label(self,textvariable=my_string_var_Volume)            
            organ_label_Volume_cm3.grid(row = row_count, column = 4,  columnspan = 1, sticky = 'W', padx = self.padx_indent_level1, pady = self.pady_indent_level)    

        self.load_and_display_the_dose_parameters()

        if TestScriptsConstants.IS_TESTING_ENVIRONMENT:
            row_count +=2
            self.reload_button = Button(self, text = 'Herlaad de dosisparameters', bd = '5',  font=('calibre',12,'bold'), command = self.load_and_display_the_dose_parameters)
            self.reload_button.grid(row = row_count, column = 0,  columnspan = 2, rowspan=1, sticky = 'w', padx = self.padx_indent_level1, pady = self.pady_indent_level)

            # print the radiation_dose_parameters, for debugging purposes. 
            row_count +=1
            self.load_button = Button(self, text = 'Print radiation_dose_parameters', bd = '5',  font=('calibre',12,'bold'), command = self.print_radiation_dose_parameters_dict)
            self.load_button.grid(row = row_count, column = 0,  columnspan = 2, rowspan=1, sticky = 'w', padx = 10, pady = 20)

    def load_and_display_the_dose_parameters(self):
        # similar to create_radiation_dose_parameters_dict() of data_input module. 
        row_count = self.table_start_row
        for key in self.ids.citor_OAR_dict.keys():
            row_count +=1
            if isinstance(self.ids.radiation_dose_parameters_dict[key]["Dmean_Gy"], LambdaType):  
                self.labeltext_dictionary_dose_parameters[key]["Dmean_Gy"].set("")
            else:
                self.labeltext_dictionary_dose_parameters[key]["Dmean_Gy"].set("{:.2f}".format(round( 
                            self.ids.radiation_dose_parameters_dict[key]["Dmean_Gy"],
                            PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)))  
            if isinstance(self.ids.radiation_dose_parameters_dict[key]["V40_fraction"],LambdaType):
                self.labeltext_dictionary_dose_parameters[key]["V40_fraction"].set("")
            else:
                self.labeltext_dictionary_dose_parameters[key]["V40_fraction"].set("{:.3f}".format(round(
                            self.ids.radiation_dose_parameters_dict[key]["V40_fraction"], 
                            PredictorValueConstants.FRACTION_NUMBER_OF_DECIMALS)))                               
            if isinstance(self.ids.radiation_dose_parameters_dict[key]["Volume_cm3"],LambdaType):   
                self.labeltext_dictionary_dose_parameters[key]["Volume_cm3"].set("")
            else:                
                self.labeltext_dictionary_dose_parameters[key]["Volume_cm3"].set("{:.2f}".format(round(
                            self.ids.radiation_dose_parameters_dict[key]["Volume_cm3"], 
                            PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)))          

    def print_radiation_dose_parameters_dict(self):
        print("First print dictionary citor_available_OAR_dict")
        print_dictionary(self.ids.citor_OAR_dict)
        print("#############################################")
        print("#############################################")
        print("Then print dictionary radiation_dose_parameters")
        print_dictionary(self.ids.radiation_dose_parameters_dict)
