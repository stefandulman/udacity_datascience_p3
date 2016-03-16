import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import string

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
ALLOWEDSTREETNAMES = ['Aleea', 'Fundacul', u'Fund\u0103tura', 'Calea', 'Splaiul', 'Stradela', u'\u0218oseaua', 'Bulevardul', 'Strada']
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



def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        
        # add the type of tag
        node['type'] = element.tag
        
        # deal with the attributes
        created = {}
        pos = {}
        for k,v in element.items():
            if k in CREATED:
                created[k] = v
                continue
            if k in ['lat', 'lon']:
                pos[k] = float(v)
                continue
            node[k] = v
        node['created'] = created
        if len(pos.keys()) > 0:
          node['pos'] = [pos['lat'], pos['lon']]
        
        # deal with the embedded tags
        for tag in element.iter():
            # deal with "tag"
            if tag.tag == 'tag':
                # ignore problematic ones
                if problemchars.search(tag.attrib['k']):
                    continue
                # deal with "addr:"
                pieces = tag.attrib['k'].split(':')
                if pieces[0] == 'addr':
                    # ignore the ones like 'addr:xxx:xxx...'
                    if len(pieces) >= 3:
                        continue
                    # deal with the ones like 'addr:xxx'
                    if 'address' not in node.keys():
                        node['address'] = dict()
                    # beautify street names
                    if pieces[1] == 'street':
                        node['address']['street'] = fix_streetname(tag.attrib['v'])
                    else:
                        node['address'][pieces[1]] = tag.attrib['v']
                    continue
                else:
                    # does it contain a ":"?
                    if len(pieces) == 1:
                        # check if overwritting the "type" element
                        if tag.attrib['k'] == 'type':
                            node['tag_type'] = tag.attrib['v']
                        # check if phone number
                        elif tag.attrib['k'] == 'phone': 
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
                            node['phone'] = temp
                        else:
                            node[tag.attrib['k']] = tag.attrib['v']
                        continue
                    else:
                        node[tag.attrib['k'].replace(':','_')] = tag.attrib['v']
                        continue
            
            # deal with "nd"
            if tag.tag == 'nd':
                if 'node_refs' not in node.keys():
                    node['node_refs'] = []
                node['node_refs'].append(tag.attrib['ref'])
        
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


data = process_map('../iasi_romania.osm', False)
pprint.pprint(data[0])
