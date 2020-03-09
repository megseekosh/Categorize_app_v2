# Categorize_app 

GUI to chop, categorize, and annotate audio clips from daylong recordings.
	
  1.	Chopper+VAD chops a longform recording into 30 second clips and runs standard vocal activity detector (Usoltsev, 2015). Creates accompanying metadata file 'config.csv' which contains % vocal acvitity, timestamp of clip in original file, speaker metadata, filename, etc. 
	
  2.	Categorize_app is GUI to walk research assistants through annotatating clips derived from Chopper+VAD. Categorize_app creates new file responses.csv that records annotations made through application + speaker and file metadata. 

# Compute_biling_dominance

Several notebooks to reliably estimate the bilingual dominance of speakers from daylong audio recordings.

Bilingual_ratio - estimates the ratio between language categories for a given speaker using responses.csv from Categorize_app

Rater_Reliability - estimates intra- and inter-rater agreement for language annotation on the basis of clips annotated two and three times. Also concatenates all clips annotated as 'unsure' into 'filename_relisten.csv' to be fed into the Relisten application and listened to again.
