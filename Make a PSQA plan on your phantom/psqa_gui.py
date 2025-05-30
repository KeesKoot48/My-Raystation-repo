############################################################################
#
# Script to plan a patient specific QA plan on the Octavius 4D phantom.
# By Kees Landheer, 2 april 2025.
#
############################################################################

from tkinter.filedialog import askdirectory
from tkinter.ttk import Combobox
from tkinter import Tk, Label, Message, Button, StringVar
from connect import get_current

import os
from make_qa_plan import create_psqa_plan

# launch a gui window.
# display qa plan info. (e.g. beam energies)
# select the isoc from a drop down.
# select the path for exporting the plan with a dialog.
class MyRootWindow(Tk):
    def __init__(self, verification_plan_name):
        super().__init__()
        self.verification_plan_name = verification_plan_name
        self.window_width = 400
        self.window_height = 600
        self.window_x = 400
        self.window_y = 200
        self.geometry('%dx%d+%d+%d' % (self.window_width,
                      self.window_height, self.window_x, self.window_y))
        self.title("Create a PSQA plan for Octavius 4D")
        self.config(bg="light blue")
        # collect info for the user.
        # the isoc name is necessary for the CreateQAPlan methode.
        self.list_of_isoc_names = []
        self.list_of_beam_energies = []
        for beamset in get_current('Plan').BeamSets:            
            for beam in beamset.Beams:
                self.list_of_beam_energies.append(beam.BeamQualityId)
                self.list_of_isoc_names.append(beam.Isocenter.Annotation.Name)
        self.list_of_isoc_names_unique = list(set(self.list_of_isoc_names))
        self.isoc_name = self.list_of_isoc_names_unique[0]
        # if list_of_isoc_names_unique longer than 1. I think this is very unlikely. So you can also give a warning in the event this happens.
        if len(self.list_of_isoc_names_unique) > 1:    
            message = "There are multiple isoc names. I will set the first one."
            print(message)

        message = "This script creates a PSQA plan on the Octavius 4D Phantom, "
        message += "the dose grid is set and the plan is exported in "
        message += "dicom format (rtplan, rtdose). "
        print(message)
        self.set_padx = 10
        self.set_pady = 10
        row_count = 0        
        self.text_label = Message(self, text=message, font=(
            'calibre', 10, 'normal'), width=self.window_width-3*self.set_padx, bg="light blue")
        row_span_message = 4
        self.text_label.grid(row=0, column=0,  columnspan=1, rowspan=row_span_message, sticky='nswe',
                            padx=self.set_padx, pady=self.set_pady)

        row_count += row_span_message + 1
        # the text in the window (take QA plan export window as example)
        paragraph_title = "QA plan information ---------------------------"
        paragraph_label = Label(self, text=paragraph_title, font=('calibre', 12, 'bold'), bg="light blue")
        paragraph_label.grid(row=row_count, column=0,  columnspan=4, rowspan=1, sticky='nw',
                            padx=self.set_padx+5, pady=self.set_pady)

        self.set_padx2 = 15
        self.set_pady2 = 0
        row_count +=1     
        # 27 positions for the left side.    
        qa_plan_name_label = Label(self, text="Patient:                    " + get_current('Patient').Name, font=('calibre', 10, 'normal'), bg="light blue")
        qa_plan_name_label.grid(row=row_count, column=0,  columnspan=1, rowspan=1, sticky='nw',
                            padx=self.set_padx2, pady=self.set_pady2)
        row_count +=1        
        patient_name_label = Label(self, text="Plan:                        " + get_current('Plan').Name, font=('calibre', 10, 'normal'), bg="light blue")
        patient_name_label.grid(row=row_count, column=0,  columnspan=1, rowspan=1, sticky='nw',
                            padx=self.set_padx2, pady=self.set_pady2)
        row_count +=1
        beam_set_name_label = Label(self, text="Beam set:                 " + get_current('BeamSet').DicomPlanLabel, font=('calibre', 10, 'normal'), bg="light blue")
        beam_set_name_label.grid(row=row_count, column=0,  columnspan=1, rowspan=1, sticky='nw',
                            padx=self.set_padx2, pady=self.set_pady2)
        row_count +=1        
        phantom_name_label = Label(self, text="Phantom:                  230222_Oct4D+1500MR", font=('calibre', 10, 'normal'), bg="light blue")
        phantom_name_label.grid(row=row_count, column=0,  columnspan=1, rowspan=1, sticky='nw',
                            padx=self.set_padx2, pady=self.set_pady2)
        row_count +=1 
        energy_label_text = ", ".join(str(item) for item in self.list_of_beam_energies)
        energy_label_text +=  " MV. "       
        bundel_energie_label = Label(self, text="Beam energies:      " + energy_label_text, font=('calibre', 10, 'normal'), bg="light blue")
        bundel_energie_label.grid(row=row_count, column=0,  columnspan=1, rowspan=1, sticky='nw',
                            padx=self.set_padx2, pady=self.set_pady2)

        row_count +=4
        message = "Which isoc do you want to use for the QA plan? "
        isoc_name_label = Label(self, text=message, font=('calibre', 12, 'bold'), bg="light blue")
        isoc_name_label.grid(row=row_count, column=0,  columnspan=1, rowspan=1, sticky='nw',
                            padx=self.set_padx2, pady=self.set_pady)
        row_count +=1
        self.set_isoc_names_combobox_width = 30
        self.isoc_names_combobox_text= StringVar(self, self.isoc_name)                
        self.isoc_names_combobox = Combobox(self, width = self.set_isoc_names_combobox_width, textvariable = self.isoc_names_combobox_text, font=('calibre',10,'normal'))                 
        self.isoc_names_combobox.name = "isoc names combobox"
        self.isoc_names_combobox["values"] = self.list_of_isoc_names_unique
        self.isoc_names_combobox.grid(row = row_count, column = 0,  columnspan = 1, rowspan=1, sticky = 'nswe',\
                                padx = self.set_padx*4, pady = 10)
        
        row_count +=4
        message = "Choose a folder for the qa plan export: "
        choose_folder_label = Label(self, text=message, font=('calibre', 12, 'bold'), bg="light blue")
        choose_folder_label.grid(row=row_count, column=0,  columnspan=1, rowspan=1, sticky='nw',
                            padx=self.set_padx2, pady=self.set_pady)
        row_count +=1
        self.select_folder_button = Button(self, text="...", command=self.callback_set_export_folder)
        self.select_folder_button.grid(row = row_count, column = 0,  columnspan = 1, rowspan=1, sticky = 'nw',\
                                padx = self.set_padx2, pady = self.set_pady)
        row_count +=1
        self.export_folder_path_text = StringVar(self, "")
        self.export_folder_label = Label(self, textvariable=self.export_folder_path_text, wraplength=300, font=('calibre', 10, 'normal'), bg="white")
        self.export_folder_label.grid(row=row_count, column=0,  columnspan=1, rowspan=2, sticky='nswe',
                            padx=self.set_padx2, pady=self.set_pady*2)
        
        row_count +=2
        # put a start button and get the current input values.
        self.start_button = Button(self, text="Start", command=self.callback_collect_input)
        self.start_button.grid(row = row_count, column = 0,  columnspan = 1, rowspan=1, sticky = 'nw',\
                                padx = self.set_padx2, pady = self.set_pady)
        row_count +=1
        self.completion_text = StringVar(self, "")
        self.completion_label = Label(self, textvariable=self.completion_text, wraplength=300, font=('calibre', 10, 'normal'), bg="white")
        self.completion_label.grid(row=row_count, column=0,  columnspan=1, rowspan=2, sticky='nswe',
                            padx=self.set_padx2, pady=self.set_pady*2)

    def callback_set_export_folder(self, event=''):
        self.export_path_name = None
        while (self.export_path_name is None):
            self.export_path_name = askdirectory(parent=self, title='Dicom Export folder', mustexist=True, initialdir= os.path.expanduser('~'))
            self.export_folder_path_text.set(self.export_path_name)
            print("set label export folder: " + self.export_path_name)

    def callback_collect_input(self, event=''):
        # collect the isocname and the path
        self.isoc_name = self.isoc_names_combobox_text.get()
        print("isoc name " + self.isoc_name)
        print("export folder: " + self.export_path_name)
        print("input confirmed")
        self.completion_text.set(create_psqa_plan(self.verification_plan_name, self.isoc_name, self.export_path_name))