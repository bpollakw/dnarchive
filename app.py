from partsdb.partsdb import PartsDB
from tables import *
from sets import Set
from waitress import serve
import os
import re
import itertools
import collections
from flask import Flask, session, redirect, url_for, escape, request, render_template, make_response, flash, jsonify, abort, Markup
import urlparse
from sqlalchemy import or_
import hashlib
	
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation, CompoundLocation
from Bio.Alphabet import IUPAC

from werkzeug import secure_filename

app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = '73234adae4dd527740b123211473c356b1df1d577e007b90'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['ape','gb','gbk'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///userdb"
app.debug = True

urlparse.uses_netloc.append("postgres")

partsdb = PartsDB('postgres://fqogwqhxyxqtah:a209a6b1bee6d45e0d9f1251ddd09e3b3c1b22e2ae702a1d1084318e1fb082b9@ec2-23-21-204-166.compute-1.amazonaws.com:5432/d55q7q6phaaj9i', clean = False, Base = Base) 
# PartsDB('postgresql:///dnarchive', clean = False, Base = Base)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize(seq):
	my_seq = Seq(seq)
	count = my_seq.count("G")
	count = count + my_seq.count("A")
	count = count + my_seq.count("T")
	count = count + my_seq.count("C")
	if len(seq) == count:
		return True
	else:
		return False

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404'), 404

@app.errorhandler(500)
def internal_error(e):
	return render_template('500.html', title='500'), 500

@app.route('/', methods=['GET','POST'])
def index():
	
	if request.method == 'POST':
		term = request.form["term"]
		type = request.form["type"]
	
		return redirect(url_for('results', term=term,type=type))
		
	return render_template('home.html')

@app.route('/results')
def results():		

	term = request.args['term']
	type = request.args['type']
	dbsession = partsdb.Session()
	if len(type) == 0:
		if not (term):
			query = dbsession.query(Entry).all()

		else:	
			query = dbsession.query(Entry).filter(Entry.id == Annotations.targetID).filter(Annotations.label.ilike('%'+term+'%')).all()
			qset = Set(query)
			query = dbsession.query(Entry).filter(or_(Entry.name.ilike('%'+term+'%'), Entry.description.ilike('%'+term+'%'))).all() 
			qset.update(query)
			query = list(qset)
	else:
		if not (term):
			query = dbsession.query(Entry).filter(Entry.type.ilike('%'+type+'%')).all()
		else:	
			query = dbsession.query(Entry).filter(Entry.id == Annotations.targetID).filter(Annotations.label.ilike('%'+term+'%')).filter(Entry.type.ilike('%'+type+'%')).all()
			qset = Set(query)
			query = dbsession.query(Entry).filter(or_(Entry.name.ilike('%'+term+'%'), Entry.description.ilike('%'+term+'%'))).filter(Entry.type.ilike('%'+type+'%')).all() 
			qset.update(query)
			query = list(qset)
	dbsession.close()

	if not query:
		flash('No results for that query')
		return redirect(url_for('index'))
	else:
		return render_template('results.html', table = query, title="- Results")

@app.route('/details',methods=['GET'])
def details():

	dbid = request.args.get('dbid')
	id = dbid.split('.')[2]
	dbsession = partsdb.Session()
	query = dbsession.query(Entry).get(int(id))
	annotations = dbsession.query(Annotations).filter(Annotations.targetID == int(id)).all()
	dbsession.close()
	
	score = (query.score+0.1)/(query.votes+0.1)

	
	voted = False
	if not "vote" in session:
		session["vote"] = ""
	if session["vote"].find(str(query.dbid)) > -1:
		voted = True

	return render_template('details.html', data = query, annotations = annotations, title="- Details", voted=voted, score = score)

	

@app.route('/upload', methods=['GET','POST'])
def upload():
	name = ""
	type = ""
	description = ""
	reference = ""
	if request.method == 'POST':
		f = request.files['file']
		
		name = request.form['name']
		description = request.form['description']
		type = request.form['type']
		reference = request.form['reference']
		
		if description == "Enhanced green fluorescent protein":
			description = ""
		if name == "eGFP":
			name = ""
		
		if name =="":
			flash('Your submission has no name!')
		else:
			if not type:
				flash('Your submission has no sequence type!')
			else:
				if not f:
					flash('ERROR - You forgot to attach the file!')

				else:
					if allowed_file(f.filename):
						flash('Excelent - Submission successful!')
						session['description'] = description
						session['reference'] = request.form['reference']
						session['type'] = type
						session['name'] = name
						f.save(os.path.join(app.config['UPLOAD_FOLDER'], "temp.gb"))
						return redirect(url_for('submitted', trace="upload"), code=302)

					else:
						flash('ERROR - Your file has the wrong extension or is not the appropriate file type. Genbank files only!')

				
				
	return render_template('upload.html', name = name, type=type, description = description, reference = reference, title="- Upload")

@app.route('/submit', methods=['GET','POST'])
def submit():
	
	name = ""
	type = ""
	description = ""
	sequence = ""
	reference = ""
	
	if request.method == 'POST':
		name = request.form["name"]
		type = request.form["type"]
		description = request.form["description"]
		sequence = request.form["sequence"].upper()
		reference = request.form["reference"]
		
		if name == "eGFP":
			name = ""
		
		if not sanitize(sequence):
			flash('ERROR - Your sequence contains non-nucleotides!')
			return render_template('submit.html', title="- Submit", name = name, type = type, description = description, sequence = sequence, reference = reference)
			
			
		if sequence == "ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTGCCCATCCTGGTCGAGCTGGACGGCGACGTAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGATGCCACCTACGGCAAGCTGACCCTGAAGTTCATCTGCACCACCGGCAAGCTGCCCGTGCCCTGGCCCACCCTCGTGACCACCCTGACCTACGGCGTGCAGTGCTTCAGCCGCTACCCCGACCACATGAAGCAGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTCCAGGAGCGCACCATCTTCTTCAAGGACGACGGCAACTACAAGACCCGCGCCGAGGTGAAGTTCGAGGGCGACACCCTGGTGAACCGCATCGAGCTGAAGGGCATCGACTTCAAGGAGGACGGCAACATCCTGGGGCACAAGCTGGAGTACAACTACAACAGCCACAACGTCTATATCATGGCCGACAAGCAGAAGAACGGCATCAAGGTGAACTTCAAGATCCGCCACAACATCGAGGACGGCAGCGTGCAGCTCGCCGACCACTACCAGCAGAACACCCCCATCGGCGACGGCCCCGTGCTGCTGCCCGACAACCACTACCTGAGCACCCAGTCCGCCCTGAGCAAAGACCCCAACGAGAAGCGCGATCACATGGTCCTGCTGGAGTTCGTGACCGCCGCCGGGATCACTCTCGGCATGGACGAGCTGTACAAGTCCGGAGCTGCGGCCGCTGCCGCTGCGGCAGCGGCCTAA":
			sequence = ""	
					
		if description == "Enhanced green fluorescent protein":
			description = ""
		
		if name !="" and sequence !="" and type !="":
			flash('Excelent - Submission successful!')
			return redirect(url_for('submitted', trace="submit"), code=307)
		
		else:
			flash('ERROR - Your submission might be missing name, type or sequence!')
			
	return render_template('submit.html', title="- Submit", name = name, type = type, description = description, sequence = sequence, reference = reference)

@app.route('/submitted', methods=['GET','POST'])
def submitted():		
	trace = request.args.get('trace')
	print trace
	
	if trace == 'submit':

		if request.method == 'POST':
			name 			=	request.form["name"]
			description 			= 	request.form["description"]
			sequence 		= 	request.form["sequence"].upper()
			type	 		=	request.form["type"]
			reference 		=	request.form["reference"]
			score 			=	0
			
			entry = partsdb.addPart('entry', name = name, description = description, type = type, reference = reference, seq = sequence, score = score, votes = 0)

			partsdb.commit()

			partsdb.annotate('annotations', trace = trace, label = name, length = len(sequence), type = type, target = entry)
		
	elif trace == 'upload':
		    
		name 			= 	session.get('name')
		description 	= 	session.get('description')
		type	 		= 	session.get('type')
		reference 		=	session.get('reference')
		score			=	0
		
		for record in SeqIO.parse('uploads/temp.gb', "genbank"):
			sequence = str(record.seq).upper()


			entry = partsdb.addPart('entry', name = name, description = description, type = type, reference = reference, seq = sequence, score = score, votes = 0)
			partsdb.commit()
			
			partsdb.annotate('annotations', fileName='uploads/temp.gb', trace=trace, target = entry)
			
	return redirect(url_for('index'))

# NOTHING DONE HERE YET...
@app.route('/export')
def export():
	dbid = request.args.get('dbid')
	
	if not dbid:
		flash("ERROR - no database id provided")
		return ('', 204)
	
	id = dbid.split('.')[2]
	
	dbsession = partsdb.Session()
	query = dbsession.query(Entry).get(int(id))
	annotations = dbsession.query(Annotations).filter(Annotations.targetID == int(id)).all()
	dbsession.close()
	
	if not query:
		return ('', 204)

	seq = query.seq
	name = query.name
	description = query.description
	type = query.type
	
	colours = ['69D2E7','A7DBD8','ffff99','FA6900','C02942','53777A','F8CA00','8A9B0F','C6A49A','C6E5D9']
	
	record = SeqRecord( Seq( seq, IUPAC.unambiguous_dna ), name = name, description = description, id=dbid, dbxrefs=[str(dbid),"DNArchive"])
	
	i=0
	for annotation in annotations:
		strand = int(annotation.location.split(';')[1])
		pos = annotation.location.split(';')[0]
		start = int(pos.split(':')[0])
		end = int(pos.split(':')[1])
		label = annotation.label
		type = annotation.type
		id = annotation.id
		
		if (i>9):
			i=i-10
		
		location = FeatureLocation(start, end, strand = strand);
		
		record.features.append( SeqFeature( location = location, strand = strand, type=type, id=name, qualifiers={"label": label,"ApEinfo_fwdcolor": "#"+colours[i]} ))
		
		i=i+1

	response = make_response(record.format("gb"))
	response.headers["Content-Type"] = "application/octet-stream"
	response.headers["Content-Disposition"] = "attachement; filename={0}".format(name+'.gb')
	return response

@app.route('/vote')
def vote():
	dbid = request.args.get('dbid')
	id = dbid.split('.')[2]
	
	vote = int(request.args.get('vote'))

	dbsession = partsdb.Session()
	query = dbsession.query(Entry).filter(Entry.dbid == dbid).update({"score": (Entry.score + vote)})
	query = dbsession.query(Entry).filter(Entry.dbid == dbid).update({"votes": (Entry.votes + 1)})
	dbsession.commit()
	dbsession.close()
	
	if not "vote" in session:
		session["vote"] = ""
	if dbid in session["vote"]:
		session["vote"] = session["vote"].replace(":{0}:".format(dbid), "")
	else:
		session["vote"] += ":{0}:".format(dbid)
	
	return "OK",  200, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
 	port = int(os.environ.get('PORT', 5000))	
	serve(app, host="0.0.0.0", port=port)
	
	#serve(wsgiapp, listen='*:8080')  
	#app.run(debug=True, host="0.0.0.0", port=5000)