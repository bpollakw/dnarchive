from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from partsdb.system.Tables import Base, BaseMixIn, PartMixIn, AnnotationMixIn
from PartAnnotator import *

	
class Entry(Base,BaseMixIn,PartMixIn):
	name 			= Column ( String(100) )
	description		= Column ( String(100) )
	type			= Column ( String(100) )
	reference 		= Column ( String(500) )
	score			= Column ( Integer )
	votes			= Column ( Integer )
	
class Annotations(Base,BaseMixIn,AnnotationMixIn):
	__targetclass__ 	= 	Entry
	__annotatorclass__ 	= 	PartAnnotator
	
	type			= Column ( String(100) )
	label			= Column ( String(100) )
	location		= Column ( String(100) )