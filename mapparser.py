#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The iterative parsing has been used to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data to expect in the map.
The output is a dictionary with the tag name as the key
and number of times this tag can be encountered in the map as value.

The function count_tags iteratively parses the map file and returns the 
dictionary with tag name as the key and number of times this tag is encountered 
as the value

The funtion print_tags prints the tags on the screen

"""
import xml.etree.ElementTree as ET
import pprint

def count_tags(filename):
    dict_tags = {}    
    for event, elem in ET.iterparse(filename,events=("start","end")):
        if elem.tag in dict_tags.keys():
            dict_tags[elem.tag] += 1
        else:
            dict_tags[elem.tag] = 1
        if event == "end":
            elem.clear()
    return dict_tags

def print_tags():

    tags = count_tags('C:\Rajesh\open_street_map_project\mumbai_india\mumbai_india.osm')
    pprint.pprint(tags)

if __name__ == "__main__":
    print_tags()