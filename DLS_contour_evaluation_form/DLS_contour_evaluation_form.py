########################################################################
#                                                                      #
# Main script for D(eep)L(earning)S(egmentation) contour evaluation form 
# fill in by CT RTTs  
# KeesLandheer
# January 19, 2026
# Python version 3.11
# version 1.0
#                                                                      #
########################################################################

# Fetch the initial visualisation state, where applicable.
# 0. Load already scored data from json.
# 1. Fetch the filled segmented contours (rois) and export them in a separate thread as Voxelroi (npz file). 
# 2. Ask the CT RTT for every DLS roi a score for the segmentation quality. (Classification level 1 to 4 for small (1), some (2), many (3) adjustments up to contour removed and redrawn(4), and an open text field for remarks.)
# 3. Ask for an overall comment on the segmentation.
# 4. Store the scoring data in the json.

# NB. Voxelrois can be imported in RayStation again for example with the script import_simple_voxel_roi.py in folder examples.
# This could be interesting if you want to export the structures to a DICOM RTSTRUCT, or if you want to convert them to Contour Sets or Triangle meshes. 
# Also, RayStation has a method to compute similarity coefficients. 

# custom libraries:
from main_window import RootWindow

def main():
    mrw = RootWindow()
    mrw.mainloop()

if __name__ == "__main__":
  main()