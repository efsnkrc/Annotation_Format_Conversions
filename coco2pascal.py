import baker
import json
from pathlib import Path as path
from cytoolz import merge, join, groupby
from cytoolz.compatibility import iteritems
from itertools import starmap
from lxml import etree, objectify
from scipy.ndimage import imread


def keyjoin(leftkey, leftseq, rightkey, rightseq):
    return starmap(merge, join(leftkey, leftseq, rightkey, rightseq))


def root(folder, filename, height, width):
    E = objectify.ElementMaker(annotate=False)
    return E.annotation(
            E.folder(folder),
            E.filename(filename),
            E.source(
                E.database('MS COCO 2012'),
                E.annotation('MS COCO 2012'),
                E.image('Flickr'),
                ),
            E.size(
                E.width(width),
                E.height(height),
                E.depth(3),
                ),
            E.segmented(0)
            )

def instance_to_xml(anno):
    E = objectify.ElementMaker(annotate=False)
    xmin, ymin, width, height = anno['bbox']
    return E.object(
            E.name(anno['category_id']),
            E.bndbox(
                E.xmin(int(round(xmin))),
                E.ymin(int(round(ymin))),
                E.xmax(int(round(xmin+width))),
                E.ymax(int(round(ymin+height))),
                ),
            )

def get_instances(coco_annotation):
    coco_annotation = path(coco_annotation).expand()
    content = json.loads(coco_annotation.text())
    categories = {d['id']: d['name'] for d in content['categories']}
    return categories, tuple(keyjoin('id', content['images'], 'image_id', content['annotations']))

def rename(name, year=2017):
        out_name = path(name).stripext()
        # out_name = out_name.split('_')[-1]
        # out_name = '{}_{}'.format(year, out_name)
        return out_name

@baker.command
def create_imageset(coco_annotation, dst):
    _ , instances= get_instances(coco_annotation)
    dst = path(dst).expand()
 
    for instance in instances:
        name = rename(instance['file_name'])
        dst.write_text('{}\n'.format(name), append=True)

@baker.command
def create_annotations(dbpath, subset, dst):
    annotations_path = path(dbpath).expand() / 'annotations_json/instances_{}2012.json'.format(subset)
    images_path = path(dbpath).expand() / 'images'
    categories , instances= get_instances(annotations_path)
    dst = path(dst).expand()

    for i, instance in enumerate(instances):
        instances[i]['category_id'] = categories[instance['category_id']]

    for name, group in iteritems(groupby('file_name', instances)):
	if Path(images_path + "/" + name).exists():
        	img = imread(images_path / name)
        	if img.ndim == 3:
	            out_name = rename(name)
        	    annotation = root('VOC2012', '{}.jpg'.format(out_name), 
        	                      group[0]['height'], group[0]['width'])
        	    for instance in group:
			if(instance['category_id'] == 'person'):
	        	        annotation.append(instance_to_xml(instance))
        	    etree.ElementTree(annotation).write(dst / '{}.xml'.format(out_name))


if __name__ == '__main__':
    baker.run()
