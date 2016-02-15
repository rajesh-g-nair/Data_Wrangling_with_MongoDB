#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import codecs
import json
import re
"""
The function key_type updates the following 2 dictionaries
- A dictionary with count of lower, lower_colon, problemchars and other keys
- A dictionary with distinct keys appearing in the tags

The function process_map iteratively parses the map file and processes them by calling
the key_type function and then writes the data to a json file

"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys, distinct_tag_attrib):
    if element.tag == "tag":
        l = lower.search(element.attrib['k'])
        lc = lower_colon.search(element.attrib['k'])
        pc = problemchars.search(element.attrib['k'])
        if l:
            keys["lower"] += 1
        elif lc:
            keys["lower_colon"] += 1
        elif pc:
            keys["problemchars"] += 1
        else:
            keys["other"] += 1
        if element.attrib['k'] in distinct_tag_attrib.keys():
            distinct_tag_attrib[element.attrib['k']] += 1
        else:
            distinct_tag_attrib[element.attrib['k']] = 1
    return keys, distinct_tag_attrib


def process_map(filename):
    file_out = "{0}_tags.json".format(filename)    
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    distinct_tag_attrib ={}
    with codecs.open(file_out, "w") as fo:    
        for _, element in ET.iterparse(filename):
            keys, distinct_tag_attrib = key_type(element, keys, distinct_tag_attrib)
        fo.write(json.dumps(distinct_tag_attrib, indent=2)+"\n")
        fo.write(json.dumps(keys, indent=2)+"\n")
    return keys, distinct_tag_attrib

def main_task():
    keys, distinct_tag_attrib = process_map('C:\Rajesh\open_street_map_project\mumbai_india\mumbai_india.osm')
    pprint.pprint(keys)
    pprint.pprint(distinct_tag_attrib)


if __name__ == "__main__":
    main_task()