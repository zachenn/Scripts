import requests                     # to request API
import json                         # to convert to json
import csv                          # to convert to csv
from datetime import datetime       # to convert unix timestamp to readable date

from lxml import html               # to parse html
from bs4 import BeautifulSoup       # to parse html


# download csv file. run it through the script, and you should have a csv file back with new
# information that you can view with excel

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
                type = row[4]

                # add all the app ids that are accepted, rejected, or under review
                applicationIDDict[id] = type

            else:
                count += 1

    callAPIWithDict(applicationIDDict)

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

def callAPIWithDict(applicationIDs):

    newCSVFile = {}

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

    # using the new list of customers, extract only what we need
    createCSV(newCSVFile)

def createCSV(newCSVFile):

    # open a file for writing
    customerData = open('Transaction Monitoring.csv', 'w')

    # create the csv writer object for the file we just opened
    csvwriter = csv.writer(customerData)

    # grab the application ids
    tids = newCSVFile.keys()
    count = 0

    # create a dictionary of customers to count number of times they transact
    customerList = {}

    for tid in tids:

        # get the information for the specified tid
        customerDetails = newCSVFile[tid]

        # create a dictionary for the fields we want
        name = 'Unknown'
        if ('man' in customerDetails['txn'][0]):
            name = customerDetails['txn'][0]['man']

        transactionType = 'Funding'
        if (customerDetails['txn'][0]['tt'] == 'AccountTransferOut'):
            transactionType = "Withdrawal"

        importantInformation = {
            'man': name,
			'Amount': '{:,}'.format(customerDetails['txn'][0]['amt']),
            'Currency': customerDetails['txn'][0]['ccy'],
			'Transaction Time': datetime.utcfromtimestamp(int(customerDetails['txn'][0]['tti'])/1000).strftime('%m-%d-%Y %H:%M:%S'),
            'Transaction Type': transactionType,
            'Decision': customerDetails['txn'][0]['decision']
		}

        # create headers if they don't exist yet
        if count == 0:

            # info for normal header
            header = list(importantInformation)

            # create header
            csvwriter.writerow(header)
            count += 1

        # add the row values
        csvwriter.writerow(importantInformation.values())

    # close and save the new csv file to the computer
    customerData.close()

def createJSON():

    # save json to computer. https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    with open('data.txt', 'w') as outfile:
        json.dumps(data, outfile)

getApplicationIDsFromCSV('test.csv')
