from redmine import Redmine
import json
from pprint import pprint
import getpass

#Config Goes Here
#=====================
REDMINE_URL="https://portal.optimusinfo.com/redmine"
PROJECT_NAME = "teamfituiwork"

# Variable declarations goes here.
input_issues = None
redmine_issues = None
sprint_issue_id = 50501

# Utility methods
#=================
def listAllIssues(parentIssueId):
    issue = redmine.issue.get(parentIssueId, include='children')
    print "-->Redmine issues"
    for item in issue.children:
        print item.subject
    return issue.children

def readInputFile(file_name):
    input_data = json_data=open(file_name).read()
    data = json.loads(json_data)
    print "-->Input issues"
    for item in data:
        print item["subject"]
    return data

def needsUpdate(redmine_issue, input_issue):
    needsUpdate=False

    keys = dict(redmine_issue).keys()
    if "tracker" in keys:
        if redmine_issue.tracker.id != input_issue["tracker_id"]:
            print "------>Tracker Id: " + str(redmine_issue.tracker.id) + " should update to " + str(input_issue["tracker_id"]) + "."
            needsUpdate=True
    else:
        print "------>Tracker Id: " + str(input_issue["tracker_id"]) + " needs to be added."
        needsUpdate=True

    if "description" in keys:
        if redmine_issue.description != input_issue["description"]:
            print "------>Description: " + str(redmine_issue.description) + " should update to " + str(input_issue["description"]) + "."
            needsUpdate=True
    else:
        print "------>Description: " + str(input_issue["description"]) + " needs to be added."
        needsUpdate=True

    if "status" in keys:
        if redmine_issue.status.id != input_issue["status_id"]:
            print "------>Status Id: " + str(redmine_issue.status.id) + " should update to " + str(input_issue["status_id"]) + "."
            needsUpdate=True
    else:
        print "------>Status Id: " + str(input_issue["status_id"]) + " needs to be added."
        needsUpdate=True

    if "assigned_to" in keys:
        if redmine_issue.assigned_to.id != input_issue["assigned_to_id"]:
            print "------>Assigned To Id: " + str(redmine_issue.assigned_to.id) + " should update to " + str(input_issue["assigned_to_id"]) + "."
            needsUpdate=True
    else:
        print "------>Assigned To Id: " + str(input_issue["assigned_to_id"]) + " needs to be added."
        needsUpdate=True

    if "done_ratio" in keys:
        if redmine_issue.done_ratio != input_issue["done_ratio"]:
            print "------>Done Ratio: " + str(redmine_issue.done_ratio) + " should update to " + str(input_issue["done_ratio"]) + "."
            needsUpdate=True
    else:
        print "------>Done Ratio: " + str(input_issue["done_ratio"]) + " needs to be added."
        needsUpdate=True
    return needsUpdate

def createIssueWithData(input_issue):
    new_issue = redmine.issue.new()
    new_issue.subject = input_issue["subject"]
    new_issue.tracker_id = input_issue["tracker_id"]
    new_issue.description = input_issue["description"]
    new_issue.status_id = input_issue["status_id"]
    new_issue.assigned_to_id = input_issue["assigned_to_id"]
    new_issue.done_ratio = input_issue["done_ratio"]
    new_issue.project_id = input_issue["project_id"]
    new_issue.parent_issue_id = input_issue["parent_issue_id"]
    return new_issue

def createUpdatedIssueWithData(input_issue, issue_id):
    updated_issue=redmine.issue.get(issue_id)
    updated_issue.subject = input_issue["subject"]
    updated_issue.tracker_id = input_issue["tracker_id"]
    updated_issue.description = input_issue["description"]
    updated_issue.status_id = input_issue["status_id"]
    updated_issue.assigned_to_id = input_issue["assigned_to_id"]
    updated_issue.done_ratio = input_issue["done_ratio"]
    updated_issue.project_id = input_issue["project_id"]
    updated_issue.parent_issue_id = input_issue["parent_issue_id"]
    return updated_issue

def createIssueList(redmine_issues, input_issues):
    issue_list = []
    print "-->Creating Issues"
    for input_issue in input_issues:
        flag=0
        for redmine_issue in redmine_issues:
            if input_issue["subject"] in redmine_issue.subject:
                # Issue exist in redmine. We need to update the issue.

                print "-->Issue " + input_issue["subject"] + " exists in Redmine."

                issue = redmine.issue.get(redmine_issue.id)
                if needsUpdate(issue, input_issue)==True:
                    print "-->Issue " + input_issue["subject"] + " needs update. Adding in issue list."
                    updated_issue=createUpdatedIssueWithData(input_issue, redmine_issue.id)
                    issue_list.append(updated_issue)
                flag=1
                break
        if flag==0:
            # Issue does not exist in redmine. We need to create a new one.

            print "-->Issue " + input_issue["subject"] + " does not exists in Redmine. Adding in issue list."
            new_issue = createIssueWithData(input_issue)
            issue_list.append(new_issue)
        else:
            flag=0
    return issue_list

def saveIssues(issues):
        choice = raw_input('-->Your are about to save tickets on redmine. Do you wish to continue? ')
        if(choice=="No"):
            print "-->You choose to stop. Probably a good step!"
            return
        for issue in issues:
            print "-->Saving ticket " + issue.subject
            issue.save()

# Script execution starts here.
#================================
USERNAME = raw_input("-->Your redmine username: ")
PASSWORD = getpass.getpass("-->Your redmine password: ")

print "-->Logging in to" + PROJECT_NAME
redmine = Redmine(REDMINE_URL, username=USERNAME, password=PASSWORD)
print "-->Successfully Logged in."
print "-->Loading projet " + PROJECT_NAME
project = redmine.project.get(PROJECT_NAME, include='trackers,issue_categories,enabled_modules')
print "-->Successfully Loaded " + PROJECT_NAME

redmine_issues = listAllIssues(sprint_issue_id)
input_issues = readInputFile("./tickets_input_file")
#createDebugData()
new_issue_list = createIssueList(redmine_issues, input_issues)
saveIssues(new_issue_list)
