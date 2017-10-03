import argparse
import json
from lxml import etree
import glob
import shutil
import logging
import re
import csv
def createargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--osm', required = True, type=str)
    args = parser.parse_args()
    return args

def getid2points(xml):
    nodes = {}
    ways = {}
    for idx, element in xml:
        if element.tag == "node":
            nodes[element.attrib["id"]] = [str(element.attrib["lat"]), str(element.attrib["lon"])]
        elif element.tag == "way":
            name = [ v.attrib['v'] for i, v in enumerate(element) if v.tag == "tag" and v.attrib['k'] == 'name'][0]
            ways[element.attrib["id"]] = {}
            ways[element.attrib["id"]]["points"] = [ nodes[ v.attrib['ref'] ] for i, v in enumerate(element) if v.tag == "nd" ]
            ways[element.attrib["id"]]["name"] = name
    return ways

def createwkt(id2points, name):
    with open(name + '.csv', 'w') as csvfile:
        fieldnames = ['osm_id', 'name', 'WKT']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for v in id2points:
            linestring = "LINESTRING("
            for idx, val in enumerate(id2points[v]["points"]):
                linestring+= (val[1]) + ' ' + (val[0]) + ', '
            linestring = linestring[0:len(linestring)-2]

            linestring+=' )'
            writer.writerow({'osm_id': v, 'name': id2points[v]["name"], 'WKT' : linestring})

def main():
    args = createargs()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    logging.info('Reading {}.'.format(args.osm))

    xml = etree.iterparse((args.osm))

    id2points = getid2points(xml)
    logging.info('{} ways found.'.format(len(id2points)))

    createwkt(id2points, args.osm.split('/')[-1].split('.')[0])


if _name_ == "_main_":
    main()
