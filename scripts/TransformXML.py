#!/usr/bin/python3
#! -*- coding: utf-8 -*-

from typing import Dict
from xml.etree import cElementTree as ET
import json
import os
import sys

ENTRY_METHODS = ['onCreate', 'onStart', 'onResume']

def transform_xml(xml_path: str):
    print("Loading XML...")
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml = ET.parse(f)
    print("Load XML OK!")

    activities = set([x.attrib.get('source').strip() \
        for x in xml.findall('Component')])
    
    intent_summaries = xml.findall('.//intentSummary')
    summary: Dict[str, list] = dict()
    for activity in activities:
        summary[activity] = []
    
    id = 0
    for intent_summary in intent_summaries:
        method = intent_summary.find('method').attrib.get('value')
        entry_flag = False
        for entry in ENTRY_METHODS:
            if entry in method and intent_summary.find('receiver') != None:
                entry_flag = True
                break
        if entry_flag:
            path_dic = {
                'id': f"path{id}"
            }
            id += 1
            activity = intent_summary.find('source').attrib.get('name')
            method_trace = intent_summary.find('methodtrace').attrib.get('value')
            path_dic['trace'] = ';'.join(x.split()[-1] for x in method_trace.split(','))
            
            receiver = intent_summary.find('receiver')
            keys = list(receiver.attrib.keys())
            if 'extras' in keys:
                keys.remove('extras')
                path_dic['params'] = keys + list(
                    filter(lambda x : x, receiver.attrib.get('extras').split(','))
                )
            else:
                path_dic['params'] = keys
            summary[activity].append(path_dic)
    json_path = os.path.join(os.path.dirname(xml_path), "paramSummary.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, sort_keys=True)
    print("Transformed to [{}]".format(os.path.abspath(json_path)))

if __name__ == '__main__':
    for f_root, f_dirs, f_files in os.walk(sys.argv[1]):
        for f_file in f_files:
            if f_file.startswith('objectSummary_entry') and 'ICCSpecification' in f_root:
                xml_path = os.path.join(f_root, f_file)
                print("Transforming [{}]...".format(os.path.abspath(xml_path)))
                transform_xml(xml_path)
                print("Transform OK!")
    