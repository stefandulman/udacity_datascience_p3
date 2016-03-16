from pymongo import MongoClient
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt

client = MongoClient('mongodb://127.0.0.1:27017')
db = client.osm

# count the documents in the database
print 'number of documents in the database', db.test.find().count()
print 'number of "node" documents', db.test.find({'type': 'node'}).count()
print 'number of "way" documents', db.test.find({'type': 'way'}).count()

# try to figure out why is there a mismatch
cursor = db.test.aggregate([
        {'$group': {'_id': '$type',
                    'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}])
for d in cursor:
    print d
print ''

# look at the statistics of users who contributed to the database
cursor = db.test.aggregate([
        {'$group': {'_id': '$created.user',
                    'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}])
mylist = list()
counter = 0
for d in cursor:
    # store the data in a list
    mylist.append(d['count'])
    # print the first ten most active contributors
    if counter < 10:
        print d
        counter = counter + 1

# draw the histogram users/documents
plt.figure(figsize=(14, 4))
plt.title('User contribution to OpenStreetMap for Iasi')
plt.hist(np.log10(np.array(mylist)), alpha=0.3, color='blue')
plt.xlabel('Log10(number of documents contributed)')
bogus = plt.ylabel('Number of users')
plt.show()