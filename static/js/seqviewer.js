var typeColors = {		'1'		: 'rgb(50, 50, 0)',
						'2'		: 'rgb(50, 0, 0)',
						'3'		: 'rgb(0, 50, 75)',
						'4'		: 'rgb(0, 50, 0)',
						'5'		: 'rgb(0, 50, 75)'
};

var typeColorsSelected = {	'0'		: 'rgb(230, 230, 120)',
							'1'		: 'rgb(255, 255, 50)',
							'2'		: 'rgb(250, 0, 50)',
							'3'		: 'rgb(0, 200, 250)',
							'4'		: 'rgb(0, 200, 100)',
							'5'		: 'rgb(200, 80, 80)',
						  	'6'		: 'rgb(50, 150, 200)',
						  	'7'		: 'rgb(100, 240, 50)',
						  	'8'		: 'rgb(255, 180, 100)',
						  	'9'		: 'rgb(150, 150, 200)'
};

sequenceCoverage = [];
legend = [];
annotations = [];
var features = []


function parse_annotation(location, label, type, id){
	var res = location.split(";");
	var id = id;
	var loc = res[0];
	var pos = loc.split(":");
	var strand = Number(res[1]);
	
	if (strand == 1){
			strand = '+'
		}else if(strand == -1){
			strand = '-'
		}else{
		}
	
	var start = Number(pos[0]);
	var end = Number(pos[1]);
	var label = label;
	
	annotations.push({label: label, start: start, end: end, strand: strand,id: id, type: type})
}

function sort_annotations(annotations){
	annotations.sort(function(a, b) {
    return a.start - b.start;
});
}

function highlight_seq(annotations){
	var previous = 0;
	var arrayLength = annotations.length;

	for (var i = 0; i < arrayLength; i++) {

		var start = annotations[i].start;
		var end = annotations[i].end;
		var label = annotations[i].label;
		var index = annotations[i].id.split('').pop();
		
		if (start < previous){
			console.log("Skipping label "+label+" due to being inside another feature");
			continue;
		}
		previous = end;

		color = typeColorsSelected[index];

		sequenceCoverage.push({
		start:		start,
		end:		end,
		bgcolor:	color,
		color:		"black",
		underscore:	false   
		});

		legend.push(
			{name: label, color: color, underscore: false}
		);
	}
}

function seqviewer(sequence, element) {
	
		seqViewer = new Sequence(sequence);
		
		seqViewer.render(element, {
			'charsPerLine': 100,
			'search': true,
			'sequenceMaxHeight': "385px",
			'title': "Gene"
		});
}

function draw(canvasName, annotation, sequence, type, name){
	var canvas = document.getElementById(canvasName);
	var arrayLength = annotations.length;
	var track1 = "no";
	var track2 = "no";
	var track3 = "no";

	geneView = new Scribl(canvas, 846);
    geneView.glyph.color = "black";
    geneView.glyph.text.size = 12;
    geneView.glyph.text.font = "courier";
    geneView.glyph.text.align = "center";
	geneView.glyph.roundness = 10;
    geneView.laneSizes = parseInt(20);
	geneView.scale.font.size = 12;
	geneView.scale.min = 25;
	geneView.tick.auto = false;
	geneView.scale.size = 10;
	geneView.scale.font.size = 12;
	geneView.scale.font.color = "black";
	geneView.scale.font.size = 12;
    geneView.trackBuffer = 10;

	if(sequence.length > 1000){
		geneView.tick.major.size = Math.ceil(seq.length / 1000) * 1000;
		geneView.tick.minor.size = Math.ceil(seq.length / 1000) * 100;
	}else if(sequence.length <= 5000 && sequence.length > 1000){
		geneView.tick.major.size = Math.ceil(seq.length / 1000) * 500;
		geneView.tick.minor.size = Math.ceil(seq.length / 1000) * 50;
	}else if(sequence.length <= 1000 && sequence.length > 100){
		geneView.tick.major.size = Math.ceil(seq.length / 100) * 100;
		geneView.tick.minor.size = Math.ceil(seq.length / 100) * 10;
	}else{
		geneView.tick.major.size = Math.ceil(seq.length / 100) * 20;
		geneView.tick.minor.size = Math.ceil(seq.length / 100) * 2;
	}
	
	geneView.scale.max = Math.ceil(seq.length/geneView.tick.major.size) * geneView.tick.major.size;
	
	geneTrack0 = geneView.addTrack().addLane();
	
	for (var i = 0; i < arrayLength; i++) {
		var length = annotations[i].end-annotations[i].start;
		if (length >= 100){
			var track1 = "yes"
		}
		else if (length < 100 && length >= 10){
			var track2 = "yes"
		}else{
			var track3 = "yes"
		}
	}
	
	if (track1 == "yes"){
		geneTrack1 = geneView.addTrack().addLane();
	}
	if (track2 == "yes"){
		geneTrack2 = geneView.addTrack().addLane();
	}
	if (track3 == "yes"){
		geneTrack3 = geneView.addTrack().addLane();
	}
	
	part = geneTrack0.addFeature(new Rect(type,0, sequence.length, '+'));
	part.color="white";
	part.borderColor="black";
   	part.borderWidth = 2;
	part.name = type+" - "+name;

	
	for (var i = 0; i < arrayLength; i++) {
		var start = annotations[i].start;
		var length = annotations[i].end-annotations[i].start;
		var strand = annotations[i].strand;
		var label = annotations[i].label;
		var type = annotations[i].type;
		var id = annotations[i].id;
		var index = annotations[i].id.split('').pop();
				
		if (length >= 100){
			newFeature = geneTrack1.addGene(start, length, strand, {'borderColor':'black'} );
		}else if (length < 100 && length >= 10){
			newFeature = geneTrack2.addGene(start, length, strand, {'borderColor':'black'} );
		}else{
			newFeature = geneTrack3.addGene(start, length, strand, {'borderColor':'black'} );
		}
				
		onClick = function(feature){
			selectedDBID = feature.dbid;
			highlight_sel(feature, typeColorsSelected[feature.index]);
		};

		newFeature.onClick = onClick;
		newFeature.type = type;
		newFeature.index = index;
		newFeature.dbid = id;
		newFeature.name = label;

		newFeature.onMouseover = function(feature){
			for(i=0; i<features.length; i++){
				if (features[i].uid == feature.uid || features[i].dbid == selectedDBID){
					features[i].borderWidth = 5;
				}
				else{
					features[i].borderWidth = 2;
				}
			}
		geneView.redraw();
		feature.addTooltip(feature.type);
		};

	features.push(newFeature);
	}
	canvas.height = geneView.getHeight() + 30;
	geneView.draw();
	draworig();
}

function draworig(){
	for(i=0; i<features.length; i++){
			features[i].setColorGradient( typeColorsSelected[features[i].index], typeColorsSelected[features[i].index]  );
			if (features[i].dbid == selectedDBID){
				features[i].borderWidth = 5;
			}
			else{
				features[i].borderWidth = 2;
			}
	}
	geneView.redraw();
}

function highlight_sel(element, color){

	var sequenceCoverage = [];
	// WARNING removed local variable definition! - RECODE
	subSeq = "";
	strand = element.strand
	type = element.type
	
	var elStart, elEnd;
	var pos, end;

	if (element.strand == '+'){
		elStart = element.position;
		elEnd = element.position+element.length;
	}
	else{
		end = seq.length;
		elStart = element.position;
		elEnd = element.position+element.length;
	}

	sequenceCoverage.push({
	start:		elStart,
	end:		elEnd,
	bgcolor:	color,
	color:		"black",
	underscore:	false   
	});

	subSeq = subSeq + seq.substring(elStart, elEnd);

	seqViewer.coverage(sequenceCoverage);

	var button = document.getElementById('clipboard_btn');
	button.setAttribute('data-clipboard-text', subSeq)
}