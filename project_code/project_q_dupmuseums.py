from pymongo import MongoClient
from pprint import pprint

client = MongoClient('mongodb://127.0.0.1:27017')
db = client.osm

# send a query to find the duplicate museum entries
cursor = db.test.aggregate([
        # the type of entry needs to be a museum and have a name
        {"$match": {'tourism': 'museum',
                    'name': {'$exists': 'true'}}},
        # group the entries by name and count how many occurences are
        {"$group": {"_id": "$name",
                    "count": {"$sum": 1}}},
        # sort in a decreasing order
        {"$sort": {"count": -1}},
        # hold only the entries that are actual duplicates
        {"$match": {'count': {'$gte': 2}}}
    ])

# print the results
names = list()
for doc in cursor:
    print 'count:', doc['count'], '\tname:', doc['_id']
    names.append(doc['_id'])
    
for name in names:
    # launch a query to get the documents for the name
    cursor = db.test.aggregate([
                # find the current name
                {'$match': {'name': name}},
                # sort reverse alphabetically (so 'way' comes before 'node')
                {'$sort':  {'type': -1}}
            ])
    # transform cursor to list - assumption is that first entry will be 
    # 'way', all others will be 'node'
    reslist = list()
    for elem in cursor:
        reslist.append(elem)
    
    # we strip the 'node' of all info but the id, type, created, pos info
    # we add the stripped info to the 'way' element
    tempway = reslist[0].copy()
    HOLD = ('id', 'type', 'created', 'pos', '_id')
    for i in range(1, len(reslist)):
        elem = reslist[i]
        # create a new copy
        tempelem = dict()
        # go through all the keys
        for k in elem.keys():
            if k in HOLD:
                # hold the minimum set of keys for the 'node'
                tempelem[k] = elem[k]
            else:
                # add all the other keys to 'way'
                tempway[k] = elem[k]
    
        # print values:
        print '---original node---'
        pprint(elem)
        print '---new node---'
        pprint(tempelem)
        print ''
        
        # save the new node - uncomment to activate
        #db.test.save(tempelem)
    
    print '---original way---'
    pprint(reslist[0])
    print '---new way---'
    pprint(tempway)
    print '\n\n'
    
    # save the new way - uncomment to activate
    #db.test.save(tempway)