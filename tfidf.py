# SOURCES
#http://docs.python-requests.org/en/latest/user/quickstart/

# IMPORTS
from kafka import KafkaConsumer
from collections import Counter
from operator import itemgetter
from math import log
import csv

# CONSTANTS
KAFKA_TOPIC = 'articles2'
KAFKA_GROUP = 'my-group'
KAFKA_PORT = 'localhost:9092'
COMPANIES_FILE = "companies.txt"
def readCompanies():
  f = open(COMPANIES_FILE, 'r')
  companies = f.read().split("\n")
  f.close()
  return companies
COMPANIES = readCompanies()
NUM_KEYWORD_CANDIDATES_PER_COMPANY = 100
NUM_KEYWORDS_PER_COMPANY = 4
INPUTFILENAME = "1_1_16.csv"
OUTPUTFILENAME = "keywords.txt"

# FUNCTIONS
def readCSV():
  articles = []
  with open(INPUTFILENAME, 'r') as inputFile:
    reader = csv.DictReader(inputFile)
    for row in reader:
      text = row.pop("text")
      articles.append({ "text": text, 
                  "companies": row})
  return articles

def kafkaStream(topic, group = KAFKA_GROUP, port = KAFKA_PORT):
  print "Initiating Kafka"
  return  KafkaConsumer(topic,
      group_id=group,
      bootstrap_servers=[port])

# returns a list of {text, companies}
#   where companies is a dict of booleans
def getFromTopic(topic):
  data = []
  for message in kafkaStream(topic=topic):
    print message.value
    if message.value == "END":
      print "Finished reading from Kafka"
      return data
    data.append({ "text": message.key, 
                  "companies": strToDictOfBools(message.value)})

# converts a dict of space-separated key:val pairs to a dict
  # where the value of each pair is a boolean
def strToDictOfBools(s):
  d = {}
  pairs = [k_v.split(":") for k_v in s.split(' ')]
  for pair in pairs:
    d[pair[0]] = strToBool(pair[1])
  return d

def strToBool(b):
  return b=="True"

# returns list of abstracts for each article of that company
def getText(company, articles):
  text = []
  if company is None:
    print "Getting all text"
  else:
    print "Getting text for " + company
  for article in articles:
    if company is None or article["companies"][company]:
      text.append(article["text"])  #extend vs append?
  return text

def tfidf(word, freq, maxFreq, docText, allText):
  tf = freq/maxFreq
  idf = log(len(allText)/numDocswWord(docText, word))
  print str(freq) + " " + str(maxFreq) + " " + str(len(allText)) + " " + str(numDocswWord(docText, word))
  return tf * idf

# sorted by frequency
def wordFrequencies(docText):
  return Counter(docText).most_common(NUM_KEYWORD_CANDIDATES_PER_COMPANY)

def numDocswWord(docs, word):
  count = 0
  for doc in docs:
    if word in doc:
      count = count + 1
  return count

# generates all tfidfs for a company in a set of articles
def tfidfsForCompany(company, articles):
  companyText = getText(company, articles)
  words = set(" ".join(companyText).split(" "))
  wordfreqs = wordFrequencies(words)
  print wordfreqs
  maxFreq = wordfreqs[0][1]  #1st elem's val (freq of most common word)
  tfIDFs = {}
  for wordfreq in wordfreqs:
    word = wordfreq[0]
    freq = wordfreq[1]
    tfIDFs[word] = tfidf(word, freq, maxFreq, companyText, allText)
  return tfIDFs

# returns a list of tuples, not a dict
def sortDictByValue(d):
  return sorted(d.items(), key=itemgetter(1))

def outputKeywords(keywords):
  outputFile = open(OUTPUTFILENAME, 'wb')
  for keyword in keywords:
    outputFile.write(keyword+"\n")
  print "Wrote keywords to " + OUTPUTFILENAME

# MAIN METHOD
if __name__ == "__main__":
  #articles = getFromTopic(KAFKA_TOPIC)
  articles = readCSV()
  allText = getText(None, articles)
  tfIDFs = {}
  keywords = set()
  for company in COMPANIES:
    tfIDFs[company] = tfidfsForCompany(company, articles)
    sorted_tfIDFs = sortDictByValue(tfIDFs[company])
    for i in range(NUM_KEYWORDS_PER_COMPANY):
      keyword = sorted_tfIDFs[i][0]
      print "Keyword: " + keyword
      keywords.update(keyword)
  outputKeywords(keywords)