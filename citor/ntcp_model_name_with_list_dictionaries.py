# load the dictionaries: coefficients_per_ntcp_dict, predictors_per_ntcp_dict, 
def load_coefficients_per_ntcp_dict():
    coefficients_per_ntcp_dict = {
        "Mod-sev xerostomia": [
            "D0",
            "D4",
            "D5",
            "D3",
            "D2",
            "D1a",
            "D1b"
        ],
        "Sev xerostomia": [
            "E0",
            "E4",
            "E5",
            "E3",
            "E2",
            "E1a",
            "E1b"
        ],
        "Grade 2-4 xerostomia": [
            "F0",
            "F4",
            "F5",
            "F2",
            "F1"
        ],
        "Mod-sev sticky saliva": [
            "G0",
            "G2",
            "G3",
            "G1a",
            "G1b",
            "G1c"
        ],
        "Sev sticky saliva": [
            "H0",
            "H2",
            "H3",
            "H1a",
            "H1b",
            "H1c"
        ],
        "Grade 2-4 sticky saliva": [
            "I0",
            "I4",
            "I5",
            "I6",
            "I1",
            "I2",
            "I3"
        ],
        "Mod-sev loss of taste": [
            "J0",
            "J4",
            "J2",
            "J1",
            "J3"
        ],
        "Grade 2-4 loss of taste": [
            "K0",
            "K1",
            "K2",
            "K3"
        ],
        "Grade 2-4 dysphagia": [
            "B0",
            "B3",
            "B4",
            "B5",
            "B6",
            "B2a",
            "B2b",
            "B1a",
            "B1b",
            "B7a",
            "B7b",
            "B7c"
        ],
        "Grade 3-4 dysphagia": [
            "C0",
            "C3",
            "C4",
            "C5",
            "C6",
            "C2a",
            "C2b",
            "C1a",
            "C1b",
            "C7a",
            "C7b",
            "C7c"
        ],
        "Grade 2-4 aspiration": [
            "L0",
            "L2",
            "L1",
            "L3",
            "L4"
        ],
        "Mod-sev aspiration": [
            "M0",
            "M1a",
            "M1b",
            "M2"
        ],
        "Mod-sev hoarseness": [
            "N0",
            "N2",
            "N3",
            "N1"
        ],
        "Mod-sev speech problems": [
            "O0",
            "O3",
            "O4",
            "O1",
            "O2"
        ],
        "Mod-sev oral pain": [
            "P0",
            "P3",
            "P2",
            "P4",
            "P1"
        ],
        "Mod-sev throat pain": [
            "Q0",
            "Q2",
            "Q1a",
            "Q1b",
            "Q1c",
            "Q3",
            "Q4a",
            "Q4b"
        ],
        "Mod-sev jaw pain": [
            "R0",
            "R2",
            "R1a",
            "R1b"
        ],
        "Grade 2-4 weight loss": [
            "S0",
            "S1",
            "S2",
            "S3",
            "S4"
        ],
        "Mod-sev nausea and vomiting": [
            "T0",
            "T1",
            "T2",
            "T3",
            "T4"
        ],
        "Mod-sev fatigue": [
            "U0",
            "U1",
            "U2",
            "U3"
        ],
        "Grade 2-4 mucositis": [
            "V0",
            "V1"
        ],
        "Grade 3-4 mucositis": [
            "W0",
            "W2",
            "W1a",
            "W1b",
            "W1c"
        ]
    }     
    return coefficients_per_ntcp_dict

# following the toxicity outcome as in publication table 2. 
def load_predictors_per_ntcp_dict():
    predictors_per_ntcp_dict = {
            "Grade 2-4 dysphagia": [
            "Intercept",
            "OralCavity_Ext_Dmean",
            "PCM_Sup_Dmean",
            "PCM_Med_Dmean",
            "PCM_Inf_Dmean",
            "Dysphagia_baseline_Grade_2",
            "Dysphagia_baseline_Grade_35",
            "TumorSite_3cat_Pharynx",
            "TumorSite_Larynx",
            "TreatmentModality_Accelerated",
            "TreatmentModality_Chemoradiation",
            "TreatmentModality_Bioradiation"
        ],
        "Grade 3-4 dysphagia": [
            "Intercept",
            "OralCavity_Ext_Dmean",
            "PCM_Sup_Dmean",
            "PCM_Med_Dmean",
            "PCM_Inf_Dmean",
            "Dysphagia_baseline_Grade_2",
            "Dysphagia_baseline_Grade_35",
            "TumorSite_3cat_Pharynx",
            "TumorSite_Larynx",
            "TreatmentModality_Accelerated",
            "TreatmentModality_Chemoradiation",
            "TreatmentModality_Bioradiation"
        ],
        "Grade 2-4 aspiration": [
            "Intercept",
            "PharynxConst_Dmean_pwr3",
            "Aspiration_baseline_Grade_13",
            "Crico_Dmean",
            "Supraglottic_Dmean"
        ],
        "Mod-sev aspiration": [
            "Intercept",
            "Q38_baseline_Alittle",
            "Q38_baseline_Quiteabit_Verymuch",
            "PCM_Med_Dmean"
        ],
        "Mod-sev xerostomia": [
            "Intercept",
            "BuccalMucosa_Dmean_sum_log",
            "OralCavity_Ext_Dmean_sqrt",
            "Submandibulars_Dmean",
            "Parotids_Dmean_sum_sqrt",
            "Q41_baseline_Alittle",
            "Q41_baseline_Quiteabit_Verymuch"
        ],
        "Sev xerostomia": [
            "Intercept",
            "BuccalMucosa_Dmean_sum_log",
            "OralCavity_Ext_Dmean_sqrt",
            "Submandibulars_Dmean",
            "Parotids_Dmean_sum_sqrt",
            "Q41_baseline_Alittle",
            "Q41_baseline_Quiteabit_Verymuch"
        ],
        "Grade 2-4 xerostomia": [
            "Intercept",
            "OralCavity_Ext_Dmean_sqrt",
            "BuccalMucosa_Dmean_sum_log",
            "Parotids_Dmean_sum_sqrt",
            "Xerostomia_baseline_Grade_14"
        ],
        "Mod-sev sticky saliva": [
            "Intercept",
            "Submandibulars_Dmean",
            "Parotids_Dmean_sum_sqrt",
            "Q42_baseline_v2_Alittle_Verymuch",
            "Q42_baseline_Alittle",
            "Q42_baseline_Quiteabit_Verymuch"
        ],
        "Sev sticky saliva": [
            "Intercept",
            "Submandibulars_Dmean",
            "Parotids_Dmean_sum_sqrt",
            "Q42_baseline_v2_Alittle_Verymuch",
            "Q42_baseline_Alittle",
            "Q42_baseline_Quiteabit_Verymuch"
        ],
        "Grade 2-4 sticky saliva": [
            "Intercept",
            "IntegralDose",
            "OralCavity_Ext_Dmean_sqrt",
            "BuccalMucosa_Dmean_sum_log",
            "Submandibulars_Dmean",
            "OralCavity_Ext_Dmean",
            "Parotids_combined_Dmean"
        ],
        "Mod-sev loss of taste": [
            "Intercept",
            "OralCavity_Ext_Dmean_log",
            "OralCavity_Ext_Dmean_sqrt",
            "Age",
            "Parotids_Dmean_log"
        ],
        "Grade 2-4 loss of taste": [
            "Intercept",
            "Submandibulars_Dmean",
            "Parotids_Dmean_sum_sqrt",
            "OralCavity_Ext_Dmean_log"
        ],
        "Grade 2-4 mucositis": [
            "Intercept",
            "OralCavity_Ext_V40"
        ],
        "Grade 3-4 mucositis": [
            "Intercept",
            "OralCavity_Ext_Dmean",
            "TreatmentModality_Accelerated",
            "TreatmentModality_Chemoradiation",
            "TreatmentModality_Bioradiation"
        ],
        "Mod-sev hoarseness": [
            "Intercept",
            "GlotticArea_Dmean",
            "Arytenoids_Dmean",
            "TumorSite_2catv2_LarynxOrHypopharynx"
        ],
        "Mod-sev speech problems": [
            "Intercept",
            "Supraglottic_Dmean",
            "OralCavity_Ext_Dmean",
            "Speech_baseline",
            "TumorSite_Larynx"
        ],
        "Mod-sev oral pain": [
            "Intercept",
            "OralCavity_Ext_Dmean",
            "BuccalMucosas_combined_Dmean",
            "BuccalMucosa_high_Dmean_sqrt",
            "OralPain_baseline"
        ],
        "Mod-sev throat pain": [
            "Intercept",
            "Supraglottic_Dmean",
            "Q34_baseline_Alittle",
            "Q34_baseline_Quiteabit_Verymuch",
            "Q34_baseline_Quiteabit_Verymuch",
            "TumorSite_2cat_Oral_cavity",
            "TreatmentModality_AcceleratedORChemoradiation",
            "TreatmentModality_3cat_Bioradiation"
        ],
        "Mod-sev jaw pain": [
            "Intercept",
            "Mandible_Dmean",
            "Q32_baseline_Alittle",
            "Q32_baseline_Quiteabit_Verymuch"
        ],
        "Grade 2-4 weight loss": [
            "Intercept",
            "Weight_baseline",
            "Sex_Female",
            "PharynxConst_Dmean",
            "IntegralDose"
        ],
        "Mod-sev nausea and vomiting": [
            "Intercept",
            "NauseaVomiting_baseline",
            "Brain_Dmean",
            "IntegralDose",
            "BrainStem_Dmean"
        ],
        "Mod-sev fatigue": [
            "Intercept",
            "Fatigue_baseline",
            "IntegralDose",
            "Brain_Dmean"
        ],
    }
    return predictors_per_ntcp_dict

