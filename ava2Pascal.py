import csv
import cv2
import math
from lxml import etree, objectify


def root(folder, filename, height, width):
    E = objectify.ElementMaker(annotate=False)
    return E.annotation(
            E.folder(folder),
            E.filename(filename),
            E.source(
                E.database('AVA v2.1'),
                E.annotation('AVA2PASCAL'),
                E.image('Flickr'),
                ),
            E.size(
                E.width(width),
                E.height(height),
                E.depth(3),
                ),
            E.segmented(0)
            )

def instance_to_xml(xmin, ymin, xmax, ymax):
    E = objectify.ElementMaker(annotate=False)
    return E.object(
            E.name('person'),
            E.bndbox(
                E.xmin(xmin),
                E.ymin(ymin),
                E.xmax(xmax),
                E.ymax(ymax),
                ),
            )

with open('ava_val_v2.1.csv') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	counter = 0
	xminOld = 0
	xmaxOld = 0
	yminOld = 0
	ymaxOld = 0
	for row in spamreader:
		if(counter <> 0):
			oldName = imageName
			oldNo = frameNo
			xminOld = xmin
			xmaxOld = xmax
			yminOld = ymin
			ymaxOld = ymax
		imageName = row[0]
		frameNo = int(row[1])
		fullImageName = "AVA_" + str(imageName) + "_" + str(frameNo) + ".jpg"	
		if(counter <> 0):
			if(annotation.filename == fullImageName):
				xmin = int(math.ceil(float(row[2]) * height))
				ymin = int(math.ceil(float(row[3]) * width))
				xmax = int(math.ceil(float(row[4]) * height))
				ymax = int(math.ceil(float(row[5]) * width))
				if(xminOld <> xmin and xmaxOld <> xmax and yminOld <> ymin and ymaxOld <> ymax):
					annotation.append(instance_to_xml(xmin, ymin, xmax, ymax))
				continue
			else:
				etree.ElementTree(annotation).write('./annotations/{}.xml'.format("AVA_" + str(oldName) + "_" + str(oldNo)))
		try:			
			img = cv2.imread("./images/" + fullImageName)
			width, height, depth = img.shape
			xmin = int(math.ceil(float(row[2]) * height))
			ymin = int(math.ceil(float(row[3]) * width))
			xmax = int(math.ceil(float(row[4]) * height))
			ymax = int(math.ceil(float(row[5]) * width))
		except AttributeError:
			continue
		annotation = root('AVA', fullImageName, height, width)
		if(xminOld <> xmin and xmaxOld <> xmax and yminOld <> ymin and ymaxOld <> ymax):
			annotation.append(instance_to_xml(xmin, ymin, xmax, ymax))
		counter = 1
			

