#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import re
import codecs
import json
"""
The following lists have been used in the Program
CREATED : This list stores all the keys which form part of created sub document
IGNORE_KEYS : This list stores all the keys that needs to be ignored while creating the JSON document
AMENITY : This list stores all the keys which form part of amenity sub document
ALT_NAMES : This list stores all the keys which will be added to the alt_names List of the JSON document

The "mapping" dictionary is used to store the mapping to correct the street names

The "process_map" function is used to parse the map file and produce the output in JSON file format

The "shape_element" function takes element as an argument. It returns a dictionary containing the 
shaped data for that element.

The "is_int" function is used to check if the argument passed is an integer

The "update_post_code" function is used to correct the Postal codes

The "update_street_name" function is used to correct the Street name

The following things should be done:
- 3 types of top level tags "node", "way" and "relation" are being processed
- all attributes of "node", "way" and "relation" are turned into regular key/value pairs, except:
    - attributes in the CREATED array are added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Values inside "pos" array are floats
- if the second level tag name is "tag" then
    - if second level tag "k" value contains problematic characters, it has been ignored
    - if second level tag "k" value is in the IGNORE_KEYS list then it has been ignored
    - all other second level tag "k" values are processed in the function "process_tag_element"
- if the second level tag name is "nd" then it is added to the "node_refs" array of "way" type
- if the second level tag name is "member" then it is added to the "members" array of "relation" type

The function "process_tag_element" is used to process the second level tag "k" values
Following is the logic used in this function
    - if second level tag "k" value starts with "addr:", it is added to a dictionary "address"
    - if second level tag "k" value is "postal_code" then it is added to dictionary "address" with key as "postcode"
    - if second level tag "k" value is "name:", then if the key value after ":" is not in ('pt','pl','jbo') then it is 
      added to the dictionary native_names
    - if second level tag "k" value is in ALT_NAMES, then it is added to "alt_names" list
    - if second level tag "k" value starts with "is_in" then it is added to dictionary "is_in"
    - if second level tag "k" value starts with "seamark" then it is added to the dictionary "seamark". If the word 
      after ":" contains ":" then it is replaces with "_"
    - if second level tag "k" value starts with "fuel" then it is added to the dictionary "fuel_type"
    - if second level tag "k" value starts with "building" then it is added to the dictionary "building"
    - if second level tag "k" value starts with "internet_access" then it is added to the dictionary "internet_access"
    - if second level tag "k" value is "amenity" or is in the AMENITY List then it is added to the dictionary "amenity"
    - all the other second level tag "k" value is processed by replacing ":" with "_" and adding it as a key  

"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
IGNORE_KEYS=["gns", "WDPA", "communication", "Sector", "diplomatic", "mangeshi dham","mangeshi dham", "Mangeshi Dham", "business Park", "contact", "leaf_cycle", "nearyouu", "place:", "ship:type", "Cable TV Provider", "EState Consultants", "earthquake:damage", "Golden Park", "mtb:scale", "oneway:bicycle", "alt_name:", "namePREAM SHARMA COMMUNICATION","name:pt", "name:pl", "name:jbo","turn:lanes","wikipedia:","population:","nerul","Laxmi Tower CHS","Mahesh Jain"]
AMENITY = ["religion", "denomination", "cuisine","opening_hours", "capacity","smoking","covered", "designation", "toilets:disposal","social_facility","social_facility:for"]
ALT_NAMES = ["new_name","old_name","alt_name","alternative_name"]

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

def is_int(check_int):
    try:
        int(check_int)
        return True
    except:
        return False

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

def update_street_name(name, mapping):

    for key in mapping.keys():
        stpos = name.find(key)
        if stpos != -1:
            name = name.replace(key,mapping[key])
            break
    return name
def process_tag_element(tag_name,node):
   # Processing the keys starting with "addr" for the address components 
   # of the tag
   # It is added as a dictionary "address" of the node
   if tag_name.attrib["k"].startswith("addr"):
            if "address" not in node.keys():
                node["address"]={}
            stcnt = tag_name.attrib["k"].count(":")
            if stcnt == 1:
                stpos = tag_name.attrib["k"].find(":")
                key = tag_name.attrib["k"][stpos + 1:]
                value = tag_name.attrib["v"]                            
                if key == "postcode":
                    value=update_post_code(tag_name.attrib["v"])   
                    if not (len(value) == 6 and value.startswith('4')):        
                        value = "Invalid Post code => " +  tag_name.attrib["v"]
                if key == "street":
                    value = update_street_name(value, mapping)
                node["address"][key]=value

   # Processing the "postal_code" keys of the tag
   # It is treated as the postal code key of the dictionary "address" of the node
   elif tag_name.attrib["k"]=="postal_code":
        if "address" not in node.keys():
            node["address"]={}
        value=update_post_code(tag_name.attrib["v"])   
        if not (len(value) == 6 and value.startswith('4')):        
            value = "Invalid Post code => " + tag_name.attrib["v"]
        node["address"]["postcode"]=value             

   # Processing the keys starting with "name" of the tag
   # If there are no colon (:) then the "name" key of the node is assigned the value of the key
   # If there is one colon (:) then the keys "pt","pl","jbo" are ignored. The rest are
   # added as attributes of the "native_names" dictionary of the node
   elif tag_name.attrib["k"].startswith("name"):
        stcnt = tag_name.attrib["k"].count(":")
        if stcnt == 0:
            node["name"]= tag_name.attrib["v"]                        
        if stcnt == 1:
            if "native_names" not in node.keys():
                node["native_names"]={}
            stpos = tag_name.attrib["k"].find(":")
            key = tag_name.attrib["k"][stpos + 1:]
            if key not in ('pt','pl','jbo'):
                node["native_names"][key]=tag_name.attrib["v"]                   

   # Processing the keys which are for one of the Alternative names (keys are one of the ALT_NAMES array)  
   # of the tag
   # It is added to the "alt_names" array of the node
   elif tag_name.attrib["k"] in ALT_NAMES:
        if "alt_names" not in node.keys():
            node["alt_names"]=[]
        node["alt_names"].append(tag_name.attrib["v"])                                                

   # Processing the keys starting with "is_in" of the tag
   # It is added as a dictionary "is_in" of the node. If there is no colon after
   # "is_in" then it is added as the "is_part_of" key else it is added
   # added as the key of "is_in" dictionary of the node
   elif tag_name.attrib["k"].startswith("is_in"):
        if "is_in" not in node.keys():
            node["is_in"]={}
        stpos = tag_name.attrib["v"].find(",")    
        if stpos == -1:
            value=tag_name.attrib["v"]    
        else:
            value=tag_name.attrib["v"][:stpos - 1]    
        stcnt = tag_name.attrib["k"].count(":")
        if stcnt == 0:
            node["is_in"]["is_part_of"]= value
        if stcnt == 1:
            stpos = tag_name.attrib["k"].find(":")
            key = tag_name.attrib["k"][stpos + 1:]
            # correcting the key name for "country" as there is no concept of "county" in Mumbai
            if key == 'county':
                key = 'country'
            node["is_in"][key]=value         

   # Processing the keys starting with "seamark" of the tag 
   # It is added as a dictionary "seamark" of the node. If there is a colon (":")
   # after the first then they are replaced with a underscore("_") and the entire string
   # after the first colon is added as the key of the seamark dictionary
   elif tag_name.attrib["k"].startswith("seamark"):
        if "seamark" not in node.keys():
            node["seamark"]={}
        stpos = tag_name.attrib["k"].find(":")
        key = tag_name.attrib["k"][stpos + 1:]
        key = key.replace(":","_")                        
        node["seamark"][key]=tag_name.attrib["v"]                            
   
   # Processing the keys starting with "fuel" of the tag 
   # It is added as an array "fuel_type" of the node
   elif tag_name.attrib["k"].startswith("fuel"):
        if "fuel_type" not in node.keys():
            node["fuel_type"]=[]
        stcnt = tag_name.attrib["k"].count(":")
        if stcnt == 1:
            stpos = tag_name.attrib["k"].find(":")
            if tag_name.attrib["v"].upper().startswith("Y"):                           
                    node["fuel_type"] = tag_name.attrib["k"][stpos + 1:]
   
   # Processing the keys starting with "building" of the tag 
   # It is added as a dictionary "building" of the node. If there is no colon (":")
   # then the value is added to the "type" attribute of the "building". If the values is
   # "yes" then the value of "building" is assigned. If there is a colon(":") then the
   # word after the ":" is added as the key of the building dictionary
   elif tag_name.attrib["k"].startswith("building"):
        if "building" not in node.keys():
            node["building"]={}
        stcnt = tag_name.attrib["k"].count(":")
        if stcnt == 0:
            if tag_name.attrib["v"] == "yes":
                node["building"]["type"]= "building"
            else:    
                node["building"]["type"]= tag_name.attrib["v"]
        if stcnt == 1:
            stpos = tag_name.attrib["k"].find(":")
            key = tag_name.attrib["k"][stpos + 1:]
            node["building"][key]=tag_name.attrib["v"] 
   
   # Processing the keys starting with "internet_access" of the tag 
   # It is added as a dictionary "internet_access" of the node. If there is no colon (":")
   # then the value is added to the "available" attribute of the "internet_access". 
   # If the values is "no" then the value of "available" attribute is set to "no"
   # else it is set to "yes". If there is a colon(":") then the
   # word after the ":" is added as the key of the internet_access dictionary   
   elif tag_name.attrib["k"].startswith("internet_access"):
        if "internet_access" not in node.keys():
            node["internet_access"]={}
        stcnt = tag_name.attrib["k"].count(":")
        if stcnt == 0:
            if tag_name.attrib["v"] == "no":
                node["internet_access"]["available"]= tag_name.attrib["v"]    
            else:
                node["internet_access"]["available"]= "yes"    
        if stcnt == 1:
            stpos = tag_name.attrib["k"].find(":")
            key = tag_name.attrib["k"][stpos + 1:]
            node["internet_access"][key]=tag_name.attrib["v"] 
   
   # Processing the "amenity" key of the tag
   # It is added as "type" key of the dictionary "amenity" of the node
   elif tag_name.attrib["k"]=="amenity":                                    
       if "amenity" not in node.keys():
           node["amenity"]={}
       node["amenity"]["type"]=tag_name.attrib["v"]    
   
   # Processing the other keys pertaining to the "amenity" dictionary of the node
   # The keys of the "amenity" dictionary are identified by the "AMENITY" array
   # If there is a colon (":") after the first then they are replaced with 
   # a underscore("_") and the entire string after the first colon is added 
   # as the key of the amenity dictionary and the values are added by transforming
   # them as lower   
   elif (tag_name.attrib["k"] in AMENITY):                                    
       if "amenity" not in node.keys():
           node["amenity"]={}
       key = tag_name.attrib["k"].replace(':','_')    
       node["amenity"][key] = tag_name.attrib["v"].lower()

   # Rest of the keys of the tag are processed by replacing ":" with "_" and 
   # adding it as a key of the node
   # If the key name is "type" then it is renamed as "tag_type" as we are using
   # "type" key to identify the node type "node", "way" and "relation"
   else:
       key = tag_name.attrib["k"].replace(':','_')   
       if key == "type":
           key = "tag_type"
       node[key]=tag_name.attrib["v"]
   return node

def shape_element(element):
    node = {}
    element_attrib = {}
    node["created"]={}
    if element.tag == "node" or element.tag == "way" or element.tag == "relation":
        node["type"]=element.tag
        if element.tag == "node":
            node["pos"]=[]
        element_attrib = element.attrib
        
        # if the key is latitude then insert it as the first value of the "pos" array
        # if the key is longitude then insert it as the second value of the "pos" array        
        for key in element_attrib.keys():
            if key == 'lat':
                node["pos"].insert(0,float(element_attrib[key]))
            elif key == 'lon':
                node["pos"].insert(1, float(element_attrib[key]))    
            elif key in CREATED:
                node["created"][key] = element_attrib[key]
            else:
                node[key] = element_attrib[key]
        
        # Processing the second level tags of node, way and relation elements                
        for tag_name in element.iter():
            tag_ignore = None            
            if tag_name.tag == "tag":
                
                # ignore the tags which have problematic characters for processing                
                m=problemchars.search(tag_name.attrib["k"])
                if not m:
                   
                   # ignore the tags which are in IGNORE_KEYS array for processing
                   for word in IGNORE_KEYS:
                       if tag_name.attrib["k"].startswith(word):
                           tag_ignore= tag_name.attrib["k"]                            
                   if tag_ignore != None:
                       continue
                   else:
                       # processing logic for the tags which have the tag name as "tag"
                       node=process_tag_element(tag_name,node)
            elif tag_name.tag == "nd":
                if "node_refs" not in node.keys():
                    node["node_refs"] = []
                node["node_refs"].append(tag_name.attrib["ref"])
            elif tag_name.tag == "member":
                if "members" not in node.keys():
                    node["members"] = []
                node["members"].append(tag_name.attrib)    
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
                    
if __name__ == "__main__":
    process_map('C:\Rajesh\open_street_map_project\mumbai_india\mumbai_india.osm', False)