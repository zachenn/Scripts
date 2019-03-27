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
                    'toDate': '1556348401000'} # 04/27/2019

    # call the API
    authValues = (username, password)
    response = requests.get(url, auth = authValues, headers = headers, params = parameters)

    # convert JSON to dictionary (de serialize)
    data = response.json()

    # prepare to convert to csv
    index = 0
    while index < data['tot']:
        id = data['txn'][index]['tid']
        newCSVFile[id] = data['txn'][index]
        index += 1

    createCSVFromAPIAppID(newCSVFile, parameters)

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
                id = row[0]
                decision = row[2]

                # add all the app ids that are accepted, rejected, or under review
                applicationIDDict[id] = decision

            else:
                count += 1

    callAPIWithDict(applicationIDDict)

def scrubWebsite():

    # create a login session
    session = requests.session()

    # get the login page
    loginURL = 'url'
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
    print("" in response.text)

    newURL = "url"
    newSession = requests.session()
    test = newSession.get(newURL)
    print(test.text)

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

    print(data)
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
    createCSVFromCSVID(newCSVFile)

def createCSVFromCSVID(newCSVFile):

    # open a file for writing
    customerData = open('Customer List.csv', 'w')

    # create the csv writer object for the file we just opened
    csvwriter = csv.writer(customerData)

    # grab the application ids
    tids = newCSVFile.keys()
    count = 0

    # create this list so we can count how many customers have been accepted
    decisionList = {
        'APPROVED': 0,
        'DECLINED': 0,
        'REVIEW': 0,
        'CLOSED': 0
    }

    for tid in tids:

        # get the information for the specified tid
        customerDetails = newCSVFile[tid]

        # only add accepted to the form and remove BOs
        if customerDetails['txn'][0]['decision'] == 'APPROVED' and '@' in customerDetails['txn'][0]['man']:

            # create a dictionary for the fields we want
            legalName = ''

                # it is a merchant
            if 'bfn' in customerDetails['txn'][0]:
                legalName = customerDetails['txn'][0]['bfn'] + ' ' + customerDetails['txn'][0]['bln']

                # it is a consumer
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

def createCSVFromAPIAppID(newCSVFile, parameters):

    # open a file for writing
    customerData = open('Customer List.csv', 'w')

    # create the csv writer object for the file we just opened
    csvwriter = csv.writer(customerData)

    # grab the application ids
    tids = newCSVFile.keys()
    count = 0

    # create this list so we can count how many customers have been accepted
    findingsList = {
        'ACCEPTED': 0,
        'Merchant': 0,
        'Consumer': 0
    }

    merchants = []
    customers = {}

    # create our customer list
    for tid in tids:

        # get the information for the specified tid
        customerDetails = newCSVFile[tid]

        # only add accepted to our list and remove BOs/trades
        if customerDetails['decision'] == 'ACCEPTED' and 'man' in customerDetails and '@' in customerDetails['man'] and customerDetails['amt'] == 0:

            # create a dictionary for the fields we want
            legalName = ''

                # it is a consumer
            if 'bfn' in customerDetails:
                legalName = customerDetails['bfn'] + ' ' + customerDetails['bln']

                # it is a merchant
            else:
                legalName = customerDetails['man']
                merchants.append(legalName)

            importantInformation = {
                # 'Application ID' : tid,
                'Legal Name': str(legalName),
                'man': customerDetails['man'],
                'Date Opened': datetime.utcfromtimestamp(int(customerDetails['tti'])/1000).strftime('%m-%d-%Y %H:%M:%S'),
                'Decision': customerDetails['decision']
            }

            # add it into our customers dictionary
            customers[tid] = importantInformation

    # add customers to our csv file
    for tid in customers:

        # remove additional BOs
        if '@' not in customers[tid]['Legal Name'] and customers[tid]['man'] not in merchants or '@' in customers[tid]['Legal Name']:

            # add to our findingsList
            findingsList[importantInformation['Decision']] += 1
            if '@' in customers[tid]['Legal Name']:
                findingsList['Merchant'] += 1
            else:
                findingsList['Consumer'] += 1

            # create headers if they don't exist yet
            if count == 0:

                # info for normal header
                header = list(customers[tid])

                # create header
                csvwriter.writerow(header)
                count += 1

            # add the row values
            csvwriter.writerow(customers[tid].values())

    # make a new row for our findings
    findingsListKeys = findingsList.keys()
    findings = ''
    for finding in findingsListKeys:
        findings += f'{finding} = {findingsList[finding]}\n'
    newFindings = [findings]
    csvwriter.writerow(newFindings)

    # close and save the new csv file to the computer
    customerData.close()

def createJSON():

    # save json to computer. https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    with open('data.txt', 'w') as outfile:
        json.dumps(data, outfile)

getApplicationIDsFromAPI()
