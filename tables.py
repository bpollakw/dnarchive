from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from partsdb.system.Tables import Base, BaseMixIn, PartMixIn
from partsdb.tools.Annotators import BlastAnnotator, PfamAnnotator

class Sequence(Base,BaseMixIn,PartMixIn):
	pass

class Gene(Base,BaseMixIn):
	name 			= Column( String(100) )
	alias			= Column( String(100) )
	coordinates 	= Column( Text )
	features		= Column ( String(100) )
	reference 		= Column( String(500) )
	sequenceID  	= Column( Integer, ForeignKey('sequence.id') )
	
	sequence 		= relationship(Sequence, 	enable_typechecks=False)