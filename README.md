# Categorize_app 

GUI to chop, categorize, and annotate audio clips from daylong recordings.
	
  1_chunk-and-label - a chopper + vocal activity dectector
          - chops longform recordings into 30 second clips
	  - runs standard vocal activity detector (Usoltsev, 2015)
	  - Creates accompanying metadata file 'config.csv' which contains % vocal acvitity, timestamp of clip in original file, speaker metadata, filename, etc. 
	
 2_categorize_app - GUI to walk research assistants through annotatating clips derived from 1_chunk-and-label. Categorize_app creates new file `responses.csv` that records annotations made through application + speaker and file metadata. 

# Compute_biling_dominance

Several notebooks to reliably estimate the bilingual dominance of speakers from daylong audio recordings.

3_bilingual_ratio.ipynb - estimates the ratio between language categories for a given speaker using responses.csv from 2_categorize_app

4_rater_Reliability - estimates intra- and inter-rater agreement for language annotation on the basis of clips annotated two and three times. Also concatenates all clips annotated as 'unsure' into 'filename_relisten.csv' to be fed into the Relisten application and listened to again.

5_relisten_app - to appear; draws all files that appear in the filename_relisten.csv dataframe to listen to again (without replacement)
