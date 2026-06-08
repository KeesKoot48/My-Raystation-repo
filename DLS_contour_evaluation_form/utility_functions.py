########################################################################
#                                                                      #
# module for DLS contour evaluation by CT RTTs (and automated tagging).  
# Collection of functions that help with debugging and saving and loading 
# the dl_segmentation_data dictionary. 
# KeesLandheer
# January 19, 2026
# Python version 3.11
# version 1.0
#                                                                      #
########################################################################

from os import path
from json import load,loads, dump, JSONEncoder
from constants import TextFormatConstants, SaveLocation

import logging
logger = logging.getLogger(__name__)

def print_dictionary(dictionary):    
    for k, v in dictionary.items():
        if isinstance(v, dict):
            logger.info("{"+ "{0} :".format(k))
            print_dictionary(v)
        else:
            logger.info("{" + "{0} : {1}".format(k, v) + "}")

def print_dictionary_with_get(dictionary):    
    for k, v in dictionary.items():
        if isinstance(v, dict):
            logger.info("{"+ "{0} :".format(k))
            print_dictionary_with_get(v)
        elif isinstance(v, str) or isinstance(v, int):
            logger.info("{" + "{0} : {1}".format(k, v) + "}")
        else:
            # logger.info(f"De type of the value is: {type(v)}")
            # What is actually the v type in this case?: <class 'tkinter.StringVar'> <class 'tkinter.IntVar'>
            logger.info("{" + "{0} : {1}".format(k, v.get()) + "}")

def dump_dict_to_json_file(my_dict, patientid, caseuuid):
    filename = path.join(SaveLocation.DLS_JSON_DIRECTORY, "{}-{}.json".format(patientid, caseuuid))        
    try:
        with open(filename, "w", encoding="utf-8") as output_text_file:
            dump(my_dict, output_text_file, indent=TextFormatConstants.JSON_INDENT, cls=JSONEncoder)  
            
    except TypeError as e:
        # Happens if data contains non-serializable objects
        logger.info(f"Serialization error while dumping to json file: {e}")

    except OSError as e:
        # Covers file-related issues (permission denied, invalid path, etc.)
        logger.info(f"File error while dumping to json file: {e}")

    except Exception as e:
        # Catch-all for unexpected errors
        logger.info(f"Unexpected error  while dumping to json file: {e}")

def open_json_file_as_dict(patientid, caseuuid):
    my_dict = {}
    filename = path.join(SaveLocation.DLS_JSON_DIRECTORY, "{}-{}.json".format(patientid, caseuuid))
    if not path.isfile(filename):
        logger.info(f"There is no existing json file with {filename}.")
        return my_dict
    with open(filename) as json_file:
        try:
            my_dict = load(json_file)             
        except Exception as exception:
            logger.info(exception)                             
    if my_dict is None:
        logger.info(f"Loading the json with filename {filename} returned None.")
    return my_dict

