#####################################################################################################
#
#   CREATION OF THE CITOR PROFILE (MATRIX). 
#
#####################################################################################################

# step 1: create a dictonary of a NTCP model name with list of tuples containing the predictor name and the corresponding coefficient name. 
# In this way we are able to pick the predictor and corresponding coefficient (for the models of all weeks).
# step 2: compute the inproduct for each ntcp model (per time point).  
# step 3: feed the improducts to the sigmoid function and compute the chance. 
# step 4: create the annotated heat map. 

from numpy import array, append, float32, dot, nan, empty, arange
from math import exp

from matplotlib.pyplot import gca, setp

# custom 
from create_predictor_dict import create_predictor_dictionary
from ntcp_model_name_with_list_dictionaries import load_coefficients_per_ntcp_dict, load_predictors_per_ntcp_dict
from citor_coefficient_values_dict import load_citor_coefficient_values_dictionary
from constants import PredictorValueConstants

from heatmap import create_heatmap_image, Annotation

# compute the sigmoid (give the chance as a percentage)
def sigmoid_perc(x):
    return round(1/(1+exp(-x))*100,PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS)

# step 1:
# load dictionaries with list of predictor names per ntcp model name and list of coefficient names per ntcp model name.
class CitorProfile:
    def __init__(self, ids, axes=None):        
        # constants
        self.ax = axes
        self.heatmap_image = None
        self.ids = ids
        self._predictors_per_ntcp_model_dict = load_predictors_per_ntcp_dict()
        self._coefficients_per_ntcp_model_dict = load_coefficients_per_ntcp_dict()
        self._ntcp_coefficient_dictionaries = load_citor_coefficient_values_dictionary()          
        self._x_time_point_list = self._ntcp_coefficient_dictionaries.keys()
        self._y_ntcp_model_names = self._predictors_per_ntcp_model_dict.keys()      
        self.citor_profile_array = self.initialize_citor_profile_array()
        self.create_heatmap_axes()
        self.annotation = Annotation()
        
    def initialize_citor_profile_array(self):
        # compute the size and file the array with nans. 
        citor_profile_array = empty([len(self._y_ntcp_model_names), len(self._x_time_point_list)])
        citor_profile_array.fill(nan)
        return citor_profile_array        
    
    def compute_citor_profile_array(self):    
        # make the data ready for plotting the heat map. 
        citor_profile_array_with_lists = []
        predictor_value_dict = create_predictor_dictionary(self.ids) 
        # check if all input is correct/usuble/as expected. 
        citor_profile_dict = {}
        for ntcp_model_name in self._y_ntcp_model_names:       
            ntcp_model_list = list(tuple(zip(self._predictors_per_ntcp_model_dict.get(ntcp_model_name),self._coefficients_per_ntcp_model_dict.get(ntcp_model_name))))
            coefficient_letter = self._coefficients_per_ntcp_model_dict.get(ntcp_model_name)[0][0]        
            ntcp_chance_vector =  array([])
            predictor_value_vector = array([],dtype=float)

            # load the predictor values per model. 
            for pred_coeff in ntcp_model_list:
                if pred_coeff[0]=="Intercept":
                    predictor_value_vector = append(predictor_value_vector, array([1.0]))
                else:                
                    predictor_value_vector = append(predictor_value_vector, predictor_value_dict.get(pred_coeff[0]))                
                
            # loop over all time points. 
            for key2 in self._ntcp_coefficient_dictionaries.keys():        
                coefficient_value_vector = array([],dtype=float32)
                all_models_coefficients_dict = self._ntcp_coefficient_dictionaries.get(key2)
                # get the coefficients starting with the coefficient letter of the ntcp model. 
                model_coefficients_dict = {key: value for key, value in all_models_coefficients_dict.items() if key.startswith(coefficient_letter)}
                # use the dictionaries to create two vectors: the predictor_value_vector and the coefficient_value vector. 
                coefficient_value_vector = append(coefficient_value_vector,array(list(model_coefficients_dict.values()), dtype=float32))
                coefficient_value_polynomial_sum = dot(predictor_value_vector, coefficient_value_vector)
                ntcp_chance = round(sigmoid_perc(coefficient_value_polynomial_sum), PredictorValueConstants.FLOAT_NUMBER_OF_DECIMALS_IN_HEATMAP)
                ntcp_chance_vector = append(ntcp_chance_vector, ntcp_chance)
            citor_profile_dict[ntcp_model_name]= list(tuple(zip(self._ntcp_coefficient_dictionaries.keys(), list(ntcp_chance_vector))))

        for values in citor_profile_dict.values():
            row_list = list(zip(*values))[1]
            citor_profile_array_with_lists.append(row_list)

        self.citor_profile_array = array(citor_profile_array_with_lists)


    def create_heatmap_axes(self):
        # row_labels, col_labels, ax=None
        """
        Create a heatmap from a numpy array and two lists of labels.

        Parameters
        ----------
        data
            A 2D numpy array of shape (N, M).
        row_labels
            A list or array of length N with the labels for the rows.
        col_labels
            A list or array of length M with the labels for the columns.
        ax
            A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
            not provided, use current axes or create a new one.  Optional.
        cbar_kw
            A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
        cbarlabel
            The label for the colorbar.  Optional.
        **kwargs
            All other arguments are forwarded to `imshow`.
        """

        if not self.ax:
            self.ax = gca()

        # We want to show all ticks...
        self.ax.set_xticks(arange(self.citor_profile_array.shape[1]))
        self.ax.set_yticks(arange(self.citor_profile_array.shape[0]))
        # ... and label them with the respective list entries.
        self.ax.set_xticklabels(self._x_time_point_list)
        headers_list = list(self._y_ntcp_model_names)
        # add headers on the left side (with row number in dict)
        citor_profile_headers_dict = {"Swallowing:        ":0, \
                                           "Salivary:          ":4,\
                                            "Mucosal:           ":12,\
                                            "Speech:           ":14,\
                                            "Pain:               ":16,\
                                            "General:        ":19}
        for key, row in citor_profile_headers_dict.items():
            headers_list[row]= key.upper() + headers_list[row]
            
        self.ax.set_yticklabels(headers_list)  # ,  weight='bold'

        # Let the horizontal axes labeling appear on top.
        self.ax.tick_params(top=True, bottom=False,
                    labeltop=True, labelbottom=False)

        # Rotate the tick labels and set their alignment.
        setp(self.ax.get_xticklabels(), rotation=-30, ha="right",
                rotation_mode="anchor")

        # Turn spines off and create white grid.
        self.ax.spines[:].set_visible(False)

        self.ax.set_xticks(arange(self.citor_profile_array.shape[1]+1)-.5, minor=True)
        self.ax.set_yticks(arange(self.citor_profile_array.shape[0]+1)-.5, minor=True)
        self.ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
        self.ax.tick_params(which="minor", bottom=False, left=False)

    def create_citor_profile_heatmap(self):         
        # compute the citor profile array. 
        self.compute_citor_profile_array()
        # Create colorbar, plot the heatmap image        
        self.heatmap_image = create_heatmap_image(self.citor_profile_array, ax=self.ax, cmap="Reds", vmin = 0, vmax = 100)
        self.annotation.annotate_heatmap(self.heatmap_image)
        cbar = self.ax.figure.colorbar(self.heatmap_image, ax=self.ax)
        cbarlabel="Complication chance [%]"
        cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
        self.ax.figure.canvas.draw_idle()
        # self.ax.set_title("Head and neck citor profile")        
        self.ax.figure.tight_layout()

    def plot_citor_profile_heatmap(self): 
        # function is called by functions below. 
        self.heatmap_image.set_data(self.citor_profile_array)
        self.annotation.annotate_heatmap(self.heatmap_image)     
        self.ax.figure.canvas.draw()             

    def reset_citor_profile_heatmap(self): 
        # initialize the citor profile array. 
        self.citor_profile_array = self.initialize_citor_profile_array()     
        self.plot_citor_profile_heatmap()  

    def redraw_citor_profile_heatmap(self):  
        self.compute_citor_profile_array()
        self.plot_citor_profile_heatmap()         




