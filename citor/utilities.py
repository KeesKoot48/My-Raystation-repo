from types import LambdaType
from os import path
from json import load,loads, dump, JSONEncoder
from tkinter.filedialog import asksaveasfile, askopenfile

# custom
from enum_module import EnumEncoder, convert_enum_dict_to_enum
from constants import TextFormatConstants, SaveLocation

# unpacking dict, list, namedtuple and tuple. 
def unpack(obj):
    if isinstance(obj, dict):
        return {key: unpack(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [unpack(value) for value in obj]
    # elif isnamedtupleinstance(obj):
    #     return {key: unpack(value) for key, value in obj._asdict().items()}
    elif isinstance(obj, tuple):
        return tuple(unpack(value) for value in obj)
    else:
        return obj

def set_values_with_lambda_function_to_zero(my_dict, replace_dict):
    for k, v in my_dict.items():           
        if (isinstance(v, dict)):
            # set key k to temp_dict. 
            replace_dict[k] = {}
            replace_dict[k]= set_values_with_lambda_function_to_zero(v, replace_dict[k])
        else:
            if isinstance(v, LambdaType): 
                replace_dict[k]=0
            else:
                replace_dict[k]=v
    return replace_dict   


def remove_lambda_function_from_dict(my_dict, replace_dict):    
    # remove the keys with value lambda functions
    # WARNING: when you remove a key you get the error RuntimeError: dictionary changed size during iteration 
    for k, v in my_dict.items():           
        if (isinstance(v, dict)):
            # set key k to temp_dict. 
            replace_dict[k] = {}
            replace_dict[k]= remove_lambda_function_from_dict(v, replace_dict[k])
        else:
            if not(isinstance(v, LambdaType)): 
                replace_dict[k]=v
    return replace_dict                

# map dict_a in dict_b for the keys they have in common. 
def map_dicta_in_dictb(my_dicta, my_dictb):    
    for k, v in my_dicta.items():           
        if (isinstance(v, dict)):
            # set key k to temp_dict.             
            my_dictb[k]= map_dicta_in_dictb(v, my_dictb[k])
        else:            
            my_dictb[k]=v
    return my_dictb   

def is_json_function(myjson):
    try:
        json_object = loads(myjson)
    except ValueError as e:
        return False
    return True

def print_dictionary(dictionary):    
    for k, v in dictionary.items():
        if isinstance(v, dict):
            print("{"+ "{0} :".format(k))
            print_dictionary(v)
        else:
            print("{" + "{0} : {1}".format(k, v) + "}")

def dump_dict_to_json_file(my_dict, patientid):
    my_enum_encoder = EnumEncoder()
    my_citordata = my_enum_encoder.default(my_dict, {})   
    files = [('JSON', '*.json')]     
    output_file = asksaveasfile(mode= 'w', title='save citordata dict', filetypes=files, defaultextension=files,\
                         initialdir =SaveLocation.CITOR_INFO_JSON_DIRECTORY,\
                         initialfile = "citor_info_patid_" + str(patientid) + ".json")      
    if output_file is not None:
        dump(my_citordata, output_file, indent=TextFormatConstants.JSON_INDENT, cls=JSONEncoder)        

def dump_oar_radiation_dose_parameters_to_json_file(ids):
    files = [('JSON', '*.json')]     
    output_file = asksaveasfile(mode= 'w', title='Save OAR radiation dose parameters', filetypes=files, defaultextension=files,\
                         initialdir =SaveLocation.CITOR_INFO_JSON_DIRECTORY,\
                         initialfile = "citor_oar_radiation_dose_parameters_patid_" + str(ids.patient_raystation_info_dict["Patient"].PatientID) + ".json")      
    if output_file is not None:        
        my_dict = unpack(ids.radiation_dose_parameters_dict) 
        replace_dict = {}
        my_dict = remove_lambda_function_from_dict(my_dict, replace_dict)        
        dump(my_dict, output_file, indent=TextFormatConstants.JSON_INDENT)        

# e.g. used to open a citor_info.json file. 
def open_json_file(parent, title, default_dir=SaveLocation.CITOR_INFO_JSON_DIRECTORY):
    # TODO: remove 2 lines below: this is for testing. 
    # filename = path.join(default_dir, 'citor_info_new.json')
    # with open(filename, 'r') as my_json_file:
    my_json_file = askopenfile(parent=parent, mode='r', title=title, initialdir = default_dir, filetypes =[('JSON', '*.json')])
    if my_json_file is not None:
        try:
            my_dict = load(my_json_file) 
            my_dict = convert_enum_dict_to_enum(my_dict, {})                  
        except Exception as exception:
            print(exception)                 
            # messagebox.showwarning(title="Warning",message="Loading the citor info json file was not succesfull.")
            raise RuntimeError("No json file loaded.")    
    else:
        # e.g. if opening is canceled 
        return {}    
    return my_dict

# load the get_head_and_neck_oar_list.json used for the autoplanning. 
def get_head_and_neck_oar_list(writeToFile = False):
    head_and_neck_oar_list=[]
    fileName = path.join(path.dirname(__file__), "head_and_neck.json")        
    head_and_neck_oar_list = []
    with open(fileName) as json_file:
        data = load(json_file)
        for element in data:                
                for dictionarykey in element:                        
                    if (dictionarykey == "roilist"):
                        for index_dict in element[dictionarykey]:
                            for key in index_dict: 
                                if (key == "organtype") and (index_dict[key]== "OrganAtRisk"):
                                    # print("and the organ is: " + str(index_dict["name"]))
                                    head_and_neck_oar_list.append(index_dict["name"])

    if writeToFile:
        oar_filename = path.join(path.dirname(__file__), "oar_nl_raystation_head_and_neck.txt")   
        with open(oar_filename, 'w') as oar_txtfile:
            for organ in head_and_neck_oar_list:
                oar_txtfile.write(organ + '\n')  
                
    return head_and_neck_oar_list  