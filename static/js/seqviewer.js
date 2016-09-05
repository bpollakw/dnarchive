function recoder(sequence, element, name) {
		seqViewer = new Sequence(sequence);
		
		seqViewer.render(element, {
			'charsPerLine': 100,
			'sequenceMaxHeight': "300px",
			'title': name
		});
}

function sites(sites, length, color){
	if (typeof sequenceCoverage !== 'undefined') {
	}
	else{
		sequenceCoverage = [];
	}
	if (sites.length > 0){
		for (var i = 0; i < sites.length; i++){

			sequenceCoverage.push({
			start:		sites[i],
			end:		sites[i]+length,
			bgcolor:	color,
			color:		"white",
			underscore:	false   
			});
		}
	}
	else{
			sequenceCoverage.push({
			start:		0,
			end:		0,
			bgcolor:	"white",
			color:		"black",
			underscore:	false   
			});
	}
}

function legende(name, color){
		if (typeof legend !== 'undefined') {
	}
	else{
		 legend = [];
	}	
	
		 legend.push({
			 name: name, color: color, underscore: false
		 });
}

function add_legend(){
	seqViewer.addLegend(legend);		
					 }

function highlight_sites(){
	seqViewer.coverage(sequenceCoverage);
}

function recode(name, seq, newseq, type){	

	if (type == "CDS" && seq.substring(0,3) == "ATG"){
		if (typeof changed !== 'undefined'){

		}
		else if(typeof changed == 'undefined'){
			front = "GGTCTCAA";
			back = "GCTTCGAGACC";
			add=8;
		}
	}
	else if (type == "CDS" && seq.substring(0,3) != "ATG"){
		alert("cds does not start with ATG. Check sequence!")
	}
	else if (type == 'promoter' && typeof changed == 'undefined'){
			front = "GGTCTCAGGAG"
			back = "CCATCGAGACC"
			add=11;
	}
	else if (type == 'promoter' && typeof changed != 'undefined'){}
	else if (type == 'terminator' && typeof changed == 'undefined'){
			front = "GGTCTCAGCTT"
			back = "CGCTTGAGACC"
			add=11;
	}
	else if (type == 'terminator' && typeof changed != 'undefined'){}
	else{
		console.log(type)
		alert("Recode is for promoters, cdss and terminators")
	}
	newseq = front+newseq+back
	recodedseq = newseq
	recoder(newseq, '#seqView', name+" - Recoded");
	delete sequenceCoverage;
	delete legend;
	var highlight = [0,newseq.length-6]
	var overhangs = [7,newseq.length-11]
	sites(highlight,6,"blue");
	sites(overhangs,4,"red");
	// WTF?
	for (var i = 0; i < BsaI.length; i++){
		sites([BsaI[i]+add],6,"green");
	}
	for (var i = 0; i < SapI.length; i++){
		sites([SapI[i]+add],7,"green");
	}

	legende("BsaI","blue");
	legende("Old sites","green");
	legende("Overhangs","red");
	add_legend();
	highlight_sites();
	document.getElementById("message").innerHTML = "BsaI & SapI sites recoded, BsaI flanking sequences and overhangs added.";

	var button = document.getElementById('clipboard_btn');
	button.setAttribute('data-clipboard-text', recodedseq)

					}
  function change_overhangs(i) {
    if (i == "N"){
		changed ="yes";
		front = "GGTCTCACC";
		back = "AATGTGAGACC";
		add=9;
	}
	else if (i == "C"){
		changed ="yes";
		front = "GGTCTCATTCG";
		back = "GCTTTGAGACC";
		add=11;
   	}
  	else if (i == "P"){
		changed ="yes";
		front = "GGTCTCAGGAG";
		back = "TACTTGAGACC";
		add=11;
   	}
  	else if (i == "T"){
		changed ="yes";
		front = "GGTCTCAGGTA";
		back = "CGCTTGAGACC";
		add=11;
   	}
   	else{ 
		delete changed;
   	}	  
  }
function export_GB(name, seqtype){
	link = "/export?"+"seq="+recodedseq+"&type="+seqtype+"&name="+name
	location.href=link;
}