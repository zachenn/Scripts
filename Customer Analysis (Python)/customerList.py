import requests                     # to request API
import json                         # to convert to json
import csv                          # to convert to csv
from datetime import datetime       # to convert unix timestamp to readable date

from lxml import html               # to parse html
from bs4 import BeautifulSoup       # to parse html


# download csv file. run it through the script, and you should have a csv file back with new
# information that you can view with excel

def getApplicationIDsFromAPI(): # 200 day max

    newCSVFile = {}

    # Basic Auth Url with login values as username and password
    url = "url"
    username = "username"
    password = "password"
    headers = {'accept': 'application/json'}
    parameters = {'fromDate': '1539131307000', # 10/10/2018
                    'toDate': '1552955307000'} # 03/19/2019

    # call the API
    authValues = (username, password)
    response = requests.get(url, auth = authValues, headers = headers, params = parameters)

    # convert JSON to dictionary (de serialize)
    data = response.json()

    # prepare to convert to csv
    for transaction in data['txn']:
        id = transaction['tid']
        newCSVFile[id] = data

    createCSV(newCSVFile)

def getApplicationIDsFromCSV(csvFile):

    applicationIDDict = {}

    # parse the csv file to get a list of applicationIDs
    with open(csvFile) as csv_file:
        readCSV = csv.reader(csv_file, delimiter=',')
        count = 0

        for row in readCSV:

            # # prevent "Application ID" header and closed applications from being added
            if count != 0:

                # column 1 is the application id column in the csv file
                id = row[1]
                decision = row[4]

                # add all the app ids that are accepted, rejected, or under review
                applicationIDDict[id] = decision

            else:
                count += 1

    callAPIWithDict(applicationIDDict)

def scrubWebsite():

    # create a login session
    session = requests.session()

    # get the login page
    loginURL = 'loginURL'
    login = session.get(loginURL)
    loginHTML = html.fromstring(login.text)

    # get the CSRF token
    hiddenInputs = loginHTML.xpath(r'//form//input[@type="hidden"]')
    form = {x.attrib["name"]: x.attrib["id"] for x in hiddenInputs}
    form['username'] = 'username'
    form['password'] = 'password'
    # csrftoken = login.cookies['csrftoken']
    # print(login.cookies)
    print(form)

    # login
    response = session.post(loginURL, data = form, headers = dict(referer = loginURL))
    print(response.url)
    print("Transaction Evaluation Results" in response.text)

    newURL = "newURL"
    newSession = requests.session()
    test = newSession.get(newURL)
    print(test.text)

    # # login
    #
    # result = session_requests.post(
    #     loginURL,
    #     data = payload,
    #     headers = dict(referer = loginURL)
    # )
    #
    # print(result.status_code)
    #
    # # scrape content
    # url = 'https://edna.identitymind.com/merchantedna/#!kyc'
    # result = session_requests.get(
    #     url,
    #     headers = dict(referer = url)
    # )
    #
    # print(result.status_code)
    #
    # tree = html.fromstring(result.content)
    # info = tree.xpath("//div[@id='id-1y-1552604206200']")
    # test = tree.xpath('//span[@class="v-button-caption"]/text()')
    # print(test)

def callAPIWithID(id):

    newCSVFile = {}

    # Basic Auth Url with login values as username and password
    url = "url"
    username = "username"
    password = "password"
    headers = {'accept': 'application/json'}

    # use the list of application IDs to get information on each one
    parameters = {'mid': id}

    # Make a request to the endpoint using the correct auth values
    authValues = (username, password)
    response = requests.get(url, auth = authValues, headers = headers, params = parameters)

    # Convert JSON to dictionary (de serialize)
    data = response.json()
    newCSVFile[id] = data

    # using the new list of customers, extract only what we need
    createCSV(newCSVFile)

def callAPIWithDict(applicationIDDict):

    newCSVFile = {}
    applicationIDs = applicationIDDict.keys()

    # Basic Auth Url with login values as username and password
    url = "url"
    username = "username"
    password = "password"
    headers = {'accept': 'application/json'}

    # use the list of application IDs to get information on each one
    for id in applicationIDs:

        parameters = {'mid': id}

        # Make a request to the endpoint using the correct auth values
        authValues = (username, password)
        response = requests.get(url, auth = authValues, headers = headers, params = parameters)

        # Convert JSON to dictionary (de serialize)
        data = response.json()
        newCSVFile[id] = data
        newCSVFile[id]['txn'][0]['decision'] = applicationIDDict[id]

    # using the new list of customers, extract only what we need
    createCSV(newCSVFile)

def createCSV(newCSVFile):

    # open a file for writing
    customerData = open('Customer List.csv', 'w')

    # create the csv writer object for the file we just opened
    csvwriter = csv.writer(customerData)

    # grab the application ids
    tids = newCSVFile.keys()
    count = 0

    # create this list so we can count how many customers have been accepted
    decisionList = {
        'Accepted': 0,
        'Rejected': 0,
        'Review': 0,
        'Closed': 0
    }

    for tid in tids:

        # get the information for the specified tid
        customerDetails = newCSVFile[tid]

        # create a dictionary for the fields we want
        legalName = ''
        if ('bfn' in customerDetails['txn'][0]):
            legalName = customerDetails['txn'][0]['bfn'] + ' ' + customerDetails['txn'][0]['bln']
        else:
            legalName = customerDetails['txn'][0]['man']

        importantInformation = {
            # 'Application ID' : tid,
            'Legal Name': legalName,
            'man': customerDetails['txn'][0]['man'],
            'Date Opened': datetime.utcfromtimestamp(int(customerDetails['txn'][0]['tti'])/1000).strftime('%m-%d-%Y %H:%M:%S'),
            'Decision': customerDetails['txn'][0]['decision'],
            'Amount' : customerDetails['txn'][0]['amt']
        }

        # add to our decisionList
        decisionList[importantInformation['Decision']] += 1

        # create headers if they don't exist yet
        if count == 0:

            # info for normal header
            header = list(importantInformation)

            # info for header for findings
            header.append('Count')

            # create header
            csvwriter.writerow(header)
            count += 1

        # add the row values
        csvwriter.writerow(importantInformation.values())

    # make a new row for our findings
    decisionListKeys = decisionList.keys()
    decisions = ''
    for decision in decisionListKeys:
        decisions += f'{decision} = {decisionList[decision]}\n'
    findings = [decisions]
    csvwriter.writerow(findings)

    # close and save the new csv file to the computer
    customerData.close()

def createJSON():

    # save json to computer. https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    with open('data.txt', 'w') as outfile:
        json.dumps(data, outfile)

getApplicationIDsFromCSV('test.csv')
# scrubWebsite()
# getApplicationIDsFromAPI()
