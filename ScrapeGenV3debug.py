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
company = '4-tell'
url = "http://www.4-tell.com/careers/"
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

def getTrueXPATH(wd, foundElements=[]):
    elementsArray = []
    indexes = []
    true_xpath = ""
    print("1 True XPATH pre filterword loop") ##
    if foundElements == []:
        print("1.5 foundElements is empty")
        for filterWord in jobWhiteList:
            foundElements += wd.find_elements_by_partial_link_text(filterWord)
            if len(foundElements) >= 3:
                print("2 True XPATH filterword loop break") ##
                break
    for element in foundElements:
        print(element.text)
        xpathToElement = generateXPATH(element, "")
        elementsArray.append(xpathToElement.split("/"))
        print("3 elements array creation") ##
    length = len(elementsArray) ##
    if length > 1:
        print("length of elements array: " + str(length))
        shortest = 100
        for k in range(length):
            new = len(elementsArray[k])
            if new < shortest:
                shortest = new
        for i in range(length-1):
            print("length of elements array[i]: " + str(len(elementsArray[i])))
            print("4 elements array i loop") ##
            
            for j in range(shortest):
                print("5 elements array i loop") ##
                print(elementsArray[i][j])
                if elementsArray[i][j] != elementsArray[i+1][j]:
                    print("6 indexes.append(j) step") ##
                    indexes.append(j)
    if len(indexes) != 0:
        for i in range(1, indexes[0]):
            print("7 true xpath assignment") ##
            true_xpath += "/" + elementsArray[0][i]
        true_xpath += "/" + elementsArray[0][indexes[0]][:elementsArray[0][indexes[0]].rfind("[")]
    if true_xpath == "":
        print("2.5 true xpath is empty, re-assignment") ##
        for filterWord in jobWhiteList:
            foundElements+= wd.find_elements_by_xpath( "(//*[contains(text(), '" + filterWord + "')] | //*[@value='" + filterWord + "'])")
            getTrueXPATH(wd, foundElements)
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
        print("8 element index split") ##
        elementString = element.text.split()
        for i in range(len(elementString)):
            print("9 elementString i loop") ##
            for filterWord in jobWhiteList:
                print("10 filterwordbreak i loop") ##
                if (elementString[i].rfind(filterWord) != -1):
                    print("11 jobnameindex") ##
                    jobNameIndex = i
                    break
            if (locationRegEx.search(elementString[i])):
                print("12 locationindex") ##
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
        print("13 second text.split") ##
        elementString = element.text.split()
        if locationIndex != -1:
            print("14 elementString[locationIndex]") ##
            location = elementString[locationIndex]
        if jobNameIndex != -1:
            print("15 elementString[jobnameIndex]") ##
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
    true_xpath = getTrueXPATH(wd) ## if xpath="", find another means
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
            print("16 url get") ##
            url = content[i].strip()
            print(url)
            global company
            print("17 url get") ##
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

#main()
wd = webdriver.Chrome(driverLocation)
runScrape(wd)
