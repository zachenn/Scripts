import requests                     # to request API
import json                         # to convert to json
import csv                          # to convert to csv
from datetime import datetime       # to convert unix timestamp to readable date

from lxml import html               # to parse html
from bs4 import BeautifulSoup       # to parse html


'''
you can run the script in 1 of 2 ways. both return a CSV file for additional analysis
1) use an HTTPS request. use getApplicationIDsFromAPI()
2) use a CSV file. use getApplicationIDsFromCSV()

note: using an HTTPS request w/ a single ID vs using a time frame
returns different JSON responses

'''

# using an HTTPS request

def getApplicationIDsFromAPI(fromDate, toDate, totalTransactionReport): # 200 day max. epoch time

    newCSVFile = {}

    # Basic Auth Url with login values as username and password
    url = "url"
    username = "username"
    password = "password"
    headers = {'accept': 'application/json'}
    parameters = {'fromDate': fromDate,
                    'toDate': toDate}

    # call the API
    authValues = (username, password)
    response = requests.get(url, auth = authValues, headers = headers, params = parameters)

    # convert JSON to dictionary (de serialize)
    data = response.json()

    # prepare to convert to csv
    for index in range(0, data['tot']):
        id = data['txn'][index]['tid']
        newCSVFile[id] = data['txn'][index]

    createCSVFromAPIAppID(newCSVFile)
    if totalTransactionReport:
        totalTransactionReport(newCSVFile)

def createCSVFromAPIAppID(newCSVFile):

    # open a file for writing
    customerData = open('Transaction Monitoring.csv', 'w')

    # create the csv writer object for the file we just opened
    csvwriter = csv.writer(customerData)

    # grab the application ids
    tids = newCSVFile.keys()
    count = 0

    # create a dictionary of customers to count transaction volume
    customerList = {}

    for tid in tids:

        # get the information for the specified tid
        customerDetails = newCSVFile[tid]

        # use this gatekeeper to prevent appIDs retrieved that did not transact
        if customerDetails['amt'] != 0:

            # create a dictionary for the fields we want
            name = 'Unknown'
            if ('man' in customerDetails):
                name = customerDetails['man']

            transactionType = 'Funding' # USD in to us
            if (customerDetails['tt'] == 'AccountTransferOut'):
                transactionType = "Withdrawal" # sell USD to them

            transactionTime = datetime.utcfromtimestamp(int(customerDetails['tti'])/1000).astimezone(timezone('US/Pacific'))

            importantInformation = {
                'man': name,
    			'Amount': '{:,}'.format(customerDetails['amt']),
                'Currency': customerDetails['ccy'],
    			'Transaction Time': transactionTime.strftime('%m-%d-%Y %H:%M:%S'), #ask neal what time zone is used in IDM
                'Transaction Type': transactionType,
                'Decision': customerDetails['decision']
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

# using a csv file

def getApplicationIDsFromCSV(csvFile):

    applicationIDDict = {}
    newCSVFile = {}

    # parse the csv file to get a list of applicationIDs
    with open(csvFile) as csv_file:
        readCSV = csv.reader(csv_file, delimiter=',')
        count = 0

        for row in readCSV:

            # prevent "Application ID" header and closed applications from being added
            if count != 0:

                # column 1 is the application id column in the csv file
                id = row[0]
                type = row[4]


                # add all the app ids that are accepted, rejected, or under review
                applicationIDDict[id] = type

            else:
                count += 1

    for id in applicationIDDict:
        newCSVFile[id] = callAPIWithSingleID(id)

    createCSVFromCSVID(newCSVFile)

def callAPIWithSingleID(id):

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
    return data

def createCSVFromCSVID(newCSVFile):

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

        transactionType = 'Funding' # USD in to us
        if (customerDetails['txn'][0]['tt'] == 'AccountTransferOut'):
            transactionType = "Withdrawal" # sell USD to them

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

# other

def totalTransactionReport(newCSVFile):

    # open a file for writing
    customerData = open('Total Transaction Report.csv', 'w')

    # create the csv writer object for the file we just opened
    csvwriter = csv.writer(customerData)

    # grab the application ids
    tids = newCSVFile.keys()
    count = 0

    # create a dictionary of customers to count transaction volume
    customerList = {}

    for tid in tids:

        # get the information for the specified tid
        customerDetails = newCSVFile[tid]

        # use this gatekeeper to prevent appIDs retrieved that did not transact
        if customerDetails['amt'] != 0 and customerDetails['ccy'] == 'USD':

            # create a dictionary for the fields we want
            name = 'Unknown'
            if ('man' in customerDetails):
                name = customerDetails['man']

            importantInformation = {
                'man': name,
    			'Amount': int(customerDetails['amt']),
                'Currency': customerDetails['ccy'],
    		}

            # add the transaction data to our customerList
            if name not in customerList:
                customerList[name] = importantInformation
            else:
                customerList[name]['Amount'] += int(customerDetails['amt'])

    # add customers to csv file
    for tid in customerList:

        # create headers if they don't exist yet
        if count == 0:

            # info for normal header
            header = list(customerList[tid].keys())

            # create header
            csvwriter.writerow(header)
            count += 1

        # add the row values
        customerList[tid]['Amount'] = '{:,}'.format(customerList[tid]['Amount'])
        csvwriter.writerow(customerList[tid].values())

    # close and save the new csv file to the computer
    customerData.close()

def createJSON():

    # save json to computer. https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    with open('data.txt', 'w') as outfile:
        json.dumps(data, outfile)

getApplicationIDsFromAPI('1553562000000', '1553648400000', False) # 03/25/2019 6 PM PST, 03/26/2019 6 PM PST // https://www.epochconverter.com/
                                                            # '1539131307000', 1556348401000 # for 09/01/18 - 04/27/19
