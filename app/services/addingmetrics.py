import json

# Define the create_project function as before
def create_project(project_id, methodology, budget, duration, group_size):
    project = {
        "ProjectID": project_id,
        "Methodology": methodology,
        "Budget": budget,
        "Duration": duration,
        "GroupSize": group_size,
        "Expenditure": 0,
        "Stage": "Planning",
        "Moralerating": 0,
        "Difficultyrating": 0,
        "Communicationrating": 0,
        "New Spec": ""
    }
    return project
"""
Expenditure" <- if the sum goes over budget, increase the percentage by 28%
Moralerating <- rating is a floating number, subtract it from 10 and multiply it by 2.7%
Difficultyrating <- rating is a floating number, multiply it by 1.5%
Communicationrating <- rating is a floating number, subtract it from 10 and multiply it by 3.4%
New Spec <-  if a new spec is added then increase the chance of failure by 4.1% 
"""
def update_project(project, updates):
    for key, value in updates.items():
        if key == "Budget":
            expenditure = project["Expenditure"] + int(value)
            if expenditure > project["Budget"]:
                project["Probability of Failure"] += 28
            project[key] = int(value)
        elif key == "Duration" or key == "GroupSize":
            project[key] = int(value)
        elif key == "Methodology" or key == "Stage" or key == "New Spec":
            if key == "New Spec":
                project["Probability of Failure"] += 4.1
            project[key] = value
        elif key == "Expenditure":
            expenditure = project["Expenditure"] + int(value)
            if expenditure > project["Budget"]:
                project["Probability of Failure"] += 28
            project[key] += int(value)
        elif key == "Moralerating":
            project[key] = float(value)
            project["Probability of Failure"] -= (10 - float(value)) * 2.7
        elif key == "Difficultyrating":
            project[key] = float(value)
            project["Probability of Failure"] += float(value) * 1.5
        elif key == "Communicationrating":
            project[key] = float(value)
            project["Probability of Failure"] -= (10 - float(value)) * 3.4
    return project


# Read input data from a JSON file
with open("input_data.json", "r") as f:
    input_data = json.load(f)

# Create a list to store the new projects
projects = []

# Create new projects using the input data and the create_project function
for data in input_data:
    new_project = create_project(data["ProjectID"], data["Methodology"], data["Budget"], data["Duration"], data["GroupSize"])
    projects.append(new_project)

# Print the list of projects to verify that the new columns were added
print(projects)

"""
# Create a project
project = create_project("P001", "Agile", 100000, 6, 5)

# Update the project with user input
updates = {"Budget": "150000", "Duration": "9", "GroupSize": "7", "Stage": "Development", "Expenditure": "5000"}
updated_project = update_project(project, updates)

print(updated_project)
"""