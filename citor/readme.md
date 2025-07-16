V 1.0   20240403 Kees Landheer.

With this package, you can make a Comprehensive Individual TOxicity Profile (Citor) for Head and Neck patients. 

The user fills in the basic patient and rt plan (4 items) information and answers the baseline questions (17 questions). 
The script fetches the necessary dose parameters of the organs at risk from the (selected) Ray Station plan. 
Then the NTCP Complication chance is computed and displayed in the (heatmap) profile for the 22 differentiated complications. 
The complication probability is given for 6 acute (3, 4, 5,6 and 7, 12 weeks) and 4 late (6,12,18,24 months after end of treatment) time points. 

The main module in this package is citor.py. 

The flow is as follows:
1. In tab Basisgegevens: Fill in the basic patient and rt plan elements (4 items) -> save data: "Sla citor basisgegevens op"
2. In tab Baseline: Answer the baseline questions (17 questions) -> save data: "Sla citor basislijn op"
3. "Herteken (redraw) het profiel" and assess the profile. 
4. Save screenshot of Citor Profile in *.tif. 

Dit is een voorbeeld Citor profiel ![Hoofd Hals Citor profiel](images/citor_profile_readme.tif)
