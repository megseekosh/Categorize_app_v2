# Categorize_app 

GUI to chop, categorize, and annotate audio clips from daylong recordings. This version annotates ambient language characteristics like language spoken (for bilingual environments), child-directed speech, and speaker category. However, the application is easily modifiable for any annotation needs. 

## What's what in this repo

Go to
* a description of the materials in the repo[description-of-materials-in-the-repo]
* an example work flow to process and annotate recordings[example-work-flow]

## Description of Materials In The Repo

### To prepare daylong audio recordings for annotation and annotate them

  1_chunk-and-label - a chopper + vocal activity dectector
          - chops longform recordings into 30 second clips
	  - runs standard vocal activity detector (Usoltsev, 2015)
	  - Creates accompanying metadata file `config.csv` which contains % vocal acvitity, timestamp of clip in original file, speaker metadata, filename, etc. 
	  
	  TODO: LIST all contents inside chunk-and-label
	
 2_categorize_app.py - GUI to walk research assistants through annotatating clips derived from 1_chunk-and-label. Categorize_app creates new file `responses.csv` that records annotations made through application + speaker and file metadata. 

### To compute bilingual dominance

Several notebooks to reliably estimate the bilingual dominance of speakers from daylong audio recordings. 

3_bilingual_ratio.ipynb - estimates the ratio between language categories for a given speaker using `responses.csv` from 2_categorize_app.py

4_rater_reliability.ipynb - estimates intra- and inter-rater agreement for language annotation on the basis of clips annotated two and three times. Also concatenates all clips annotated as 'unsure' into `filename_relisten.csv` to be fed into the Relisten application and listened to again.

5_relisten_app.py - to appear; draws all files that appear in the `filename_relisten.csv` dataframe to listen to again (without replacement)

## Example Work Flow

1. If you have multiple .wav files from a given day, sew them together and intersperse with white noise

	On the command line, type the following:
	
	``

2. Run the chopper and vocal activity detector

	Using the command line, move inside of `1_chunk-and-label/` and run the following:
	
	`python3 split_app.py`
	
	You will be prompted to select an audio file on your local machine to process:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/audio_cut_prompt.png "audio file prompt")
	
	You will be prompted to select a directory to store the chopped files and generated `config.csv` file:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/output_directory_prompt.png "output_directory_prompt")
	
	The speed of the VAD depends on your machine, but a good estimate is 1 second/clip or 24 minutes for a 12 hour recording. 
	
3. Begin annotation

	Again on the command line, run the annotation application. You will be prompted to select a `config.csv` file so it does not matter where `categorize_app.py` is stored on your machine
	
	`python3 categorize_app.py`
	
	You will be prompted to select a metadata file (`config.csv`):
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/metadata_prompt.png "metadata_prompt")

	You will be prompted to enter your name (to calculate inter-rater reliability in the event that you have multiple annotators):
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/name_prompt.png "name_prompt")
	
	The main interactive window will appear, which can be easily modified in the source code according to your annotation goals. In the current example, the following window is displayed:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/annotation_window.png "annotation_window")


	
4. 

## Citations

Usoltsev, A. Voice Activity Detector-Python. GitHub Repository. https://github.com/marsbroshok/VAD-python
