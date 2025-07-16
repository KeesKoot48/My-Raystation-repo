from sys import exit
from collections import namedtuple
from json import loads

from tkinter import messagebox
from datetime import date

# custom
from citor.enum_module import BaselineToxicityPhysician, BaselineToxicityPatient,\
     SexPatient, TumorSite, TreatmentModality, PostOperative, convert_enum_dict_to_enum
from citor.constants import TestScriptsConstants, SaveLocation
from citor.utilities import dump_dict_to_json_file, open_json_file, \
    print_dictionary, map_dicta_in_dictb, is_json_function

from connect import get_current

try:
    Patient = get_current("Patient")
    Case = get_current("Case")
    Plan = get_current("Plan")
    BeamSet = get_current("BeamSet")
except:# SystemError:
    messagebox.showwarning(title="Warning",message="No patient, case, plan or beam set loaded. Look at the error stack.")  

class InputDataStructure:
    def __init__(self, rootwindow):	
        self.rootwindow = rootwindow        
        #################################################
        # initialize the dictionaries    
        #################################################
        self.set_verbose = 2
        self.weight_in_kg_init = -1
        self.citor_info_up_to_date = 1        
        self.patient_raystation_info_dict = {"Patient" : None, 
                                             "Patient_date_of_birth": None, 
                                             "Case": None, 
                                             "Plan": None,                                               
                                             "Beamset": None
                                            }        
        
        # TODO: replace "no roi available" with the name of your corresponding roi. 
        self.citor_OAR_dict = {"Arytenoids": "no roi available",\
                               "Bodycontour": "External",\
                               "Brain": "Brain",\
                               "Brainstem": "BrainStem",\
                               "Buccalmucosa left": "no roi available",\
                               "Buccalmucosa right":"no roi available",\
                               "Cricopharyngealinletmuscle": "Cricopharyngeus_Inlet",\
                               "Glotticarea": "Glottis",\
                               "Mandible":"Mandible",\
                               "Oralcavity": "OralCavity",\
                                "Parotidgland left": "Parotid_L",\
                               "Parotidgland right": "Parotid_R",\
                               "PCMinferior": "Musc_Constrict_I",\
                               "PCMmiddle": "Musc_Constrict_M",\
                               "PCMsuperior": "Musc_Constrict_S",\
                               "PCMcomplete" : "Musc_Constrict",\
                               "Submandibulargland left": "Submandibular_L",\
                               "Submandibulargland right": "Submandibular_R",\
                               "Supraglotticlarynx": "Larynx_SG"} 

        self.radiation_dose_parameters_dict = {}                          

        # gets information used in both self.patient_raystation_info_dict and self.citor_info        
        self.patient_raystation_info()

        if not TestScriptsConstants.IS_RAYSTATION_ENVIRONMENT:
            # add a field for the example patient. 
            Patient = namedtuple("Patient",["Name", "PatientID", "Gender"])
            Plan = namedtuple("Plan",["Name"])
            self.my_patient = Patient("anoniem", 99999999, "Other")
            self.my_plan = Plan("onbekend")
            self.patient_raystation_info_dict["Patient"]=self.my_patient
            self.patient_raystation_info_dict["Plan"]=self.my_plan    

        self.load_citor_info()                     
        self.create_radiation_dose_parameters_dict()

    def initalize_citor_info(self):
        self.citor_info = {"patient_characteristics":{}, "baseline": {}}  

        self.citor_info["patient_characteristics"]= {"Age_in_years": -1, 
                                                     "Patient_sex": SexPatient.UNKNOWN, 
                                                     "Weight_in_kg":self.weight_in_kg_init, 
                                                     "TumorSite":TumorSite.UNKNOWN, 
                                                     "TreatmentModality": TreatmentModality.ACCELERATED_RT, 
                                                     "PostOperative":PostOperative.NO
                                                     }
        
        self.citor_info["patient_and_plan"]={"Patient_ID" : self.patient_raystation_info_dict["Patient"].PatientID,
                                             "CaseName": self.patient_raystation_info_dict["Case"].CaseName,
                                             "CaseBodySite" : self.patient_raystation_info_dict["Case"].BodySite,
                                             "PlanName" : self.patient_raystation_info_dict["Plan"].Name,
                                             "BeamSetDicomPlanLabel" : self.patient_raystation_info_dict["Beamset"].DicomPlanLabel
                                             }
        self.citor_info["prediction_and_evaluation"]={}
        for plan in self.patient_raystation_info_dict["Case"].TreatmentPlans:
            # print(plan.Name)  
            self.citor_info["prediction_and_evaluation"][plan.Name]=lambda: "I am shared but immutable"   
            self.citor_info["prediction_and_evaluation"][plan.Name]= { 
                                    "number_no_roi_present" : 0,
                                    "Prospective" : "Denk je dat het model voor de verschillende toxiteiten een goede complicatiekans heeft berekend voor deze patient? Geef Enter na invullen.",
                                    "Retrospective" :"Invullen na afronding van de bestralingsbehandeling. En/Of pas na 2 jaar. Heeft \'t model voor de verschillende toxiteiten een goede complicatiekans berekend? Geef Enter na invullen."
                                    }

        # voeg de dss (decision support system: photons or protons) info ook toe aan de citor_info cache file. Dan kun je die file gebruiken voor je data mining. 
        self.citor_info["dssinfo"]= {}
        
        self.citor_info["baseline"] = {
                "Q31_mouth_pain": BaselineToxicityPatient.NOT_AT_ALL,
                "Q32_jaw_pain": BaselineToxicityPatient.NOT_AT_ALL,
                "Q33_mouth_soreness": BaselineToxicityPatient.NOT_AT_ALL,
                "Q34_throat_pain": BaselineToxicityPatient.NOT_AT_ALL,
                "Q38_choking": BaselineToxicityPatient.NOT_AT_ALL,
                "Q41_dry_mouth": BaselineToxicityPatient.NOT_AT_ALL,
                "Q42_sticky_saliva": BaselineToxicityPatient.NOT_AT_ALL,
                "Q53_trouble_talking_to_people": BaselineToxicityPatient.NOT_AT_ALL,
                "Q54_trouble_talking_on_phone": BaselineToxicityPatient.NOT_AT_ALL,
                "Q10_rest_needed": BaselineToxicityPatient.NOT_AT_ALL,
                "Q12_feeling_weak": BaselineToxicityPatient.NOT_AT_ALL,
                "Q14_nauseated": BaselineToxicityPatient.NOT_AT_ALL,
                "Q15_vomiting": BaselineToxicityPatient.NOT_AT_ALL,
                "Q18_tired": BaselineToxicityPatient.NOT_AT_ALL,
                "PhR_xerostomia": BaselineToxicityPhysician.GRADE_0,
                "PhR_dysphagia": BaselineToxicityPhysician.GRADE_0,
                "PhR_aspiration": BaselineToxicityPhysician.GRADE_0
        }
 
    def calculate_age(self):        
        if self.patient_raystation_info_dict["Patient_date_of_birth"] is None:
            return -1       
        today = date.today() 
        age_in_days = today - self.patient_raystation_info_dict["Patient_date_of_birth"]
        age_in_years = int(age_in_days.days/365.25)
        return age_in_years   

    def load_dssinfo_patient_and_baseline_into_citor_info(self):
        # dssinfo options from LIPP: PostOperative (ja/nee)
        postoperative_dict = {"ja": PostOperative.YES, "nee": PostOperative.NO}
        self.citor_info["patient_characteristics"]["PostOperative"]= postoperative_dict[self.citor_info["dssinfo"]["Po"]]
        # tumorlocation:"TumorSite":TumorSite.UNKNOWN, 
        # "Mondholte","Pharynx (oro, naso, hypo)","Larynx en Overige"
        # UNKNOWN = 0, ORAL_CAVITY = 1, OROPHARYNX = 2, NASOPHARYNX = 3, HYPOPHARYNX = 4, LARYNX = 5
        # I can copy: "Mondholte" and "Larynx en Overige"
        tumorsite_dict={"Mondholte":TumorSite.ORAL_CAVITY, "Larynx en Overige": TumorSite.LARYNX}
        if self.citor_info["dssinfo"]["Tuloc"] in tumorsite_dict.keys():
            self.citor_info["patient_characteristics"]["TumorSite"]= tumorsite_dict[self.citor_info["dssinfo"]["Tuloc"]]
        # Kan ik Blxer invullen bij: Have you had a dry mouth?
        # Blxer: "Helemaal niet","Een beetje","Nogal-heel erg"
        # UNKNOWN, NOT_AT_ALL, A_LITTLE, # QUITE_A_BIT = 3, VERY_MUCH = 4 cannot be retrieved from dssinfo. 
        # NOT_AT_ALL is the default. 
        if self.citor_info["dssinfo"]["Blxer"]=="Een beetje":
            self.citor_info["baseline"]["Q41_dry_mouth"]= BaselineToxicityPatient.A_LITTLE
        # Bldys: "Graad 0-1","Graad 2","Graad 3-4". 
        # 3 groups instead of 5. It is not possible to copy this. 

    def patient_raystation_info(self):        
        if not TestScriptsConstants.IS_RAYSTATION_ENVIRONMENT:            
            return

        self.patient_raystation_info_dict["Plan"] = Plan
        self.patient_raystation_info_dict["Patient"]= Patient
        self.patient_raystation_info_dict["Case"] =  Case               
        self.patient_raystation_info_dict["Beamset"] = BeamSet

    def load_citor_info(self):
        self.initalize_citor_info()    
        citor_info_dict = {}
        if TestScriptsConstants.IS_RAYSTATION_ENVIRONMENT:
            Patient = self.patient_raystation_info_dict["Patient"] 
            if Patient.DateOfBirth is not None:
                self.patient_raystation_info_dict["Patient_date_of_birth"]= date(Patient.DateOfBirth.Year, Patient.DateOfBirth.Month, Patient.DateOfBirth.Day)                        
            citor_info_dict = open_json_file(self.rootwindow, "Open the citor info.json", SaveLocation.CITOR_INFO_JSON_DIRECTORY)                              
            if TestScriptsConstants.IS_TESTING_ENVIRONMENT:                    
                is_okcancel = messagebox.askokcancel(title="Yes or No",message="Er bestaat in Ray station geen citorinfo voor deze patient. "+\
                                                    "Wilt u de citorinfo uit een json bestand laden?")                             
                if (is_okcancel):                    
                    # load the citor_info file. 
                    citor_info_dict = open_json_file(self.rootwindow, "Open the citor info.json", SaveLocation.CITOR_INFO_JSON_DIRECTORY)                          
        
        if citor_info_dict !={}: 
            # convert the __enum__ dicts to enums (if this has already been done, this does nothing)
            citor_info_dict = convert_enum_dict_to_enum(citor_info_dict, {})
            self.citor_info = map_dicta_in_dictb(citor_info_dict, self.citor_info)                             
            if is_json_function(self.patient_raystation_info_dict["Case"].Comments):                
                casecom = loads(self.patient_raystation_info_dict["Case"].Comments)
                dssinfo = casecom.get("dssinfo", None)
                if dssinfo is not None:
                    print("There is dssinfo available.")
                    self.citor_info["dssinfo"] = dssinfo
                    # self.load_dssinfo_patient_and_baseline_into_citor_info()

        if TestScriptsConstants.IS_RAYSTATION_ENVIRONMENT:
            Age_in_years = self.calculate_age()       
            Gender = SexPatient[Patient.Gender.upper()]
            if (int(self.citor_info["patient_characteristics"]["Age_in_years"]) !=Age_in_years):                                        
                print("the citor info json file is not up to date for age!")
                print("It is now updated from " + str(self.citor_info["patient_characteristics"]["Age_in_years"]) + " to " + str(Age_in_years))                    
                self.citor_info["patient_characteristics"]["Age_in_years"] = Age_in_years
            if (self.citor_info["patient_characteristics"]["Patient_sex"] != Gender):                                        
                print("the citor info json file is not up to date for Gender! :)")
                print(self.citor_info["patient_characteristics"]["Patient_sex"])                                        
                self.citor_info["patient_characteristics"]["Patient_sex"] = Gender
            if (self.citor_info["patient_and_plan"]["Patient_ID"] != Patient.PatientID):   
                # NB: Patient.PatientID in Raystation is a string:
                # is_string = isinstance(Patient.PatientID, str)            
                print("the citor info json file is not up to date for PatientID! :)")                                                      
                self.citor_info["patient_and_plan"]["Patient_ID"] = Patient.PatientID
            if (self.citor_info["patient_and_plan"]["CaseName"] != self.patient_raystation_info_dict["Case"].CaseName):                                        
                print("the citor info json file is not up to date for CaseName! :)")                                                      
                self.citor_info["patient_and_plan"]["CaseName"] = self.patient_raystation_info_dict["Case"].CaseName
            if (self.citor_info["patient_and_plan"]["CaseBodySite"] != self.patient_raystation_info_dict["Case"].BodySite):                                        
                print("the citor info json file is not up to date for CaseBodySite! :)")                                                      
                self.citor_info["patient_and_plan"]["CaseBodySite"] = self.patient_raystation_info_dict["Case"].BodySite
            if (self.citor_info["patient_and_plan"]["PlanName"] != self.patient_raystation_info_dict["Plan"].Name):                                        
                print("the citor info json file is not up to date for PlanName! :)")                                                          
                self.citor_info["patient_and_plan"]["PlanName"] = self.patient_raystation_info_dict["Plan"].Name
            if (self.citor_info["patient_and_plan"]["BeamSetDicomPlanLabel"] != self.patient_raystation_info_dict["Beamset"].DicomPlanLabel):                                        
                print("the citor info json file is not up to date for BeamSetDicomPlanLabel! :)")                                                      
                self.citor_info["patient_and_plan"]["BeamSetDicomPlanLabel"] = self.patient_raystation_info_dict["Beamset"].DicomPlanLabel
            if TestScriptsConstants.IS_TESTING_ENVIRONMENT:
                if not self.citor_info_up_to_date:                        
                    print("citor_info is not up to date.")
                    print("The patientID is: "+ str(Patient.PatientID))
                    is_okcancel = messagebox.askokcancel(title="Yes or No",message="Wilt u verversde citorinfo opslaan in het jsonbestand van deze patient?") 
                    if is_okcancel:
                        dump_dict_to_json_file(self.citor_info, Patient.PatientID) 
            print_dictionary(self.citor_info)   
            # breakpoint()

    #############################################################################################
    #
    #               RADIATION DOSE PARAMETERS
    #
    #############################################################################################

    def find_organs_at_risk(self):
        """
        Find all structures with OrganType "OrganAtRisk"
        and return a list
        :param: case: RS Case object
        :return: plan_oars: a list of organs at risk
        """
        # Declare return list
        plan_oars = []
        for r in self.patient_raystation_info_dict["Case"].PatientModel.RegionsOfInterest:
            if r.OrganData.OrganType == "OrganAtRisk":
                plan_oars.append(r.Name)
        return plan_oars
    
    # example dictionary code:
    # radiation_dose_parameters_dict = {
    #     "Arytenoids": {
    #         "Dmean_Gy": 29.02
    #     },
    #     "Body contour": {
    #         "Dmean_Gy": 9.8,
    #         "Volume_cm3": 23511.16
    #     },
    def initialize_radiation_dose_parameters_dict(self):
        self.radiation_dose_parameters_dict = {}                  
        self.radiation_dose_parameters = ["Dmean_Gy", "Volume_cm3", "V40_fraction"]     
        for key1 in self.citor_OAR_dict.keys():    
            self.radiation_dose_parameters_dict[key1]={}
            for key2 in self.radiation_dose_parameters:
                self.radiation_dose_parameters_dict[key1][key2]=lambda: "I am shared but immutable"   

    def create_radiation_dose_parameters_dict(self, is_json=False, radiation_dose_dict = None):
        self.initialize_radiation_dose_parameters_dict()
        if TestScriptsConstants.IS_RAYSTATION_ENVIRONMENT:    
            list_with_all_rois_of_current_plan = self.find_organs_at_risk()            
            for key, organ_at_risk in self.citor_OAR_dict.items():  
                if organ_at_risk == "no roi available":
                    continue
                if not(organ_at_risk in list_with_all_rois_of_current_plan):
                    message = "for organ at risk " + organ_at_risk + " no roi is present in the current plan"
                    print(message)     
                    print(message) 
                    organ_at_risk = "no roi present"  
                    # this overwrite works, because it is a primitive data type, a string. although we are iterating over the dictionary that I change here! I checked it.    
                    self.citor_OAR_dict[key] = organ_at_risk    
                    continue                 
                if self.patient_raystation_info_dict["Plan"].GetTotalDoseStructureSet().RoiGeometries[organ_at_risk].HasContours(): 
                    if key == "Bodycontour":             
                        try:
                            # GetRoiVolume returns a float with the volume in cm^3.   

                            self.radiation_dose_parameters_dict[key]["Volume_cm3"] = float(self.patient_raystation_info_dict["Plan"].GetTotalDoseStructureSet().RoiGeometries[organ_at_risk].GetRoiVolume())                  
                            if (self.set_verbose > 1):
                                print("The volume found is: " + "{:.2f}".format(self.radiation_dose_parameters_dict[key]["Volume_cm3"]))
                        except Exception as exception:
                            message_exception = "General exception: Volume of body contour not found. Check if a plan is selected in ray station. Set Volume_cm3_value to zero."                        
                            messagebox.showwarning(title="Warning from BodyContour picker",message=message_exception)                        
                            print(message_exception)
                            print(exception)
                            print(message_exception)                                    
                    if key == "Oralcavity":
                        try:
                            # the dosevalue in cGy 
                            self.radiation_dose_parameters_dict[key]["V40_fraction"] = float(self.patient_raystation_info_dict["Plan"].TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName=organ_at_risk, DoseValues=[4000.0])[0])   
                            if (self.set_verbose > 1):
                                print("The V40_fraction_value found is: " + "{:.3f}".format(self.radiation_dose_parameters_dict[key]["V40_fraction"]))
                        except Exception as exception:                        
                            message = "General exception: V40_fraction_value not found." 
                            messagebox.showwarning(title="Warning from V40 fraction value picker",message=message)                       
                            print(message)
                            print(exception)
                            print(message)
                                    
                    # for all organs at risk, get the D_mean. 
                    try:                        
                        # api says: The total dose of the treatment course. It is the sum of all EstimatedFractionDoseOnTotalDoseExamination in the treatment fraction list.
                        self.radiation_dose_parameters_dict[key]["Dmean_Gy"] =  float(self.patient_raystation_info_dict["Plan"].TreatmentCourse.TotalDose.GetDoseStatistic(RoiName = organ_at_risk,DoseType = "Average")/100)
                        if (self.set_verbose > 1):
                            print(organ_at_risk +" has Dmean_Gy_value: " + "{:.2f}".format(self.radiation_dose_parameters_dict[key]["Dmean_Gy"]))                        
                    except Exception as exception:
                        print(exception)
                        message = repr(exception)
                        messagebox.showwarning(title="Warning from Dmean picker",message=message)      
                        print(message)     
                else:
                    print("Roi " + str(organ_at_risk)+" has no contours.")
        else:    
            radiation_dose_dict = open_json_file(self.rootwindow, "Open the oar json", SaveLocation.CITOR_INFO_JSON_DIRECTORY)   
            if radiation_dose_dict is not None:
                for key, value_dict in radiation_dose_dict.items():
                    for key2, value in value_dict.items(): 
                        self.radiation_dose_parameters_dict[key][key2]=value
            # else:
            #     # Hard coding is also an option                        
            #     # dit zijn de waardes van de voorbeeld patient. Omdat dit in principe uit het plan moet komen wordt dit niet in de citor_info.json gestopt. 
            #     self.radiation_dose_parameters_dict["Arytenoids"]["Dmean_Gy"]= 29.02
            #     self.radiation_dose_parameters_dict["Bodycontour"]["Dmean_Gy"]=9.8
            #     self.radiation_dose_parameters_dict["Bodycontour"]["Volume_cm3"]=23511.16
            #     self.radiation_dose_parameters_dict["Brain"]["Dmean_Gy"]=3.0
            #     self.radiation_dose_parameters_dict["Brainstem"]["Dmean_Gy"]=11.45
            #     self.radiation_dose_parameters_dict["Buccalmucosa left"]["Dmean_Gy"]=53.69
            #     self.radiation_dose_parameters_dict["Buccalmucosa right"]["Dmean_Gy"]=26.26
            #     # self.radiation_dose_parameters_dict["Buccalmucosascombined"]["Dmean_Gy"]=39.78
            #     self.radiation_dose_parameters_dict["Cricopharyngealinletmuscle"]["Dmean_Gy"]=20.32
            #     self.radiation_dose_parameters_dict["Glotticarea"]["Dmean_Gy"]=31.28
            #     self.radiation_dose_parameters_dict["Mandible"]["Dmean_Gy"]=39.67
            #     self.radiation_dose_parameters_dict["Oralcavity"]["Dmean_Gy"]=48.95
            #     self.radiation_dose_parameters_dict["Oralcavity"]["V40_fraction"]=0.745
            #     self.radiation_dose_parameters_dict["Parotidgland left"]["Dmean_Gy"]=19.42
            #     self.radiation_dose_parameters_dict["Parotidgland right"]["Dmean_Gy"]=13.0
            #     # self.radiation_dose_parameters_dict["Parotidsglandscombined"]["Dmean_Gy"]=16.38
            #     self.radiation_dose_parameters_dict["PCMinferior"]["Dmean_Gy"]=26.58
            #     self.radiation_dose_parameters_dict["PCMmiddle"]["Dmean_Gy"]=36.12
            #     self.radiation_dose_parameters_dict["PCMsuperior"]["Dmean_Gy"]=53.79            
            #     self.radiation_dose_parameters_dict["PCMcomplete"]["Dmean_Gy"]=43.57
            #     self.radiation_dose_parameters_dict["Submandibulargland left"]["Dmean_Gy"]=59.35
            #     self.radiation_dose_parameters_dict["Submandibulargland right"]["Dmean_Gy"]=59.35
            #     self.radiation_dose_parameters_dict["Supraglotticlarynx"]["Dmean_Gy"]=28.83           

