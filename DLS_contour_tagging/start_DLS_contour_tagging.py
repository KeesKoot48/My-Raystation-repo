########################################################################
#                                                                      #
# Main script for DLS contour evaluation by CT RTTs (and automated tagging).  
# KeesLandheer
# January 19, 2026
# Python versie 3.11
# versie 0.0 (demo and test version)
#                                                                      #
########################################################################

# (Fetch the initial visualisation state, where applicable.)
# (0. Load already scored data.)
# 1. Fetch the filled segmented structures. (ModelGeneratedRoiGeometries) 
# 2. Ask the CT RTT for every DLS roi a score for the segmentation quality. (Classification level 1 to 5, and an open text field for remarks.)
# 3. Ask for a general comment on the segmentation.
# 4. Store the scoring data (TODO).
# 5. Tag in database on patient level (TODO).  

# custom libraries:
from main_window import RootWindow

def main():
    mrw = RootWindow()
    mrw.mainloop()

if __name__ == "__main__":
  main()