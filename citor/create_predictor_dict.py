#############################################################################################
#
#               COMPUTE PREDICTOR VALUES (DERIVED FROM MULTIPLE INPUTS)
#
#############################################################################################

from numpy import nextafter
from math import log, sqrt, pow

# custom
from enum_module import BaselineToxicityPhysician, BaselineToxicityPatient,\
     SexPatient, TumorSite, TreatmentModality
from constants import PredictorValueConstants
from utilities import set_values_with_lambda_function_to_zero

# NOTA BENE: If a roi is not available, the (corresponding) predictor value is set to zero. 
def create_predictor_dictionary(ids):
    # initialize
    predictor_dict = {}
    eps = nextafter(0, 1)

    # create a local radiation_dose_parameters_dict, and set all the lambda function to zero. 
    # there is a difference between having a value of 0 or of lambda. Therefore I do not convert ids.radiation_dose_parameters_dict here. 
    temp_radiation_dose_parameters_dict = set_values_with_lambda_function_to_zero(ids.radiation_dose_parameters_dict, {})
   
    # Predictor naming and order as in citor example patient excel.
    # Age: 57    
    predictor_dict["Age"]= int(ids.citor_info["patient_characteristics"]["Age_in_years"])
    # Arytenoids_Dmean: 29,02    
    predictor_dict["Arytenoids_Dmean"]= float(temp_radiation_dose_parameters_dict["Arytenoids"]["Dmean_Gy"])
    # Aspiration baseline_dict Grade 1-3: 0
    predictor_dict["Aspiration_baseline_Grade_13"]= int(not(ids.citor_info["baseline"]["PhR_aspiration"] == BaselineToxicityPhysician.GRADE_0))    
    # Brain_Dmean: 3,00    
    predictor_dict["Brain_Dmean"]=float(temp_radiation_dose_parameters_dict["Brain"]["Dmean_Gy"])
    # BrainStem_Dmean	11,45
    predictor_dict["BrainStem_Dmean"]=float(temp_radiation_dose_parameters_dict["Brainstem"]["Dmean_Gy"])
    # BuccalMucosa_Dmean	39,78    
    predictor_dict["BuccalMucosas_combined_Dmean"] = round((float(temp_radiation_dose_parameters_dict["Buccalmucosa left"]["Dmean_Gy"])+float(temp_radiation_dose_parameters_dict["Buccalmucosa right"]["Dmean_Gy"]))/2.0,PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)            
    # BuccalMucosa_Dmean_sum_log	7,25
    if not(float(temp_radiation_dose_parameters_dict["Buccalmucosa left"]["Dmean_Gy"])< eps and float(temp_radiation_dose_parameters_dict["Buccalmucosa right"]["Dmean_Gy"]) < eps):
        predictor_dict["BuccalMucosa_Dmean_sum_log"] = round(log(float(temp_radiation_dose_parameters_dict["Buccalmucosa left"]["Dmean_Gy"]))+\
            log(float(temp_radiation_dose_parameters_dict["Buccalmucosa right"]["Dmean_Gy"])),PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)
        # BuccalMucosa_high_Dmean_sqrt	7,327346041
        isBuccalmucosaLeftDmeanGreaterThanRight = float(temp_radiation_dose_parameters_dict["Buccalmucosa left"]["Dmean_Gy"]) > float(temp_radiation_dose_parameters_dict["Buccalmucosa right"]["Dmean_Gy"])
        predictor_dict["BuccalMucosa_high_Dmean_sqrt"] = round(sqrt(int(isBuccalmucosaLeftDmeanGreaterThanRight)* float(temp_radiation_dose_parameters_dict["Buccalmucosa left"]["Dmean_Gy"]) + \
            int(not(isBuccalmucosaLeftDmeanGreaterThanRight))* float(temp_radiation_dose_parameters_dict["Buccalmucosa right"]["Dmean_Gy"])), PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)    
    else: 
        predictor_dict["BuccalMucosa_Dmean_sum_log"] = 0
        predictor_dict["BuccalMucosa_high_Dmean_sqrt"] =0
    
    # Crico_Dmean	20,32    
    predictor_dict["Crico_Dmean"]=float(temp_radiation_dose_parameters_dict["Cricopharyngealinletmuscle"]["Dmean_Gy"])
    # Dysphagia baseline_dict Grade 2	1: 
    predictor_dict["Dysphagia_baseline_Grade_2"] = int((ids.citor_info["baseline"]["PhR_dysphagia"] == BaselineToxicityPhysician.GRADE_2))
    # Dysphagia baseline_dict Grade 3-5	0
    predictor_dict["Dysphagia_baseline_Grade_35"] = int((ids.citor_info["baseline"]["PhR_dysphagia"] == BaselineToxicityPhysician.GRADE_3) or (ids.citor_info["baseline"]["PhR_dysphagia"] == BaselineToxicityPhysician.GRADE_4))        
    # Fatigue baseline_dict	66,66666667    
    predictor_dict["Fatigue_baseline"] = round(((ids.citor_info["baseline"]["Q10_rest_needed"].value + ids.citor_info["baseline"]["Q12_feeling_weak"].value + ids.citor_info["baseline"]["Q18_tired"].value)/3-1)/3*100,PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)        
    # Sex Female	0
    predictor_dict["Sex_Female"] = int(ids.citor_info["patient_characteristics"]["Patient_sex"] == SexPatient.FEMALE)
    # Weight baseline_dict	110,8    
    predictor_dict["Weight_baseline"]=float(ids.citor_info["patient_characteristics"]["Weight_in_kg"])
    # GlotticArea_Dmean	31,28    
    predictor_dict["GlotticArea_Dmean"]=float(temp_radiation_dose_parameters_dict["Glotticarea"]["Dmean_Gy"])
    # IntegralDose	230409,368
    predictor_dict["IntegralDose"] = round(float(temp_radiation_dose_parameters_dict["Bodycontour"]["Dmean_Gy"])*float(temp_radiation_dose_parameters_dict["Bodycontour"]["Volume_cm3"]),PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)
    # TumorSite_2cat Larynx	0
    # TumorSite_3cat Larynx	0;WAT VOEGT DIT TOE TOV # TumorSite_2cat Larynx
    # predictor_dict["TumorSite_2cat_Larynx"]=pred_TumorSite_Larynx
    # predictor_dict["TumorSite_3cat_Larynx"]=pred_TumorSite_Larynx
    predictor_dict["TumorSite_Larynx"]= int(ids.citor_info["patient_characteristics"]["TumorSite"] == TumorSite.LARYNX)    	    
    # TumorSite_2cat Oral cavity	0
    predictor_dict["TumorSite_2cat_Oral_cavity"]= int(ids.citor_info["patient_characteristics"]["TumorSite"] == TumorSite.ORAL_CAVITY)       
    # TumorSite_2catv2 Larynx/Hypopharynx 	0
    predictor_dict["TumorSite_2catv2_LarynxOrHypopharynx"]= int((ids.citor_info["patient_characteristics"]["TumorSite"] == TumorSite.LARYNX) or \
        (ids.citor_info["patient_characteristics"]["TumorSite"] == TumorSite.HYPOPHARYNX))               
    # TumorSite_3cat Pharynx	1
    predictor_dict["TumorSite_3cat_Pharynx"]= int((ids.citor_info["patient_characteristics"]["TumorSite"] == TumorSite.NASOPHARYNX) or \
        (ids.citor_info["patient_characteristics"]["TumorSite"] == TumorSite.OROPHARYNX) or \
        (ids.citor_info["patient_characteristics"]["TumorSite"] == TumorSite.HYPOPHARYNX))
    # Mandible_Dmean	39,67
    predictor_dict["Mandible_Dmean"]=float(temp_radiation_dose_parameters_dict["Mandible"]["Dmean_Gy"])
    # TreatmentModality Accelerated	1
    predictor_dict["TreatmentModality_Accelerated"] = int(ids.citor_info["patient_characteristics"]["TreatmentModality"] == TreatmentModality.ACCELERATED_RT)
    # TreatmentModality Bioradiation	0
    predictor_dict["TreatmentModality_Bioradiation"]= int(ids.citor_info["patient_characteristics"]["TreatmentModality"] == TreatmentModality.RT_WITH_CETUXIMAB)
    # TreatmentModality Chemoradiation	0
    predictor_dict["TreatmentModality_Chemoradiation"] = int(ids.citor_info["patient_characteristics"]["TreatmentModality"] == TreatmentModality.CHEMORADIATION)
    # TreatmentModality_3cat Accelerated RT or chemoradiation	1
    predictor_dict["TreatmentModality_AcceleratedORChemoradiation"] = int((ids.citor_info["patient_characteristics"]["TreatmentModality"] == TreatmentModality.ACCELERATED_RT) or\
        ids.citor_info["patient_characteristics"]["TreatmentModality"] == TreatmentModality.CHEMORADIATION)
    # TreatmentModality_3cat_Bioradiation	0    
    predictor_dict["TreatmentModality_3cat_Bioradiation"] = int(ids.citor_info["patient_characteristics"]["TreatmentModality"] == TreatmentModality.RT_WITH_CETUXIMAB)    
    # NauseaVomiting_baseline	33,33333333    
    predictor_dict["NauseaVomiting_baseline"] = round(((ids.citor_info["baseline"]["Q14_nauseated"].value + ids.citor_info["baseline"]["Q15_vomiting"].value)/2-1)/3*100,PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)    
    # OralCavity_Ext_Dmean	48,95
    predictor_dict["OralCavity_Ext_Dmean"]=float(temp_radiation_dose_parameters_dict["Oralcavity"]["Dmean_Gy"])
    # OralCavity_Ext_Dmean_log	3,890799369
    if (float(temp_radiation_dose_parameters_dict["Oralcavity"]["Dmean_Gy"])>0):
        predictor_dict["OralCavity_Ext_Dmean_log"] = round(log(float(temp_radiation_dose_parameters_dict["Oralcavity"]["Dmean_Gy"])),PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)
    else:
        predictor_dict["OralCavity_Ext_Dmean_log"] = 0
    # OralCavity_Ext_Dmean_sqrt	6,99642766
    predictor_dict["OralCavity_Ext_Dmean_sqrt"] = round(sqrt(float(temp_radiation_dose_parameters_dict["Oralcavity"]["Dmean_Gy"])),PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)    
    # OralCavity_Ext_V40	0,745    
    predictor_dict["OralCavity_Ext_V40"]=temp_radiation_dose_parameters_dict["Oralcavity"]["V40_fraction"]
    # OralPain baseline_dict	83,33333333
    predictor_dict["OralPain_baseline"] = round(((ids.citor_info["baseline"]["Q31_mouth_pain"].value + ids.citor_info["baseline"]["Q33_mouth_soreness"].value)/2-1)/3*100,PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)
    # Parotids_Dmean	16,38
    predictor_dict["Parotids_combined_Dmean"] = round((float(temp_radiation_dose_parameters_dict["Parotidgland left"]["Dmean_Gy"])+float(temp_radiation_dose_parameters_dict["Parotidgland right"]["Dmean_Gy"]))/2,PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)
        # Parotids_Dmean_log	2,796061078
    if predictor_dict["Parotids_combined_Dmean"] >0 :
        predictor_dict["Parotids_Dmean_log"] = round(log(predictor_dict["Parotids_combined_Dmean"]),PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)
    else:
        predictor_dict["Parotids_Dmean_log"] = 0    
    
    # Parotids_Dmean_sum_sqrt	8,012364183
    predictor_dict["Parotids_Dmean_sum_sqrt"] = round(sqrt(float(temp_radiation_dose_parameters_dict["Parotidgland left"]["Dmean_Gy"]))+sqrt(float(temp_radiation_dose_parameters_dict["Parotidgland right"]["Dmean_Gy"])),PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)    
        # PCM_Inf_Dmean	26,58    
    predictor_dict["PCM_Inf_Dmean"]=float(temp_radiation_dose_parameters_dict["PCMinferior"]["Dmean_Gy"])
    # PCM_Med_Dmean	36,12
    predictor_dict["PCM_Med_Dmean"]=float(temp_radiation_dose_parameters_dict["PCMmiddle"]["Dmean_Gy"])
    # PCM_Sup_Dmean	53,79
    predictor_dict["PCM_Sup_Dmean"]=float(temp_radiation_dose_parameters_dict["PCMsuperior"]["Dmean_Gy"])
    # See mail of Lisa from january 11, 2024. Basically, it is a volume weighted sum. But we already have the roi Musc_Constrict available. 
    # PCM complete is a read out of our Raystation roi Musc_Constrict
    # I think the naming PharynxConst_Dmean of the citor study is confusing. See email of lisa. 
    # PharynxConst_Dmean	43,57
    predictor_dict["PharynxConst_Dmean"]= float(temp_radiation_dose_parameters_dict["PCMcomplete"]["Dmean_Gy"])
    # PharynxConst_Dmean_pwr3	82710,88729
    predictor_dict["PharynxConst_Dmean_pwr3"] = round(pow(predictor_dict["PharynxConst_Dmean"], 3),PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)    
    # Q32_baseline_Alittle	0
    predictor_dict["Q32_baseline_Alittle"] = int((ids.citor_info["baseline"]["Q32_jaw_pain"] == BaselineToxicityPatient.A_LITTLE))    
    # Q32 baseline_dict Quite a bit - very much	1
    predictor_dict["Q32_baseline_Quiteabit_Verymuch"] = int((ids.citor_info["baseline"]["Q32_jaw_pain"] == BaselineToxicityPatient.QUITE_A_BIT or ids.citor_info["baseline"]["Q32_jaw_pain"] == BaselineToxicityPatient.VERY_MUCH))    
    # Q34 baseline_dict v2 Quite a bit - very much	1
    # Q34 baseline_dict Quite a bit - very much	1
    predictor_dict["Q34_baseline_Quiteabit_Verymuch"] = int((ids.citor_info["baseline"]["Q34_throat_pain"] == BaselineToxicityPatient.QUITE_A_BIT or ids.citor_info["baseline"]["Q34_throat_pain"] == BaselineToxicityPatient.VERY_MUCH))    
    # Q34 baseline_dict A little	0
    predictor_dict["Q34_baseline_Alittle"] = int((ids.citor_info["baseline"]["Q34_throat_pain"] == BaselineToxicityPatient.A_LITTLE))    
    # Q38 baseline_dict A little	1
    predictor_dict["Q38_baseline_Alittle"] = int((ids.citor_info["baseline"]["Q38_choking"] == BaselineToxicityPatient.A_LITTLE))    
    # Q38 baseline_dict Quite a bit - very much	0
    predictor_dict["Q38_baseline_Quiteabit_Verymuch"] = int((ids.citor_info["baseline"]["Q38_choking"] == BaselineToxicityPatient.QUITE_A_BIT or ids.citor_info["baseline"]["Q38_choking"] == BaselineToxicityPatient.VERY_MUCH))    
    # Q41 baseline_dict A little	0
    predictor_dict["Q41_baseline_Alittle"] = int((ids.citor_info["baseline"]["Q41_dry_mouth"] == BaselineToxicityPatient.A_LITTLE))    
    # Q41 baseline_dict Quite a bit - very much	1
    predictor_dict["Q41_baseline_Quiteabit_Verymuch"] = int((ids.citor_info["baseline"]["Q41_dry_mouth"] == BaselineToxicityPatient.QUITE_A_BIT or ids.citor_info["baseline"]["Q41_dry_mouth"] == BaselineToxicityPatient.VERY_MUCH))    
    # Q42 baseline_dict v2 A little - very much	1
    predictor_dict["Q42_baseline_v2_Alittle_Verymuch"]= int((ids.citor_info["baseline"]["Q42_sticky_saliva"] == BaselineToxicityPatient.A_LITTLE or ids.citor_info["baseline"]["Q42_sticky_saliva"] == BaselineToxicityPatient.QUITE_A_BIT or ids.citor_info["baseline"]["Q42_sticky_saliva"] == BaselineToxicityPatient.VERY_MUCH))    
    # Q42 baseline_dict A little	0
    predictor_dict["Q42_baseline_Alittle"] = int((ids.citor_info["baseline"]["Q42_sticky_saliva"] == BaselineToxicityPatient.A_LITTLE))    
    # Q42 baseline_dict Quite a bit - very much	1
    predictor_dict["Q42_baseline_Quiteabit_Verymuch"] = int((ids.citor_info["baseline"]["Q42_sticky_saliva"] == BaselineToxicityPatient.QUITE_A_BIT or ids.citor_info["baseline"]["Q42_sticky_saliva"] == BaselineToxicityPatient.VERY_MUCH))    
    # Speech baseline_dict	16,66666667
    predictor_dict["Speech_baseline"] = round(((ids.citor_info["baseline"]["Q53_trouble_talking_to_people"].value + ids.citor_info["baseline"]["Q54_trouble_talking_on_phone"].value)/2-1)/3*100,PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)
    # Submandibulars_Dmean	59,35
    predictor_dict["Submandibulars_Dmean"] = round((float(temp_radiation_dose_parameters_dict["Submandibulargland left"]["Dmean_Gy"])+float(temp_radiation_dose_parameters_dict["Submandibulargland right"]["Dmean_Gy"]))/2,PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)
    # Supraglottic_Dmean 28,83    
    predictor_dict["Supraglottic_Dmean"]=float(temp_radiation_dose_parameters_dict["Supraglotticlarynx"]["Dmean_Gy"])
    # Xerostomia baseline_dict Grade 1-4	0
    predictor_dict["Xerostomia_baseline_Grade_14"] = int(not(ids.citor_info["baseline"]["PhR_xerostomia"] == BaselineToxicityPhysician.GRADE_0))            
    return predictor_dict