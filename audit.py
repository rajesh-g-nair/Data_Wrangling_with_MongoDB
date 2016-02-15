"""
This exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list. Also the audit function returns a list of Postal codes
    The street names having problems and needs to be corrected are added to the mappings dictionary as the key with the corrected name as its value,
- The update_name function is used to actually fix the street name.
    The function takes a string with street name as an argument returns the fixed name
    The update_post_code function is used to correct the Postal codes
    
The List "expected" contains the list of street name endings which are expected

The "mapping" dictionary is used to store the mapping to correct the street names

   
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "C:\Rajesh\open_street_map_project\mumbai_india\mumbai_india.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", 
            "Trail", "Parkway", "Commons","West)","Nagar","Naka","Mumbai","Marg","Road","Chowk","East)","Highway", "Estate","Multiplex","Ghatkopar","Kharghar","Path","Point","Wadi","Society","Raigad", "Powai", "Colony"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Rd": "Road",
            "Raod": "Road",
            "ROAD": "Road",
            "E)" : "East)",
            "Easr" : "(East)",
            "East" : "(East)",
            "East," : " (East)",
            "W)": "West)",
            "west": "(West)",
            "West,": "(West)",
            "WEST" : "(West)",
            "nagar": "Nagar",
            "Chouk": "Chowk",
            "marg": "Marg"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_int(check_int):
    try:
        int(check_int)
        return True
    except:
        return False
    
def audit_post_code(post_codes, post_code):
    if len(post_code.strip()) != 6 or not is_int(post_code) or not post_code.startswith('4'):
        post_codes.append(post_code)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode" or elem.attrib['k'] == "postal_code")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    post_code = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_post_code(tag):
                    audit_post_code(post_code,tag.attrib['v'])
    return street_types, post_code


def update_name(name, mapping):

    for key in mapping.keys():
        stpos = name.find(key)
        if stpos != -1:
            name = name.replace(key,mapping[key])
            break
    return name

def update_post_code(post_code):
    post_code=post_code.strip('.')
    post_code=post_code.replace('o','0')
    post_code=post_code.replace(' ','')
    if is_int(post_code):
        stpos=len(post_code) 
    else:
        stpos = post_code.find(",") -1
    if len(post_code[1:stpos]) >= 6:
        if int(post_code[1:stpos]) < 10:
            post_code=post_code[:1] + '0000' + post_code[-1:]
        elif int(post_code[1:stpos]) >= 10 and int(post_code[1:stpos]) < 100:
            post_code=post_code[:1] + '000' + post_code[-2:]
        elif int(post_code[1:stpos]) >= 100 and  int(post_code[1:stpos]) < 1000:    
            post_code=post_code[:1] + '00' + post_code[-3:]
    elif len(post_code[1:stpos]) < 6:
        if post_code.startswith('4') and len(post_code)==5:
            post_code = "4" + post_code[2:].zfill(5)
        elif len(post_code) == 2:
            post_code = '4000' + post_code
    post_code=post_code[:6]
    return post_code

def audit_data():
    st_types, post_codes = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    pprint.pprint(post_codes)

    for st_type, ways in st_types.iteritems():
        for name in ways:
            if st_type in mapping.keys():
                better_name = update_name(name, mapping)
                print name, "=>", better_name
    for post_code in post_codes:
        corrected_post_code = update_post_code(post_code)        
        if len(corrected_post_code) == 6 and corrected_post_code.startswith('4'):        
            print post_code, "=>", corrected_post_code 
        else:
            print "Invalid Post code", "=>", post_code
if __name__ == '__main__':
    audit_data()