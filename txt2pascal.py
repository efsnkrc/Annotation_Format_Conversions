import sys
import os
import csv
import cv2
import math
from lxml import etree, objectify
from pathlib import Path

input_txt = sys.argv[1]
input_images_folder = sys.argv[2]
output_xml_folder = sys.argv[3]

def root(folder, filename, height, width):
	E = objectify.ElementMaker(annotate=False)
	return E.annotation(
		E.folder(folder), 
		E.filename(filename),
		E.source(
		E.database('TMP'),
		E.annotation('TMP'),
		E.image('Flickr'),
		),
	E.size(
		E.width(width),
		E.height(height),
		E.depth(3),
		),
	E.segmented(0)
	)

def instance_to_xml(xmin, ymin, xmax, ymax, activity):
	E = objectify.ElementMaker(annotate=False)
	return E.object(
		E.name(label),
		E.bndbox(
		E.xmin(xmin),
		E.ymin(ymin),
		E.xmax(xmax),
		E.ymax(ymax),
		),
	)

with open(input_txt) as file:
	annotation = None
	for line in file:
		row = line.strip().split(',')
		fullImageName = row[0]
		if os.path.exists("%s/%s" % (input_images_folder, fullImageName)):
			img = cv2.imread("%s/%s" % (input_images_folder, fullImageName))
			width, height, depth = img.shape
			for i in range(2, len(row), 5):
				label = row[i + 4]
				if annotation is None:
					annotation = root('TMP', fullImageName, height, width)
				elif annotation.filename != fullImageName:
					etree.ElementTree(annotation).write("%s/%s.xml" % (output_xml_folder, str(annotation.filename).split('.')[0]))
					annotation = root('TMP', fullImageName, height, width)
				xmin = int(math.ceil(float(row[i])))
				ymin = int(math.ceil(float(row[i+1])))
				xmax = int(math.ceil(float(row[i+2])))
				ymax = int(math.ceil(float(row[i+3])))
				annotation.append(instance_to_xml(xmin, ymin, xmax, ymax, label))
	etree.ElementTree(annotation).write("%s\%s.xml" % (output_xml_folder, fullImageName.split('.')[0]))
