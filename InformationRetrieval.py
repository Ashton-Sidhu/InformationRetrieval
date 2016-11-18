
# coding: utf-8

# In[1]:

from whoosh import index, writing
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import *
from whoosh.qparser import QueryParser
import os, os.path
import shutil


# In[2]:

DOCUMENTS_DIR = "/resources/data/DSS_Fall2016_Assign1/government/documents"
INDEX_DIR = "/resources/data/DSS_Fall2016_Assign1/government/index1"
QUER_FILE = "/resources/data/DSS_Fall2016_Assign1/government/topics/gov.topics"
QRELS_FILE = "/resources/data/DSS_Fall2016_Assign1/government/qrels/gov.qrels"
OUTPUT_FILE = "/resources/data/DSS_Fall2016_Assign1/government/myres"
TREC_EVAL = "/resources/data/DSS_Fall2016_Assign1/trec_eval.8.1/trec_eval"
INDEX_DIR2 = "/resources/data/DSS_Fall2016_Assign1/government/index2"
OUTPUT_FILE2 = "/resources/data/DSS_Fall2016_Assign1/government/myres2"


# In[3]:

# first, define a Schema for the index
mySchema = Schema(file_path = ID(stored=True),
                  file_content = TEXT(analyzer = RegexTokenizer()))

# if index exists - remove it
if os.path.isdir(INDEX_DIR):
    shutil.rmtree(INDEX_DIR)

# create the directory for the index
os.makedirs(INDEX_DIR)

# create index
myIndex = index.create_in(INDEX_DIR, mySchema)


# In[4]:

# first we build a list of all the full paths of the files in DOCUMENTS_DIR
filesToIndex = []
for root, dirs, files in os.walk(DOCUMENTS_DIR):    
    filePaths = [os.path.join(root, fileName) for fileName in files if not fileName.startswith('.')]
    filesToIndex.extend(filePaths)


# In[5]:

# open writer
myWriter = writing.BufferedWriter(myIndex, period=20, limit=1000)

try:
    # write each file to index
    for docNum, filePath in enumerate(filesToIndex):
        with open(filePath, "r") as f:
            fileContent = f.read()
            myWriter.add_document(file_path = filePath,
                                  file_content = fileContent)
            
            if (docNum % 1000 == 0):
                print("already indexed:", docNum+1)
    print("done indexing.")

finally:
    # save the index
    myWriter.close()


# In[6]:

# define a query parser for the field "file_content" in the index
myQueryParser = QueryParser("file_content", schema=myIndex.schema)
mySearcher = myIndex.searcher()


# In[7]:

topicsFile = open(QUER_FILE,"r")
topics = topicsFile.read().splitlines()

# create an output file to which we'll write our results
outputTRECFile = open(OUTPUT_FILE, "w")

# for each evaluated topic:
# build a query and record the results in the file in TREC_EVAL format
for topic in topics:
    topic_id, topic_phrase = tuple(topic.split(" ", 1))
    topicQuery = myQueryParser.parse(topic_phrase)
    topicResults = mySearcher.search(topicQuery, limit=None)
    for (docnum, result) in enumerate(topicResults):
        score = topicResults.score(docnum)
        outputTRECFile.write("%s Q0 %s %d %lf test\n" % (topic_id, os.path.basename(result["file_path"]), docnum, score))

# close the topic and results file
outputTRECFile.close()
topicsFile.close()


# In[8]:


get_ipython().system(u'$TREC_EVAL -q $QRELS_FILE $OUTPUT_FILE')


# Q1: 
# a) Recall (Num of relevant retrieved documents/number of relevant documents) or interpolated recall is best suited for the government website.
# 
# b) Number of retrieved documents is the most appropriate because based on the queries the user(s) are looking for all relevant data on the subject would want to be returned. 
#     

# Q2:
# a) num_rel_ret/num_rel = 7/33 = .21
# 
# b) Topics 18,24,14 did well, while  topics 7,16,28 did poorly.

# In[9]:

stmLwrStpIntraAnalyzer = RegexTokenizer() | LowercaseFilter() | IntraWordFilter() | StopFilter()

mySchema2 = Schema(file_path = ID(stored=True),
                   file_content = TEXT(analyzer = stmLwrStpIntraAnalyzer))

# if index exists - remove it
if os.path.isdir(INDEX_DIR2):
    shutil.rmtree(INDEX_DIR2)

# create the directory for the index
os.makedirs(INDEX_DIR2)

# create index or open it if already exists
myIndex2 = index.create_in(INDEX_DIR2, mySchema2)


# In[10]:

# open writer
myWriter2 = writing.BufferedWriter(myIndex2, period=20, limit=1000)

try:
    # write each file to index
    for docNum, filePath in enumerate(filesToIndex):
        with open(filePath, "r") as f:
            fileContent = f.read()
            myWriter2.add_document(file_path = filePath,
                                  file_content = fileContent)
            
            if (docNum % 1000 == 0):
                print("already indexed:", docNum+1)
    print("done indexing.")

finally:
    # save the index
    myWriter2.close()


# In[11]:

# define a query parser for the field "file_content" in the index
myQueryParser2 = QueryParser("file_content", schema=myIndex2.schema)
mySearcher2 = myIndex2.searcher()

# Load topic file - a list of topics(search phrases) used for evalutation
topicsFile = open(QUER_FILE,"r")
topics = topicsFile.read().splitlines()

# create an output file to which we'll write our results
outputTRECFile2 = open(OUTPUT_FILE2, "w")

# for each evaluated topic:
# build a query and record the results in the file in TREC_EVAL format
for topic in topics:
    topic_id, topic_phrase = tuple(topic.split(" ", 1))
    topicQuery = myQueryParser2.parse(topic_phrase)
    topicResults = mySearcher2.search(topicQuery, limit=None)
    for (docnum, result) in enumerate(topicResults):
        score = topicResults.score(docnum)
        outputTRECFile2.write("%s Q0 %s %d %lf test\n" % (topic_id, os.path.basename(result["file_path"]), docnum, score))

# close the topic and results file
outputTRECFile2.close()
topicsFile.close()


# In[12]:

get_ipython().system(u'$TREC_EVAL -q $QRELS_FILE $OUTPUT_FILE2')


# Q3:
# a) Lowercasing and getting rid of stop words such as "the", "are", "is" etc. would improve the search filter. By getting rid of some of the words that don't provide context the documents will then match better in accordance with the more unique words. Splitting up words that are joined by a period or a comma will also provide a better search.
# 
# b) I made every word lowercase and stripped all useless words such as "the", "are", "is" etc from the document. I also split up words that had were considered one word due to a period or a comma.
# 
# c) Yes .34 compares to .21.
# 
# d) Yes some queries got better (like topic 2 and 28) while most others stayed the same according to my metric. Topic 19 had a recall of .5  with the improvements, compared to not being recognized when we just used Whoosh baseline.
# 
# e) I believe this means my idea was good. The queries were more so looking for breadth and any document that was relevant to their search topic, so the more that we can return the more data the user has to look at.

# In[ ]:



