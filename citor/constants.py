"""
Constants used by the citor package.
"""

class PredictorValueConstants:

    FLOAT_NUMBER_OF_DECIMALS = 2
    FLOAT_NUMBER_OF_DECIMALS_IN_HEATMAP = 2
    FRACTION_NUMBER_OF_DECIMALS = 3

class TestScriptsConstants:
    
    IS_RAYSTATION_ENVIRONMENT = [False,True][1]    
    IS_TESTING_ENVIRONMENT = [False,True][0]
    
class TextFormatConstants:

    JSON_INDENT = 4

class SaveLocation:

    CITOR_INFO_JSON_DIRECTORY = r'C:\\citor\\test\\'
    CITOR_SCREENSHOT_DIRECTORY = r'C:\\MyScreenshots\\'
    