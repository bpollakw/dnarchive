from partsdb.partsdb import PartsDB
from tables import *

partsdb = PartsDB('postgresql:///dnarchive', clean = False, Base = Base)


sequence    = partsdb.addPart('sequence', seq = "TTACGTGATGATGATGTAGTAGTAGTAGTAGATGATGATGATGATGATA")
gene = partsdb.addPart('gene', name = "algo", alias = "otro", coordinates = "1,2,3,4,5", features = "Cas9", reference = "Me", sequence = sequence)

partsdb.commit()
