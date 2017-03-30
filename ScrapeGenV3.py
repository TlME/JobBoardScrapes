##=====================================
# Generic Website Scrape Generator
#
## Written mostly by Nick Henegar
# Current version written 3/30/2017
#======================================

import urllib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import json
import re
import sys

#==== Constants and Variables ========================
# define whatever needs to be globally available here,
# unless another function does it instead...?
company = 'BadValue'
url = ""
driverLocation =  'C:\\Users\\Student\\Desktop\\JobBoardLiveProject\\NickTestZone\\Scrapes\\chromedriver.exe'
jobWhiteList = ["Engineer","Developer","Specialist"]
locationRegEx = re.compile(r"\b[A-Z][a-zA-Z]+,(([ ]?[A-Z]{2})|([ ]?[A-Z][a-z]+))\b")

#==== generateXPATH - [FUNCTIONS] =================================================================
# @invocation - generateXPATH(childElement, current)
# @args -
    # childElement - The element which is being examined to determine its xpath.
    # current - A string which contains the current xpath to a given element.
# @returns - A string that is the XPATH to a given element.
#
# Usage - Give it an element and an empty string, or a current xpath, and it will
#       find the exact xpath to the element specified. This is useful.
#==================================================================================================
def generateXPATH(childElement, current):
    childTag = childElement.tag_name
    if(childTag == "html") :
        return "/html[1]" + current
    
    parentElement = childElement.find_element_by_xpath("..")
    childrenElements = parentElement.find_elements_by_xpath("*")
    count = 0
    for e in childrenElements:
        childrenElementTag = e.tag_name
        if(childTag == childrenElementTag):
            count += 1
        if(childElement == e):
            return generateXPATH(parentElement, "/" + childTag + "[" + str(count) + "]" + current)
    return null
#==== getTrueXPATH - [FUNCTIONS] =================================================
# @invocation - getTrueXPATH(wd)
# @dependencies - GLOBAL jobWhiteList[]
# @args -
    # wd - A selenium compatible webdriver, probably chromedriver v2.28
# @returns - true_xpath, a string which represents the relative xpath to a given
#               element on the page
#
# Usage - This breaks elements down by a filterWord matching criteria, finds their
#       xpaths, then compares the results of splitting thier xpaths against other 
#       elements' xpaths which match the criteria. If a pattern can be discerned,
#       it returns the true_xpath to the container which owns those elements.
#==================================================================================
def getTrueXPATH(wd):
    elementsArray = []
    foundElements = []
    indexes = []
    true_xpath = ""
    for filterWord in jobWhiteList:
        foundElements += wd.find_elements_by_partial_link_text(filterWord)
        if len(foundElements) >= 3:
            break
    for element in foundElements:
        xpathToElement = generateXPATH(element, "")
        elementsArray.append(xpathToElement.split("/"))
    if len(elementsArray) > 1: 
        for i in range(len(elementsArray)-1):
            for j in range(len(elementsArray[i])):
                if elementsArray[i][j] != elementsArray[i+1][j]:
                    indexes.append(j)

    for i in range(1, indexes[0]):
        true_xpath += "/" + elementsArray[0][i]
    true_xpath += "/" + elementsArray[0][indexes[0]][:elementsArray[0][indexes[0]].rfind("[")]
    return true_xpath
#==== findElementIndex() - [FUNCTIONS] ===========================================================
# @invocation - findElementIndex(allElements)
# @args -
    # allElements - List of Selenium web-element objects, which respond to method calls.
# @returns - jobNameIndex, either -1 or the index that the job name was found in element.text[].
#            locationIndex, either -1 or the index that the location was found in element.text[].
#
# Usage - Used to parse through a series of elements looking for the index at which
#          specific text strings can be found, which it then returns as two separate variables.
#=================================================================================================          
def findElementIndex(allElements):
    jobNameIndex = -1
    locationIndex = -1
    dateIndex = -1
    for element in allElements:
        elementString = element.text.split()
        for i in range(len(elementString)):
            for filterWord in jobWhiteList:
                if (elementString[i].rfind(filterWord) != -1):
                    jobNameIndex = i
                    break
            if (locationRegEx.search(elementString[i])):
                locationIndex = i
                break
            #if (dateRegEx.search(elementString[i])):
                #dateIndex = i
    return jobNameIndex, locationIndex
#==== buildJob() - [FUNCTIONS] ============================================================
# @invocation - buildJob(allElements, jobNameIndex, locationIndex, jobs)
# @dependencies - GLOBAL url, GLOBAL company
# @args -
    # allElements - List of Selenium web-element objects, which respond to method calls. 
    # jobNameIndex - int "known" index of a specific jobName within a text.split() array.
    # locationIndex - int "known" index of a specific location within a text.split() array.
    # jobs - An empty list to be filled with Job objects
# @returns - A populated list of jobs for conversion into json - jobs[]
#
# Usage - Takes @allElements and tries to split its .text portion into an array which is
#       accessed based on provided @index_values. An href element is found, and all the
#       data is written into the job dict object and appended to the jobs[] list.
#===========================================================================================
def buildJob(allElements, jobNameIndex, locationIndex, jobs): 
    location = ""
    jobTitle = ""
    applicationLink = url

    for element in allElements:
        elementString = element.text.split()
        if locationIndex != -1:
            location = elementString[locationIndex]
        if jobNameIndex != -1:
            jobTitle = elementString[jobNameIndex]
        anchor = element.find_element_by_tag_name("a")
        applicationLink = anchor.get_attribute("href")
        # Build an individual job
        job = {'ApplicationLink': applicationLink,
               'Company': company,
               'DatePosted': '',
               'Experience': '',
               'Hours': '',
               'JobID': '',
               'JobTitle': jobTitle,
               'LanguagesUsed' : '',
               'Location' : location,
               'Salary' : '',
        }
        print(job)
        jobs.append(job)
    return jobs
#==== parseSinglePage() - [FUNCTION] ====================================================
# @invocation - parseSinglePage(wd)
# @args -
    # wd - A selenium compatible webdriver, probably chromedriver v2.28
# @returns - jobs[], an array of dict objects which are described in FUNCTION buildJob()
#
# Usage - Function designed to try to strip the relevant job posting data
#          from a single page. It cannot currently navigate to other pages.
#======================================================================================
def parseSinglePage(wd):
    jobs = []
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    true_xpath = getTrueXPATH(wd)
    allElements = wd.find_elements_by_xpath(true_xpath)
    jobNameIndex, locationIndex = findElementIndex(allElements)
    jobs = buildJob(allElements, jobNameIndex, locationIndex, jobs)

    return jobs
#==== runScrape() - [FUNCTION] =================================================
# @invocation - runScrape(wd)
# @dependencies - GLOBAL url, GLOBAL company
# @args -
    # wd - A selenium compatible webdriver, probably chromedriver v2.28
# @returns - closes @wd, writes to an outfile.
#
# Usage -   When provided with a webdriver and GLOBAL STRING "URL",
#           calls parseSinglePage function and uses json.dump to write
#           the results (if any) to a [company].json file in directory.
#=============================================================================
def runScrape(wd):
    wd.get(url)
    jobs = parseSinglePage(wd)
    # Pagination function evocation goes here
    wd.quit()
    with open(company + '.json', 'w') as outfile:
        json.dump(jobs, outfile)
#==== main() - [FUNCTIONS] =================================================
# @invocation - main()
# @args - 
# @returns - writes a fails.txt, success.txt
#           - sets two GLOBAL strings: url & company 
#
# Usage - This runs the program
#==================================================================================        
def main():    
    with open('sitesToScrape.txt', 'r') as inputSites:
        content = inputSites.readlines()
    with open('ScrapeFailure.txt', 'w') as fails:
        for i in range(0,len(content)-1, 2):
            global url
            url = content[i].strip()
            print(url)
            global company
            company = content[i+1].strip()
            print(company)
            wd = webdriver.Chrome(driverLocation)
            try: runScrape(wd)
            except:
                exc = str(sys.exc_info()[0])
                print("There was an exception while trying to parse " + url) # Debug mode is another file which may or
                print("Please run this url in debug mode to learn more." + exc) # may not have development parity with this one.
                wd.quit()
                fails.write(url + "\n" + "Failure reason: " + exc + "\n")
                continue
            
## Main function evocation ##
main()
