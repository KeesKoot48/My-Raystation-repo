#####################################################################################################
#
#   CREATION OF THE CITOR PROFILE HEATMAP. 
#
#####################################################################################################

from numpy import arange
import numpy.ma as ma
from matplotlib import ticker
from matplotlib.artist import Artist
from matplotlib.pyplot import gca


def create_heatmap_image(data, ax=None, **kwargs):
    if not ax:
        ax = gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)
    return im

# switch to an object with an update method to update the annotation text and color of an image heatmap. 
class Annotation():
    def __init__(self):
        # Normalize the threshold to the images color range.
        self.threshold = 50

        # Set default alignment to center (but allow it to be overwritten by textkw.)
        self.kw = dict(horizontalalignment="center",
                verticalalignment="center")                
        
        self.valfmt = ticker.StrMethodFormatter("{x:.0f}%")
        self.textcolors=("black", "white")    
        self.texts = []    

    def annotate_heatmap(self, im):
        # remove any annotation if present. 
        number_of_texts = len(im.axes.texts)

        if number_of_texts > 0:
            for i in range(number_of_texts):    
                # plot needs to be redrawn to make the remove visible. 
                Artist.remove(im.axes.texts[0])     

        self.data = im.get_array()
        """
        A function to annotate a heatmap.

        Parameters
        ----------
        im
            The AxesImage to be labeled.
        data
            Data used to annotate.  If None, the image's data is used.  Optional.
        valfmt
            The format of the annotations inside the heatmap.  This should either
            use the string format method, e.g. "$ {x:.2f}", or be a
            `matplotlib.ticker.Formatter`.  Optional.
        textcolors
            A pair of colors.  The first is used for values below a threshold,
            the second for those above.  Optional.
        threshold
            Value in data units according to which the colors from textcolors are
            applied.  If None (the default) uses the middle of the colormap as
            separation.  Optional.
        **textkw
            All other arguments are forwarded to each call to `text` used to create
            the text labels.
        """

        # Loop over the data and create a `Text` for each tile.
        # Change the text's color depending on the data.              
        for i in range(self.data.shape[0]):
            for j in range(self.data.shape[1]):
                my_data = ma.getdata(self.data)
                is_white = my_data[i, j] > self.threshold                
                self.kw.update(color=self.textcolors[int(is_white)])
                im.axes.text(j, i, self.valfmt(self.data[i, j], None), **self.kw)