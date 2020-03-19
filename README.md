# Categorize_app 

GUI to chop, categorize, and annotate audio clips from daylong recordings. This version annotates ambient language characteristics like language spoken (for bilingual environments), child-directed speech, and speaker category. However, the application is easily modifiable for any annotation categories. 

## What's what in this repo

* [A description of the materials](#description-of-materials-in-the-repo)
* [An example work flow to process and annotate recordings](#example-work-flow)

## Description of Materials In The Repo

### To prepare daylong audio recordings for annotation and annotate them

  `1_chunk-and-label/`
  	  - a chopper + vocal activity dectector
          - chops longform recordings into 30 second clips
	  - runs standard vocal activity detector (Usoltsev, 2015)
	  - Creates accompanying metadata file `config.csv` which contains % vocal acvitity, timestamp of clip in original file, speaker metadata, filename, etc.
	  
	
 2_categorize_app_biling.py - GUI to walk research assistants through annotatating clips derived from 1_chunk-and-label. Includes annotation options for language choice, speaker, and presence/absence of media. Categorize_app creates new file `responses.csv` that records annotations made through application + speaker and file metadata. 
 
 2_categorize_app_CDS.py - same as above, but additionally includes a child-directed speech versus other-directed speech category 

### To compute bilingual dominance

Several notebooks to reliably estimate ambient language characteristics of daylong audio recordings. 

3a_bilingual_ratio.ipynb - estimates the ratio between language categories for a given speaker using `responses.csv` from 2_categorize_app_biling.py or 2_categorize_app_CDS.py

3b_speech_ratio.ipynb - estimates the ratio between type of speech categories (CDS, ODS) for a given speaker using `responses.csv` from 2_categorize_app_CDS.py

4_rater_reliability.ipynb - estimates intra- and inter-rater agreement for language annotation on the basis of clips annotated two and three times. Also concatenates all clips annotated as 'unsure' into `filename_relisten.csv` to be fed into the Relisten application and listened to again.

5_relisten_app.py - to appear; draws all files that appear in the `filename_relisten.csv` dataframe to listen to again (without replacement)

## Example Work Flow

This is an example of a workflow to get you from a full daylong recording to one annotated for ambient language characteristics like language choice and speech type via random sampling. It assumes that you have all relevant libraries and contingencies installed. 

1. If you have multiple .wav files from a given day, sew them together and intersperse with white noise such as `whiteNoise16.wav` (included in this repo). Interspersing white noise allows the annotator to know if a new recording has begun in the middle of a clip. 

	On the command line, type the following:
	
	`sox filename1.wav whiteNoise16.wav filename2.wav new_name_of_combined_files.wav` 

2. Run the chopper and vocal activity detector

	Using the command line, move inside of `1_chunk-and-label/` and run the following where childID is the ID of the participant (any length or format), birthdate is DDMMYYYY, recordingdate is DDMMYYYY, and gender is any way that you would like to code participant gender (e.g. 'Female', 'Non-binary', etc.). 
	
	`python3 split_app.py childID birthdate recordingdate gender`
	
	An example of this is the following:
	
	`python3 split_app.py 6396 06122018 05152019 female`
	
	After starting the application, you will be prompted with a window to select an audio file on your local machine to process:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/audio_cut_prompt.png "audio file prompt")
	
	You will be prompted with a window to select a directory to store the chopped files and generated `config.csv` file:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/output_directory_prompt.png "output_directory_prompt")
	
	The speed of the VAD depends on your machine, but a good estimate is 1 second/clip or 24 minutes for a 12 hour recording. 
	
3. Begin annotation

	Again on the command line, run the annotation application. You will be prompted to select a `config.csv` file so it does not matter where `categorize_app_CDS.py` is stored on your machine
	
	`python3 categorize_app_CDS.py`
	
	You will be prompted with a window to select the metadata file that you previously created (`config.csv`):
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/metadata_prompt.png "metadata_prompt")

	You will be prompted with a window to enter your name (to calculate inter-rater reliability in the event that you have multiple annotators):
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/name_prompt.png "name_prompt")
	
	The main interactive window will appear, which can be easily modified in the source code according to your annotation goals. In the current example, the following window is displayed:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/annotation_window.png "annotation_window")
	
	Press "Play." Various metadata details will display in the command line. After the clip, make your selection from the menus and hit "Next" or "Repeat". You can repeat as many times as you would like. To play the next clip in your current annotation session, always press "Next." 
	
	When you have completed with that annotation session, you can close the application and restart at any time. 
	
4. After you have annotated for a while, you may be interested in your progress. The next step is to run a notebook to evaluate when the ratio between annotation categories has asymptoted for a given recording, indicating that you can stop annotation. An example of this for language annotations in bilingual environments and speech type choices (e.g. child-directed speech) is the following:

	Move to the directory where you are storing `3a_bilingual_ratio.ipynb` and/or `3b_speech_ratio.ipynb` and type:
	
	`jupyter notebook`
	
	Select the notebook you would like to use from the webpage. 
	
	In the second cell of the notebook, write the path name to the `responses.csv` file on your computer for the participant. Run the notebook and evaluate your progress. 

## Citations

Usoltsev, A. Voice Activity Detector-Python. GitHub Repository. https://github.com/marsbroshok/VAD-python
