#################################################################
# GUI Module of Citor Raystation script
# Python version 3.8
# Kees Landheer
# 23-11-2023
# script version 1.0
#################################################################

from tkinter import Label, Button, Tk
from tkinter.ttk import Notebook

# custom
from citor.tabs import TabCitorProfile, TabBasicInputAndBaseline, TabRadiationDose

class MyRootWindow(Tk):		
	def __init__(self):		
		super().__init__() 				
		self.window_width = 1000
		self.window_height = 1080
		self.window_x = 400
		self.window_y = 10
		self.geometry('%dx%d+%d+%d' % (self.window_width, self.window_height, self.window_x, self.window_y)) 
		self.title("Citor Hoofd Hals")		

class MyWindow(Notebook):
	def __init__(self, myrootwindow, ids):	
		self.ids = ids
		super().__init__(myrootwindow)
		# create a window with 3 tabs (with different background colors).  	
		self.tab_citor_profile = TabCitorProfile(self, self.ids, bg = "white")
		self.tab_basic_input_and_baseline = TabBasicInputAndBaseline(self, self.ids, citorprofile = self.tab_citor_profile.CitorProfile, bg= "dark green")				
		self.tab_radiation_dose_parameters = TabRadiationDose(self, self.ids, bg= "#fcba03")		
	
		self.add(self.tab_basic_input_and_baseline, text = "Basisgegevens")
		self.add(self.tab_citor_profile, text = "Citor Profile")
		self.add(self.tab_radiation_dose_parameters, text = "Dosis parameters")
		self.pack(expand = 1, fill ="both") 	

		padx_indent_level1 = 10
		padx_indent_level2 = 20
		pady_indent_level1= 5
		pady_indent_level2 = 20
		button_font_size = 12

		row_count = 28
		update_citor_info_label_left = Label(self.tab_basic_input_and_baseline,text="Wijziging gemaakt?: ", font=('calibre',button_font_size,'bold'))
		update_citor_info_label_left.grid(row = row_count, column = 0,  columnspan = 1, sticky = 'W', padx = padx_indent_level2, pady = pady_indent_level2*3)         

		tab_basic_input_update_citorprofile_button = Button(self.tab_basic_input_and_baseline, text = 'Sla citor basislijn op', bd = '5', \
																font=('calibre',button_font_size,'bold'), command = self.save_citor_profile)
		
		tab_basic_input_update_citorprofile_button.grid(row = row_count, column = 1,  columnspan = 1, rowspan=1, sticky = 'w', padx = padx_indent_level1, pady = pady_indent_level1)  

		self.bind("<<NotebookTabChanged>>", func=self.on_tab_selected)

	def save_citor_profile(self, event=''):
		self.select(1)

	def on_tab_selected(self, event):
		# Get the index of the selected tab
		selected_tab_index = self.index(self.select())
		
		# Perform any actions based on the selected tab
		if selected_tab_index == 1:
			print("CitorProfileTab selected")			 
			self.tab_basic_input_and_baseline.update_citor_info_callback()
			self.tab_citor_profile.CitorProfile.redraw_citor_profile_heatmap()