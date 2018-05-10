import csv
import os
import pickle as pk
from nltk.corpus import stopwords

print(os.getcwd())

csvFiles = os.listdir('../../OutputData/outputs/original/csv')
csvPath = '../../OutputData/outputs/original/csv/'
refPath = '../../OutputData/REF/REF2014ResultsOutputsCsv.csv'

def processInputCsv(inputPath):
    '''
    Process the paper titles file from inputPath, read it in using win-1252 encoding,
    and create a dict using the headers as keys and the values of each column
    as a list for the desired columns
    '''
    inputFile = []
    with open(inputPath, 'r', newline='',
              encoding='windows-1252') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read())
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        for row in reader:
            inputFile.append(row)
        csvfile.close()

    headers = inputFile[2]

    # Transpose the matrix so that we can easily pull the fields out as lists, then wrap it all up in a dict
    inputTranspose = list(map(list, zip(*inputFile)))

    output = {"institutionCode": inputTranspose[0][6:-1],
              "institutionName": inputTranspose[1][6:-1],
              "unitOfAssessmentName": inputTranspose[3][6:-1],
              "unitOfAssessmentNum": inputTranspose[4][6:-1],
              "title": inputTranspose[9][6:-1],
              "volumeTitle": inputTranspose[12][6:-1],
              "volume": inputTranspose[13][6:-1],
              "researchGroup": inputTranspose[27][6:-1],
              "citations": inputTranspose[29][6:-1]}
    return output

def processRefCsv(inputPath):
    '''
    Process the REF uni scores file from inputPath that we have generated from excel
    and create a dict using the headers as keys and the values of each column
    as a list for the desired columns
    '''
    inputFile = []
    with open(inputPath, 'r', newline='',
          encoding='utf-8') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read())
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        for row in reader:
            inputFile.append(row)
        csvfile.close()

    headers = inputFile[7]

    inputTranspose = list(map(list, zip(*inputFile)))
    output = {"institutionCode": inputTranspose[0][8:],
              "institutionName": inputTranspose[1][8:],
              "unitOfAssessmentNum": inputTranspose[4][8:],
              "unitOfAssessmentName": inputTranspose[5][8:],
              "profile": inputTranspose[9][8:],
              "staff": inputTranspose[10][8:],
              "fourStar": inputTranspose[11][8:],
              "threeStar": inputTranspose[12][8:],
              "twoStar": inputTranspose[13][8:],
              "oneStar": inputTranspose[14][8:],
              "unclassified": inputTranspose[15][8:]}
    return output

def stripUnused(inputData, keyToRemove, valueToMatch):
    '''
    As we care mostly about the outputs we will remove the impact, environment and overall
    variables from REF data
    '''
    indexToKeep = []
    REFOutputs = {}
    for value, index in zip(inputData[keyToRemove], range(len(inputData[keyToRemove]))):
        if (value == valueToMatch):
            indexToKeep.append(index)

    for key in inputData:
        REFOutputs[key] = [inputData[key][i] for i in indexToKeep]
    return REFOutputs

inputCollection = {}

for file in csvFiles:
    path = csvPath + file
    output = processInputCsv(path)
    inputCollection[file[8:-4]] = output #Strip the number and .csv for the name

REF = processRefCsv(refPath)

pickleOut = open("../../OutputData/outputs/pickles/REF.pickle", "wb")
pk.dump(REF, pickleOut)
pickleOut.close()

pickleOut = open("../../OutputData/outputs/pickles/inputCollection.pickle", "wb")
pk.dump(inputCollection, pickleOut)
pickleOut.close()

fullCollection = pk.load(open("../../OutputData/outputs/pickles/fullCollection.pickle", "rb"))
REF = pk.load(open("../../OutputData/outputs/pickles/REF.pickle", "rb"))

# Remove all values from REF data that aren't outputs or related to chemistry
REFOutputs = stripUnused(REF, 'profile', 'Outputs')

for topic in fullCollection:         # Loop through the keys of the dict (chemistry, physics, etc.)
    fourStarScore = []
    threeStarScore = []
    twoStarScore = []
    oneStarScore = []
    unclassified = []

    REFTopic = stripUnused(REFOutputs, 'unitOfAssessmentName', topic) # Has REF data for each uni based on topic

    for instituteCode in fullCollection[topic]['institutionCode']:
        index = REFTopic['institutionCode'].index(instituteCode)
        fourStarScore.append(REFOutputs['fourStar'][index])
        threeStarScore.append(REFOutputs['threeStar'][index])
        twoStarScore.append(REFOutputs['twoStar'][index])
        oneStarScore.append(REFOutputs['oneStar'][index])
        unclassified.append(REFOutputs['unclassified'][index])

    fullCollection[topic]['fourStar'] = fourStarScore
    fullCollection[topic]['threeStar'] = threeStarScore
    fullCollection[topic]['twoStar'] = twoStarScore
    fullCollection[topic]['oneStar'] = oneStarScore
    fullCollection[topic]['unclassified'] = unclassified

pickleOut = open("../../OutputData/outputs/pickles/fullCollection.pickle", "wb")
pk.dump(fullCollection, pickleOut)
pickleOut.close()

# Remove stopwords and add to our dictionary
for key in fullCollection:
    fullCollection[key]['filteredTitle'] = []
    for title in fullCollection[key]['title']:
        filteredWordList = title.split(" ")
        filteredWordList = [x.lower() for x in filteredWordList]
        for word in filteredWordList: # iterate over word_list
            if word in stopwords.words('english'):
                filteredWordList.remove(word) # remove word from filtered_word_list if it is a stopwor
        fullCollection[key]['filteredTitle'].append(' '.join(filteredWordList))

pickleOut = open("../../OutputData/outputs/pickles/fullCollection.pickle", "wb")
pk.dump(fullCollection, pickleOut)
pickleOut.close()

# Remove stop words and add to a list suitable for parsing with our Hadoop cluster
for key in fullCollection:
    if not os.path.exists('../../OutputData/outputs/csv/processed/' + str(key).replace(" ", "")):
        os.makedirs('../../OutputData/outputs/csv/processed/' + str(key).replace(" ", ""))

    fourStarScores = list(map(float, set(fullCollection[key]['fourStar']))) # Get unique values
    fourStarScores.sort() # Sort the unique values
    topTenValues = list(map(str, fourStarScores[-10:])) # Take the top highes scores for each topic

    with open("../../OutputData/outputs/csv/processed/" + str(key).replace(" ", "") + "/" +
              str(key).replace(" ", "") + "Titles.csv", "w", encoding="utf-8") as csvfile:

        for title, i in zip(fullCollection[key]['title'], range(len(fullCollection[key]['title']))):
            if fullCollection[key]['fourStar'][i] in topTenValues:
                filteredWordList = title.split(" ")
                filteredWordList = [x.lower() for x in filteredWordList]

                for word in filteredWordList: # iterate over word_list
                    if word in stopwords.words('english'):
                        filteredWordList.remove(word) # remove word from filtered_word_list if it is a stopword
                writer = csv.writer(csvfile, delimiter = ' ')
                writer.writerow(filteredWordList)
