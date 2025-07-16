from connect import get_current
    
patient_db = get_current("PatientDB")

# fill in the name of a template you have in your raystation environment. 
template_name = 'R_prostate_70_35_C'

# load clinical goal template via patientDB
template = patient_db.LoadTemplateClinicalGoals(templateName=template_name,lockMode='Read')

for i in range(template.EvaluationSetups[0].EvaluationFunctions.Count):
    clinical_goal_dict = {}
    number_attribute = "_" + str(i)
    intermediate_object = getattr(template.FunctionToRoiMaps, number_attribute)   
    clinical_goal_dict['roiname'] = intermediate_object.OrganData.ResponseFunctionTissueName            
    goal = template.EvaluationSetups[0].EvaluationFunctions[i].PlanningGoal                
    clinical_goal_dict['acceptancelevel'] = goal.PrimaryAcceptanceLevel
    clinical_goal_dict['criteria'] = goal.GoalCriteria
    clinical_goal_dict['parametervalue'] = goal.ParameterValue        
    clinical_goal_dict['type'] = goal.Type
    clinical_goal_dict['priority'] = goal.Priority
    print(clinical_goal_dict)