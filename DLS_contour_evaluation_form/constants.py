"""
Constants used by the DLS_contour package.
"""
import System, clr
clr.AddReference('System.Drawing')

class SaveLocation:

    DLS_EXPORT_ROI_DIRECTORY = r"C:\DL_contouren"
    DLS_JSON_DIRECTORY = r"C:\DL_contouren\cache"
    
class DLS_Constants:
 
    ROI_DLS_COPY_LEADING = "_"
    ROI_DLS_COPY_SUFFIX = "__dls_tmp" 
    TEMP_ROI_COLOR = System.Drawing.Color.FromArgb(128, 128, 255)

class TextFormatConstants:

    JSON_INDENT = 4