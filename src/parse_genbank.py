from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
from pprint import pprint
from Bio.SeqFeature import SeqFeature, CompoundLocation, FeatureLocation
import os
import sys

## I should do something about Ape colors in qualifiers...
	
for record in SeqIO.parse(sys.argv[1], "genbank"):
	
	name = record.name
	description = record.description
	seq = record.seq
	features = record.features
	
	ftype = []
	location_start = []
	location_end = []
	labels = []
	labels = []
	strands = []
	
for feature in features:
	ftype.append(feature.type)
	location_start.append(int(feature.location.start))
	location_end.append(int(feature.location.end))
	strands.append(feature.location.strand)
	print feature.location
	tabs = feature.qualifiers['label'][0].split('(')
	if len(tabs) == 1:
		joined = tabs[0]
	else:
		joined = '('.join(tabs[:-1])
		
	labels.append(joined)
	
print location_start
print location_end
print strands
print ftype
print labels


	