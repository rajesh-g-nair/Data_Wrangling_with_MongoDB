#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint

"""
The function process_map returns a set of unique user IDs 
and a dictionary with user id as the key and count of the user
as the value

The function get_user is used to get the user id for the element

The function print_users is used to print the list of distinct users
and the dictionary of users with count

"""

def get_user(element):
    user = ""
    dict_element_attribs = element.attrib
    for key in dict_element_attribs.keys():
        if key == "user":
            user = element.attrib[key]
    return user


def process_map(filename):
    users = set()
    user_count = {}
    for _, element in ET.iterparse(filename):
        user=get_user(element)
        if user != "":
            users.add(user)
        if user not in user_count.keys():
            user_count[user] = 1
        else:
            user_count[user] +=1
    return users, user_count


def print_users():

    users, user_count = process_map("C:\Rajesh\open_street_map_project\mumbai_india\mumbai_india.osm")
    pprint.pprint(users)
    pprint.pprint(user_count)

if __name__ == "__main__":
    print_users()