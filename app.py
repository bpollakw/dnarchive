from waitress import serve
import os
import re
import itertools
import collections
from flask import Flask, session, redirect, url_for, escape, request, render_template, make_response, flash, abort

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation, CompoundLocation
from Bio.Alphabet import IUPAC

app = Flask(__name__, static_url_path="", static_folder="static")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404'), 404

@app.errorhandler(500)
def internal_error(e):
	return render_template('500.html', title='500'), 500

@app.route('/')
def index():
				
	return render_template('home.html')

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