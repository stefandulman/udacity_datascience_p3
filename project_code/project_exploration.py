import xml.etree.cElementTree as ET
import operator
import string
from collections import defaultdict


# helper function - sorts a dictionary on the values and returns it as a list
def sorted_dict(d):
    return sorted(d.items(), key=operator.itemgetter(1))



# count individual element types
def preprocess_counttags(filename):
    # return variable
    mydict = defaultdict(int)
    # open file for reading
    f = open(filename, "r")
        
    # go through all elements and trigger an event at their start
    for _, elem in ET.iterparse(f, events=("start",)):
        mydict[elem.tag] = mydict[elem.tag] + 1
    
    # close file and return a list sorted on values
    f.close()
    
    return sorted_dict(mydict)

print 'tags encountered in the xml file:'
for k,v in preprocess_counttags('../iasi_romania.osm'):
    print 'count:', v, '\ttag name:', k
print ''



# count how many tags have 'type' as a key
def preprocess_counttypekeys(filename):
    # return variables
    count_node = 0
    count_ways = 0
    
    # open file for reading
    f = open(filename, "r")
        
    # go through all elements and trigger an event at their start
    for _, elem in ET.iterparse(f, events=("start",)):
        # count the tags with "type"
        has_type = 0
        for tag in elem.iter('tag'):
            if tag.attrib['k'] == 'type':
                has_type = 1
                break
            
        if elem.tag == 'node':
            count_node = count_node + has_type
            continue
        if elem.tag == 'way':
            count_ways = count_ways + has_type
            continue
    
    # close file and return the computed values
    f.close()
    
    return (count_node, count_ways)

vnode, vways = preprocess_counttypekeys('../iasi_romania.osm')
print '"node" elements with tags named "type":', vnode
print '"way" elements with tags named "type":', vways
print ''


# count how many documents "node" and "way" have tags that overlap
def preprocess_countduplicatetags(filename):
    
    # return variable
    res = dict({'node': 0, 'way': 0})
    
    # open file for reading
    f = open(filename, "r")
    
    # go through all elements and trigger an event at their start
    for _, elem in ET.iterparse(f, events=("start",)):
        
        # temporary variables
        tempdict = defaultdict(int)
        flag = False
        
        # focus only on nodes and ways
        if elem.tag in ('node', 'way'):
            
            # create a dictionary from the tags and stop if an overlap is detected
            for tag in elem.iter('tag'):
                # break if we've seen this key before
                if tempdict[tag.attrib['k']] >= 1:
                    flag = True
                    break
                tempdict[tag.attrib['k']] = tempdict[tag.attrib['k']] + 1
            
            # update return variable
            if flag:
                res[elem.tag] = res[elem.tag] + 1
            
    # close file and return the computed values
    f.close()
    return sorted_dict(res)

print 'duplicate tags appear in:'
for k,v in preprocess_countduplicatetags('../iasi_romania.osm'):
    print 'duplicates:', v, '\tin', k
print ''



# check how many keys overlap with our default tags
DEFAULTTAGS = ( 'pos', 'type', 'id', 'created' )

# count overlapping elements
def preprocess_countoverlappingkeys(filename):
    
    # return variable
    res = dict({'pos': 0, 'type': 0, 'id': 0, 'created': 0})
    
    # open file for reading
    f = open(filename, "r")
    
    # go through all elements and trigger an event at their start
    for _, elem in ET.iterparse(f, events=("start",)):
        
        # focus only on nodes and ways
        if elem.tag in ('node', 'way'):
            
            # check all the keys in these elements
            for tag in elem.iter('tag'):
                if tag.attrib['k'] in DEFAULTTAGS:
                    res[tag.attrib['k']] = res[tag.attrib['k']] + 1
            
    # close file and return the computed values
    f.close()
    return sorted_dict(res)

print 'overlapping keys with default tags:'
for k,v in preprocess_countoverlappingkeys('../iasi_romania.osm'):
    print 'duplicates:', v, '\tfor key', k
print ''


 # check the streetnames
def check_streetnames(filename):
    
    # return variable
    res = defaultdict(int)
    
    # open file for reading
    f = open(filename, "r")
    
    # go through all elements and trigger an event at their start
    for _, elem in ET.iterparse(f, events=("start",)):
        
        # focus only on nodes and ways
        if elem.tag in ('node', 'way'):
            
            # check all the keys in these elements
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'addr:street':
                    streettype = tag.attrib['v'].split(' ')[0]
                    res[streettype] = res[streettype] + 1
            
    # close file and return the computed values
    f.close()
    return sorted_dict(res)

print 'street types:'
for k,v in check_streetnames('../iasi_romania.osm'):
    print 'count:', v, '\tname', k
print ''



ALLOWEDSTREETNAMES = ['Aleea', 'Fundacul', u'Fund\u0103tura', 'Calea', 'Splaiul', 'Stradela', u'\u0218oseaua', 'Bulevardul', 'Strada', u'Pia\u021ba']
REPLACES = ({'Fundac': 'Fundacul', 'Alee': 'Aleea', 'Splai': 'Splaiul'})

# fix a street name
def fix_streetname(name):
    
    # extract the first entry in the word
    splitname = name.split(' ')
    prefix = splitname[0]
        
    # replace abbreviated forms
    newname = name
    if prefix in REPLACES.keys():
        prefix = REPLACES[prefix]
        newname = prefix + ' ' + string.join(splitname[1:])
    
    # check if name is in the allowed list, if not, add "Strada" in front
    if prefix in ALLOWEDSTREETNAMES:
        return newname
    else:
        return 'Strada ' + name


def example_fixstreetnames(filename):
    
    # return variable
    res = []
    
    # open file for reading
    f = open(filename, "r")
    
    # go through all elements and trigger an event at their start
    for _, elem in ET.iterparse(f, events=("start",)):
        
        # focus only on nodes and ways
        if elem.tag in ('node', 'way'):
            
            # check all the keys in these elements
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'addr:street':
                    res.append([tag.attrib['v'], fix_streetname(tag.attrib['v'])])
            
    # close file and return the computed values
    f.close()
    return res

print 'fixing street names'
names = example_fixstreetnames('../iasi_romania.osm')
for i in range(1,10):
    print 'oldname:', names[i][0]
    print 'newname:', names[i][1]
    print ''
    


# process individual phone number
def beautify_phone_nr(number):
    
    # check if phone is in format: "xxxx (int xxx)" and remove the "(int xxx)"
    res = number.split(' (')[0]
    
    # remove the special characters:
    res = res.replace(' ', '')
    res = res.replace('-', '')
    res = res.replace('+', '')
    res = res.replace('.', '')
    res = res.replace('/', '')
    
    # add the country code
    if res[0] == '0':
        res = '+4' + res
    else:
        res = '+' + res
    
    # sanity check - phone numbers can be in the format '+40232...' or '+407...'
    if res[0:6] != '+40232' and res[0:4] != '+407':
        #print 'wrong number:', res
        return None
    
    return res

# check the phone numbers
def check_phones(filename):
    
    # return variable
    res = []
    resold = []
    
    # open file for reading
    f = open(filename, "r")
    
    # go through all elements and trigger an event at their start
    for _, elem in ET.iterparse(f, events=("start",)):
        
        # focus only on nodes and ways
        if elem.tag in ('node', 'way'):
            
            # check all the keys in these elements
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'phone':
                    
                    # several phone numbers are split by ',' or ';'
                    if tag.attrib['v'].find(',') != -1:
                        phonenrs = tag.attrib['v'].split(',')
                    elif tag.attrib['v'].find(';') != -1:
                        phonenrs = tag.attrib['v'].split(';')
                    else:
                        phonenrs = [tag.attrib['v']]
                    
                    # process each phone number
                    temp = []
                    for nr in phonenrs:
                        temp.append(beautify_phone_nr(nr))
                    # update the return variables
                    res.append(temp)
                    resold.append(phonenrs)
            
    # close file and return the computed values
    f.close()
    return (res, resold)

print 'phone numbers:'
phonesnew, phonesold = check_phones('../iasi_romania.osm')
for i in range (0,10): 
    print 'new phone:', phonesnew[i], 'old phone:', phonesold[i]
    print ''
    
