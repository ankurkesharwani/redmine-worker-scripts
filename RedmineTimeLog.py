from redmine import Redmine
import redmine
import json
from pprint import pprint
import datetime
import sys

#Config Goes Here
#=====================
USERNAME=""
PASSWORD=""
REDMINE_URL=""
PROJECT_NAME = ""

# Variable declarations goes here.
input_issues = None
redmine_issues = None
sprint_issue_id = 50501

# Utility methods
#=================
def listAllIssues(parentIssueId):
    issue = redmine.issue.get(parentIssueId, include='children')
    print "->Redmine issues"
    for item in issue.children:
        print item.subject
    return issue.children

def readInputFile(file_name):
    input_data = json_data=open(file_name).read()
    data = json.loads(json_data)
    print "->Input issues"
    for item in data:
        print item["subject"]
    return data

def createTimeEntries(redmine_issues, input_entries):
    new_time_entries =[]
    for time_entry in input_entries:
        for redmine_issue in redmine_issues:
            if time_entry["subject"] in redmine_issue.subject:
                # Issue found in redmine.

                print "-->Createing a time entry for " + time_entry["subject"]
                new_time_entry = redmine.time_entry.new()
                new_time_entry.issue_id = redmine_issue.id
                new_time_entry.spent_on = time_entry["spent_on"]
                new_time_entry.hours = time_entry["hours"]
                new_time_entry.activity_id = time_entry["activity_id"]
                new_time_entry.comments = time_entry["comments"]

                if(time_entry["custom_fields"] == "External"):
                    new_time_entry.custom_fields = [{'id': 45, 'name': 'Billing Category','value':'External'}]
                else:
                    new_time_entry.custom_fields = [{'id': 45, 'name': 'Billing Category','value':'Internal'}]

                new_time_entries.append(new_time_entry)
                break
    return new_time_entries

def logTime(time_entries):
    choice = raw_input('-->Your are about to save time entries on redmine. Do you wish to continue? ')
    if(choice=="No"):
        print "-->You choose to stop. Probably a good step!"
        return
    for entry in time_entries:
        entry.save()

# Script execution starts here.
#================================
print "->Logging in to" + PROJECT_NAME
redmine = Redmine(REDMINE_URL, username=USERNAME, password=PASSWORD)
print "->Successfully Logged in."
print "->Loading projet " + PROJECT_NAME
project = redmine.project.get(PROJECT_NAME, include='trackers,issue_categories,enabled_modules')
print "->Successfully Loaded " + PROJECT_NAME

redmine_issues = listAllIssues(sprint_issue_id)
input_time_entries = readInputFile("./input_time")
new_time_entries = createTimeEntries(redmine_issues,input_time_entries)

logTime(new_time_entries)
