import xml.etree.cElementTree as ET
from collections import defaultdict
# attributes that get displayed as a name
NAMES = ['name', 'addr:housenumber', 'addr:housename', 'addr:postcode', 
         'addr:street', 'place_name', 'operator', 'man_made', 'source', 'building:levels']
# function returns a dictionary of unnamed tourism buildings: (identifier, type)
def getIdsUnnamedLandmarks(osmfile):
    additionalTagSet = defaultdict(list)
    f = open(osmfile, "r")
    # go through all elements and trigger an event at their start
    for _, elem in ET.iterparse(f, events=("start",)):
        # we are interested only in the 'way' elements
        if elem.tag != "way":
            continue
        # go through the tags and detect if it is a building, has no name and has other tags 
        isBuilding = False
        hasName = False
        tempList = list()
        for tag in elem.iter('tag'):
            # does it have a name or a house number?
            if tag.attrib['k'] in NAMES:
                hasName = True
                break        
            # is it a building?
            if tag.attrib['k'] == 'building':
                isBuilding = True
                continue
            # is this another tag? store it temporarily
            tempList.append((tag.attrib['k'], tag.attrib['v']))
        # shall we consider this element?
        if not isBuilding or hasName or len(tempList)==0:
            continue
        # add this entry to the dictionary
        additionalTagSet[str(tempList)].append(elem.attrib['id'])
    f.close()
    return additionalTagSet
# custom 'pretty' print our findings
vals = getIdsUnnamedLandmarks('../iasi_romania.osm')
for k, v in dict(vals).items():
    print 'tags:', k
    print 'ids:', list(v), '\n'