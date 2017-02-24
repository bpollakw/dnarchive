from waitress import serve
import os
import re
import itertools
import collections
from flask import Flask, session, redirect, url_for, escape, request, render_template, make_response, flash, abort
import urlparse
import psycopg2

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation, CompoundLocation
from Bio.Alphabet import IUPAC

from partsdb.partsdb import PartsDB
from tables import *

app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = '73234adae4dd527740b123211473c356b1df1d577e007b90'
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///userdb"
app.debug = True

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

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
		if term !="":
			return redirect(url_for('results'), code=307)
		else:
			flash('ERROR - Your query is empty!')
	return render_template('home.html')

@app.route('/results', methods=['POST'])
def results():		
	
	if request.method == 'POST':
		term = request.form["term"]
		
		if not (term):
			flash('Empty search term')
			return redirect(url_for('index'))
		
		else:	
			partsdb = PartsDB('postgres://fqogwqhxyxqtah:a209a6b1bee6d45e0d9f1251ddd09e3b3c1b22e2ae702a1d1084318e1fb082b9@ec2-23-21-204-166.compute-1.amazonaws.com:5432/d55q7q6phaaj9i', clean = False, Base = Base)

			session = partsdb.Session()
			query = session.query(Gene).first()
			
			return render_template('results.html', query = query, name = query.name, sequenceID = query.sequenceID, sequence = query.sequence.seq )
			
			session.close()
			
		

@app.route('/submit', methods=['GET','POST'])
def submit():
	
	if request.method == 'POST':
		name = request.form["name"]
		sequence = request.form["sequence"]

		if name !="" and sequence !="":
			return redirect(url_for('submitted'), code=307)
		else:
			flash('ERROR - Your submission is empty!')
			
	return render_template('submit.html')

@app.route('/submitted', methods=['POST'])
def submitted():		
	
	if request.method == 'POST':
		name = request.form["name"]
		alias = request.form["alias"]
		sequence = request.form["sequence"]
		features = request.form["features"]
		reference = request.form["reference"]
	
	partsdb = PartsDB('postgres://fqogwqhxyxqtah:a209a6b1bee6d45e0d9f1251ddd09e3b3c1b22e2ae702a1d1084318e1fb082b9@ec2-23-21-204-166.compute-1.amazonaws.com:5432/d55q7q6phaaj9i', clean = False, Base = Base)

	sequence = partsdb.addPart('sequence', seq = sequence)
	
	gene = partsdb.addPart('gene', name = name, alias = alias, features = features, reference = reference, sequence = sequence)
	
	partsdb.commit()
	
	return render_template('submitted.html')

# NOTHING DONE HERE YET...
@app.route('/export')
def export():
	name = request.args.get('name','')
	seq = request.args.get('seq','')
	seq_type = request.args.get('type','')
	
	if not name:
		return ('', 204)

	record = SeqRecord( Seq( seq, IUPAC.unambiguous_dna ), name = name, description = name+"recoded to type IIs part", id=name)
	
	strand = 1;
	location = FeatureLocation(11, len(seq)-11, strand = strand);
	record.features.append( SeqFeature( location = location, strand = strand, type=seq_type, id=name, qualifiers={"key": name} ))
	
	location = FeatureLocation(0, 6, strand = strand);
	record.features.append( SeqFeature( location = location, strand = strand, type="BsaI_F", id="BsaI"))
	
	location = FeatureLocation(7, 11, strand = strand);
	record.features.append( SeqFeature( location = location, strand = strand, type="misc_feature", id="Overhang" ))

	strand = -1;
	location = FeatureLocation(len(seq)-6, len(seq), strand = strand);
	record.features.append( SeqFeature( location = location, strand = strand, type="BsaI_R", id="BsaI" ))
	

	location = FeatureLocation(len(seq)-11, len(seq)-7, strand = strand);
	record.features.append( SeqFeature( location = location, strand = strand, type="misc_feature", id="Overhang" ))


	response = make_response(record.format("gb"))
	response.headers["Content-Type"] = "application/octet-stream"
	response.headers["Content-Disposition"] = "attachement; filename={0}".format(name+'.gb')
	return response


if __name__ == "__main__":
 	port = int(os.environ.get('PORT', 5000))	
	serve(app, host="0.0.0.0", port=port)
	
	#serve(wsgiapp, listen='*:8080')  
	#app.run(debug=True, host="0.0.0.0", port=5000)