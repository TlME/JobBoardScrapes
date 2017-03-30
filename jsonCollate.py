##=====================================
# Bulk JSON File Collating Script
#
## Written mostly by Nick Henegar
# Current version written 3/30/2017
#======================================

import json
import os

path = r"C:\Users\Student\Desktop\JobBoardLiveProject\NickTestZone\Scrapes"
bigData = []
for filename in os.listdir(path):
    if filename.endswith(".json"):
        with open(os.path.join(path, filename), 'r') as jfile:
            jsonData = json.loads(jfile.read())
            for element in jsonData:
                print(element)
                bigData.append(element)
with open(os.path.join(path, "bigData.json"), 'w') as jfile:
    json.dump(bigData, jfile)
