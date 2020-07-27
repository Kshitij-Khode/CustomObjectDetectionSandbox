#!/usr/bin/python
import os, subprocess, argparse, sys, re
import glob, math

import pandas as pd
import xml.etree.ElementTree as ET

rc = {
    -1: '[FAIL] Illegal args'
}

parser = argparse.ArgumentParser(description='$CHANGE_HELP_MSG')

def add_string_arg(id, help, required):
    parser.add_argument('--%s' % id, help=help, type=str, default='', required=required)

def parse_args():
    return parser.parse_args().__dict__

def write_file(content, filepath):
    with open(filepath, 'w') as sfile:
        sfile.write(content)
        sfile.close()

def exit(returncode):
    print(rc[returncode])
    sys.exit(returncode)

def xml_to_csv(fileList):
    xml_list = []
    for xml_file in fileList:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df

add_string_arg('function', 'HelpMessage', True)
add_string_arg('targetFolder', 'HelpMessage', False)
add_string_arg('xmlFolder', 'HelpMessage', False)
add_string_arg('trainValLoc', 'HelpMessage', False)
add_string_arg('csvLoc', 'HelpMessage', False)

argDict = parse_args()
function = argDict['function']

if function == 'rename':
    if 'targetFolder' not in argDict: exit(-1)
    path = argDict['targetFolder']

    counter = 1
    for f in os.listdir(path):
        suffix = f.split('.')[-1]
        if suffix == 'jpg' or suffix == 'png':
            new = '{}{}.{}'.format(str(path.replace('/', '')), str(counter), suffix)
            os.rename(path + f, path + new)
            counter = int(counter) + 1

elif function == 'genTrainVal':
    if 'xmlFolder' not in argDict or 'trainValLoc' not in argDict: exit(-1)
    xmlFolder = argDict['xmlFolder']
    trainValLoc = argDict['trainValLoc']

    trainValContent = ''
    for f in os.listdir(xmlFolder):
        trainValContent += f.split('.')[0] + '\n'
    write_file(trainValContent, '%strainval.txt' % trainValLoc)

elif function == 'xmlToCsv':
    if 'xmlFolder' not in argDict and 'csvLoc' not in argDict: exit(-1)
    xmlFolder = argDict['xmlFolder']
    csvLoc = argDict['csvLoc']
    xmlFileList = glob.glob(os.path.join(os.getcwd(), xmlFolder) + '/*.xml')
    trainList = xmlFileList[:math.floor(0.7*len(xmlFileList))]
    valList = xmlFileList[math.floor(0.7*len(xmlFileList)):]
    xml_df = xml_to_csv(trainList)
    xml_df.to_csv('%strainList.csv'%csvLoc, index=None)
    xml_df = xml_to_csv(valList)
    xml_df.to_csv('%svalList.csv'%csvLoc, index=None)
