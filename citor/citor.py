# THIS IS THE MAIN SCRIPT

#######################################################################
#
# CITOR is short for Comprehensive Individial TOxicity Risk Profile. This  
# implementation is based on the paper: Comprehensive toxicity risk profiling 
# in radiation therapy for head and neck cancer: A new concept for individually 
# optimised treatment by Lisa Van den Bosch et al., 2021. 
# This script shows a dashboard with acute and long term toxicity probabilities 
# for Head and Neck patients. The NTCP models used use the mean dose to various
# organs at risk and docter and patient questionnaires.  
#
# Python version 3.8
# Kees Landheer
# 23-11-2023
# script version 1.0
#######################################################################

# custom libraries:
from citor.data_input import InputDataStructure
from citor.mygui import MyWindow, MyRootWindow

def main():   
    mrw = MyRootWindow()    
    ids = InputDataStructure(mrw)

    # collect input data from patient/docter questionnaire via gui:    
    app = MyWindow(mrw, ids)

    mrw.mainloop()

# for testing: 
if __name__ == "__main__":
    main()