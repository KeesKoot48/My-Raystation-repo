############################################################################
#
# Script to make a patient specific QA plan on your phantom
# The core functionality is in the module make_qa_plan. 
# The module psqa_gui generates the gui to let you make some choices. 
# By Kees Landheer, 2 april 2025.
#
############################################################################

from sys import exit
from System.Windows import MessageBox, MessageBoxButton, MessageBoxImage
from connect import get_current

from psqa_gui import MyRootWindow

def main():
    verification_plan_name = checks_before_rootwindow_launch()
    print("verification_plan_name " + verification_plan_name)
    app = MyRootWindow(verification_plan_name)
    app.mainloop()

def checks_before_rootwindow_launch():
    # check if a plan is selected:
    plan = get_current('Plan')

    verification_plan_name = "QA_" + get_current('Patient').Name
    # number of allowed characters is limited to 16.
    verification_plan_name = verification_plan_name[:16]
    if plan is None:
        message = "First select a plan and then launch the script."
        print(message)
        MessageBox.Show(message, "Warning", MessageBoxButton.OK,
                        MessageBoxImage.Error)
        exit("The script stops.")

    if len(plan.VerificationPlans) > 0:
        for i in range(len(plan.VerificationPlans)):
            if plan.VerificationPlans[i].BeamSet.DicomPlanLabel.startswith(verification_plan_name):
                message = "A QA plan with name " + \
                    verification_plan_name + " already exists. Please "
                message += " remove this plan before running the script. "
                print(message)
                MessageBox.Show(message, "Warning",
                                MessageBoxButton.OK, MessageBoxImage.Error)
                exit(message)

    return verification_plan_name

if __name__ == "__main__":
    main()
