from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
from Bio.SeqFeature import SeqFeature, CompoundLocation, FeatureLocation
import sys

class Annotator:
	def __init__(self, cls):
		self.cls = cls

class PartAnnotator(Annotator):
	def annotate(self, db, **kwargs):
		if kwargs['trace'] == 'upload':
			self._annotate(db, kwargs['fileName'], kwargs['target'] )
			
		elif kwargs['trace'] == 'submit':
			self._annotate_submit(db, kwargs['label'], kwargs['length'], kwargs['type'], kwargs['target'] )

	def _annotate(self, db, fileName, target):
		
		for record in SeqIO.parse(fileName, "genbank"):

			features = record.features

		for feature in features:
			
			start 	= int(feature.location.start)
			end 	= int(feature.location.end)
			strand 	= feature.location.strand
			tabs = feature.qualifiers['label'][0].split('(')
			if len(tabs) == 1:
				joined = tabs[0]
			else:
				joined = '('.join(tabs[:-1])			
			
			hit 			=	 self.cls()
			hit.location 	= 	"%s:%s;%s" % (start,end,strand)
			# Issues with next one with wrongly formatted Genbank files (such as recode2S export)
			hit.label 		= 	joined
			hit.type 		= 	feature.type
			hit.target 		=	target
			
			db.session.add(hit)
		db.commit()
		db.session.close()
		
	def _annotate_submit(self, db, label, length, type, target):
		
		hit 			= 	self.cls()
		
		hit.location	= 	"%s:%s;%s" % (0,length,0)
		hit.label 		= 	label
		hit.type 		= 	type
		hit.target 		=	target
		
		db.session.add(hit)
		db.commit()
		db.session.close()