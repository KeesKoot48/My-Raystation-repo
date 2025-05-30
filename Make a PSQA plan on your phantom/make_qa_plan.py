############################################################################
#
# Module of script to make a patient specific QA plan on your phantom
# This is basically an automation of methods available in Raystation:
# "New QA Plan", "Edit dose grid settings", "Final dose", "Export QA plan"
# By Kees Landheer, 2 april 2025.
# In line 16 and 17 you select your phantom setting its name and id (similar to a patient). 
############################################################################

from System.Windows import MessageBox, MessageBoxButton, MessageBoxImage 
from connect import get_current

def create_psqa_plan(verification_plan_name, isoc_name, exportfolder_path):    
    beam_set = get_current("BeamSet")
    isoc = beam_set.GetIsocenterData(Name=isoc_name)
    # create the QA plan.
    try:
        beam_set.CreateQAPlan(PhantomName="230222_Oct4D+1500MR",
                           PhantomId="230222xx0x",
                           QAPlanName=verification_plan_name,
                           IsoCenter={
                               'x': isoc["Position"]["x"], 'y': isoc["Position"]["y"], 'z': isoc["Position"]["z"]},
                           DoseGrid={'x': 0.2, 'y': 0.2, 'z': 0.2},
                           GantryAngle=None,
                           CollimatorAngle=None,
                           CouchRotationAngle=None,
                           ComputeDoseWhenPlanIsCreated=True,
                           DesiredStatisticalUncertaintyForElectrons=None,
                           MotionSynchronizationTechniqueSettings={'DisplayName': None,
                                                                   'MotionSynchronizationSettings': None,
                                                                   'RespiratoryIntervalTime': None,
                                                                   'RespiratoryPhaseGatingDutyCycleTimePercentage': None,
                                                                   'MotionSynchronizationTechniqueType': "Undefined"},
                           RemoveCompensators=False,
                           EnableDynamicTracking=False,
                           SetupBeamsSettings={'UseSetupBeams': False,
                                               'UseLocalizationPointAsSetupIsocenter': False,
                                               'UseUserSelectedIsocenterAsSetupIsocenter': False}
                           )
    except Exception as exc:        
        message = 'Errors for CreateQAPlan(): '
        print(message)        
        MessageBox.Show(exc.Message)

    # take resolution (voxel side), number of voxels and corner positions of grid. Take a resolution comparable to the measurement plate gridsize.
    for verificationplan in get_current('Plan').VerificationPlans:
        if verificationplan.BeamSet.DicomPlanLabel.startswith(verification_plan_name):
            # Corner is in cm: -26.3 (right left -> x), -18.1 (inf-sup -> z) and -25.3 (post-ant -> y)
            verificationplan.UpdateVerificationPlanDoseGrid(Corner={'x': -26.29719, 'y': -16.1, 'z': -18.1},
                                                            VoxelSize={
                                                                'x': 0.2, 'y': 0.2, 'z': 0.2},
                                                            NumberOfVoxels={'x': 264, 'y': 207, 'z': 181})

            verificationplan.BeamSet.ComputeDose(RunEntryValidation=True)

            # Save before export!
            get_current('Patient').Save()
            print("Dose grid adjusted and dose recalculated. Verification plan saved. ")
            
            try:
                verificationplan.ScriptableQADicomExport(ExportFolderPath= exportfolder_path,
                                                         QaPlanIdentity='Patient',
                                                         ExportExamination=False,
                                                         ExportExaminationStructureSet=False,
                                                         ExportBeamSet=True,
                                                         ExportRtRadiationSet=False,
                                                         ExportRtRadiations=False,
                                                         ExportBeamSetDose=True,
                                                         ExportBeamSetBeamDose=False,
                                                         IgnorePreConditionWarnings=False
                                                         )
            except SystemError as error:
                message = 'Errors were reported when exporting dicom plans. ' + error + 'Error exporting dicom file'
                print(message)
                MessageBox.Show(message, MessageBoxButton.OK, MessageBoxImage.Error)   
    message = "QA plan created and exported successfully."
    print(message)
    return message