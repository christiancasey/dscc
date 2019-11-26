cd pdf_in;
for f in *.pdf; 
	do convert -thumbnail x300 -background white -alpha remove "$f"[0] "../pdf_out/${f%.pdf}_thumb.png"; 
	done