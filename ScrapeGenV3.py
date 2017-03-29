##=====================================
# Generic Website Scrape Generator
#
## Written mostly by Nick Henegar
# Current version written 3/28/2017
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
company = 'BadValue'
url = ""
driverLocation =  'C:\\Users\\Student\\Desktop\\JobBoardLiveProject\\NickTestZone\\Scrapes\\chromedriver.exe'
jobWhiteList = ["Engineer","Developer","Specialist"]
locationRegEx = re.compile(r"\b[A-Z][a-zA-Z]+,(([ ]?[A-Z]{2})|([ ]?[A-Z][a-z]+))\b")

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

##def splitter(element_text, delimiter=False):
##    dlist = ["\n", ""
##    
##    if delimiter:
##        return element_text.split(delimiter)
##    else:
##        for delim in dlist:
##        testCase = splitter(element_text, 
            
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

def parseSinglePage(wd):
    jobs = []
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    true_xpath = getTrueXPATH(wd)
    allElements = wd.find_elements_by_xpath(true_xpath)
    jobNameIndex, locationIndex = findElementIndex(allElements)
    jobs = buildJob(allElements, jobNameIndex, locationIndex, jobs)

    return jobs

def runScrape(wd):
    wd.get(url)
    jobs = parseSinglePage(wd)
    # Pagination function evocation goes here
    wd.quit()
    with open(company + '.json', 'w') as outfile:
        json.dump(jobs, outfile)
        
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
                print("There was an exception while trying to parse " + url)
                print("Please run this url in debug mode to learn more." + exc) #There is no debug mode currently, *sunglasses* deal with it.
                wd.quit()
                fails.write(url + "\n" + "Failure reason: " + exc + "\n")
                continue

main()
