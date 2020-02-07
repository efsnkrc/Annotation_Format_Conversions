import sys
import os
import csv
import cv2
import math
from lxml import etree, objectify
from pathlib import Path

path = sys.argv[1]
txt = ''

for file in os.listdir(path):
	tree = etree.parse(path + file)
	root = tree.getroot()
	for child in root:
		if child.tag == 'filename':
			rootname = child.text
			objects = ''
			cnt = 0
		if child.tag == 'object':
			cnt += 1
			objectroot = child
			for child in objectroot:
				if child.tag == 'name':
					tagname = child.text
				if child.tag == 'bndbox':
					xmin = child[0].text
					ymin = child[1].text
					xmax = child[2].text
					ymax = child[3].text
					objects += ',%s,%s,%s,%s,%s' % (xmin, ymin, xmax, ymax, tagname)
	if objects != '':
		txt += '%s,%d%s\n' % (rootname, cnt, objects) 
text_file = open((rootname.split('.')[0] + ".txt"), "w")
text_file.write(txt)
text_file.close()
