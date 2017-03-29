##=====================================
# Generic Website Scrape Generator
#
## Written mostly by Nick Henegar
# Current version written 3/26/2017
#======================================

import urllib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import json
import re



#==== Constants and Variables ========================
company = 'portlandTech'
url = "http://portlandtech.org/"
whiteList = [["AdVolume","AltSource"],["Hewlett","Relic"], ["Providence", "Salesforce"]] #add two words from each column to use as filters.
locationRegEx = re.compile(r"\b[A-Z][a-zA-Z]+,(([ ]?[A-Z]{2})|([ ]?[A-Z][a-z]+))\b")
appLinkArray = []
companyNameArray =[]


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

def getTrueXPATH(wd, whiteList):
    elementsArray = []
    foundElements = []
    indexes = []
    for filterWord in whiteList:
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
    true_xpath = ""
    for i in range(1, indexes[0]):
        true_xpath += "/" + elementsArray[0][i]
    true_xpath += "/" + elementsArray[0][indexes[0]][:elementsArray[0][indexes[0]].rfind("[")]
    return true_xpath

def findElementIndex(allElements):
    jobNameIndex = -1
    locationIndex = -1
    dateIndex = -1
    for element in allElements:
        elementString = element.text.split("\n")
        for i in range(len(elementString)):
            for filterWord in jobWhiteList:
                if (elementString[i].rfind(filterWord) != -1):
                    jobNameIndex = i
            if (locationRegEx.search(elementString[i])):
                locationIndex = i
            #if (dateRegEx.search(elementString[i])):
                #dateIndex = i
    return jobNameIndex, locationIndex

def buildJob(allElements, jobNameIndex, locationIndex, jobs): 
    location = ""
    jobTitle = ""
    applicationLink = url

    for element in allElements:
        elementString = element.text.split("\n")
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
def grabLinks(allElements):
    count = 0
    for element in allElements:
        if count < 15:
            anchor = element.find_element_by_tag_name("a")
            applicationLink = anchor.get_attribute("href")
            appLinkArray.append(applicationLink)
            print("Adding " + applicationLink + " to the array...")
            companyNameArray.append(anchor.text)
            print("Adding " + anchor.text + " to the array...")
            count += 1
        else:
            break
        
def parseSinglePage(wd):
    true_xpath_list = []
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    for filters in whiteList:
        true_xpath_list.append(getTrueXPATH(wd, filters))
    for true_xpath in true_xpath_list:
        allElements = wd.find_elements_by_xpath(true_xpath)
        grabLinks(allElements)


wd = webdriver.Chrome('C:\\Users\\Student\\Desktop\\JobBoardLiveProject\\NickTestZone\\chromedriver.exe')
wd.get(url)
wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
fullListElement = wd.find_element_by_partial_link_text("Full List")
fullListElement.click()
parseSinglePage(wd)

# Pagination function evocation goes here

wd.quit()
#==== Outputting a JSON file for internal usage ===============
with open("sitesToScrape.txt", 'w') as outfile:
    for i in range(len(appLinkArray)):
        outfile.write(appLinkArray[i].strip() + "\n")
        outfile.write(companyNameArray[i].strip() + "\n")
    outfile.close()
