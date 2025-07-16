from enum import Enum
from json import JSONEncoder

class SexPatient(Enum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    OTHER = 3

sex_dictionary = {"MALE": "Man", "FEMALE": "Vrouw", "UNKNOWN" : "onbekend", "OTHER": "onbekend"}

class TumorSite(Enum):
    # tumor site can actually be a combination of 1-5. 
    UNKNOWN = 0
    ORAL_CAVITY = 1
    OROPHARYNX = 2
    NASOPHARYNX = 3
    HYPOPHARYNX = 4
    LARYNX = 5

class TreatmentModality(Enum):
    UNKNOWN = 0
    CONVENTIONAL_RT = 1
    ACCELERATED_RT = 2
    CHEMORADIATION = 3
    RT_WITH_CETUXIMAB = 4

class BaselineToxicityPatient(Enum):
    UNKNOWN = 0
    NOT_AT_ALL = 1
    A_LITTLE = 2
    QUITE_A_BIT = 3
    VERY_MUCH = 4

class BaselineToxicityPhysician(Enum):
    UNKNOWN = 0
    GRADE_0 = 1
    GRADE_1 = 2
    GRADE_2 = 3
    GRADE_3 = 4
    GRADE_4 = 5

class PostOperative(Enum):
    UNKNOWN = 0
    NO = 1
    YES = 2

PUBLIC_ENUMS = {
    # values of all enums in citor_info.    
    "SexPatient" : SexPatient,
    "TumorSite" : TumorSite, 
    "TreatmentModality" : TreatmentModality,
    "PostOperative" : PostOperative,    
    "BaselineToxicityPatient" : BaselineToxicityPatient, 
    "BaselineToxicityPhysician" : BaselineToxicityPhysician    
}


class EnumEncoder(JSONEncoder):
    def default(self, obj, replace_dict):   
        # json Encoder kan omgaan met dict, maar geeft problemen als er in het dict objecten (bijv Enum) zitten. 
        if (isinstance(obj, dict)):    
            for k, v in obj.items():    
                if (isinstance(v, dict)):   
                    # set key k to temp_dict. 
                    replace_dict[k] = {}
                    replace_dict[k]= EnumEncoder.default(self, v, replace_dict[k])
                else:
                    if type(v) in PUBLIC_ENUMS.values():            
                        replace_dict[k] = {"__enum__": str(v)}
                    else:
                        replace_dict[k]=str(v)
            return replace_dict
        return JSONEncoder.default(self, obj)

# Enum dict decoder.  
# convert __enum__ keys in dictionary to real enums. 
def convert_enum_dict_to_enum(my_dict, replace_dict):
    for k, v in my_dict.items():    
        if (isinstance(v, dict) and "__enum__" in v.keys()):
            # an enum is converted to 1 dictionary.  
            name, member = v["__enum__"].split(".")            
            replace_dict[k] = getattr(PUBLIC_ENUMS[name], member)       
        elif (isinstance(v, dict)):
            replace_dict[k] = {}
            replace_dict[k]=convert_enum_dict_to_enum(v, replace_dict[k])
        else:    
            replace_dict[k]=v
    return replace_dict 
   