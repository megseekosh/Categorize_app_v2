# Categorize_app 

GUI to chop, categorize, and annotate audio clips from daylong recordings. This version annotates ambient language characteristics like language spoken (for bilingual environments), child-directed speech, and speaker category. However, the application is easily modifiable for any annotation categories. 

## What's what in this repo

* [A description of the materials](#description-of-materials-in-the-repo)
* [An example work flow to process and annotate recordings](#example-work-flow)
* [Research output](#research-output)

## Dependencies 
The following dependencies are required to run the applications and scripts in this repo: `ffprobe`, `ffmpeg`, (both available [here](https://evermeet.cx/ffmpeg/)), `pydub`, `matplotlib`, `scipy`, and `pandas`. In addition, this repo is configured for Python 3.7.0 or older. That doesn't mean it's unworkable with newer versions, but you will likely have to create some work arounds. One solution is to configure a Python 3.7.0 environment within Anaconda:

	conda create --name py37 python=3.7.0 pip

	conda activate py37

## Description of Materials In The Repo

### To prepare daylong audio recordings for annotation and annotate them

  `1_chunk-and-label/`
  	  - a chopper + vocal activity dectector
          - chops longform recordings into 30 second clips
	  - runs standard vocal activity detector (Usoltsev, 2015)
	  - Creates accompanying metadata file `config.csv` which contains % vocal acvitity, timestamp of clip in original file, speaker metadata, filename, etc.
	  
`2_categorize_app_biling.py` - GUI to walk research assistants through annotatating clips derived from `1_chunk-and-label/`. Includes annotation options for language choice, speaker, and presence/absence of media. Categorize_app creates new file `responses.csv` that records annotations made through application + speaker and file metadata.

 
 `2_categorize_app_CDS.py` - same as above, but additionally includes a child-directed speech versus other-directed speech category 
 
  `2_categorize_app_CDS_entire.py` - same as above, but instead samples every other clip from the recording, in chronological order, instead of randomly from the recording

 
### To estimate ambient language characteristics

Several notebooks to reliably estimate ambient language characteristics of daylong audio recordings. 

`3a_bilingual_ratio.ipynb` - estimates the ratio between language categories for a given speaker using `responses.csv` from `2_categorize_app_biling.py` or `2_categorize_app_CDS.py`.

`3b_cds_biling_ratio.ipynb` - estimates the ratio between type of speech categories (CDS, ODS) for a given speaker using `responses.csv` from `2_categorize_app_CDS.py`

`4_rater_reliability.ipynb` - estimates intra- and inter-rater agreement for language annotation on the basis of clips annotated two and three times. Also concatenates all clips annotated as 'unsure' into `filename_relisten.csv` to be fed into the Relisten application and listened to again by two annotators.

`5_relisten_app.py` - to appear; draws all files that appear in the `filename_relisten.csv` dataframe to listen to again (without replacement)

`collect_responses.py` - to appear; a script that will collect all of the `responses.csv` files from all of the coded participants and concatenate them together in a single .csv for analysis

## Example Work Flow

This is an example of a workflow to get you from a full daylong recording to one annotated for ambient language characteristics like language choice and speech type via random sampling. It assumes that you have all relevant libraries and contingencies installed. 

1. (Optional) If you have multiple .wav files from a given day, sew them together and intersperse with white noise such as `whiteNoise16.wav` (included in this repo). Interspersing white noise allows the annotator to know if a new recording has begun in the middle of a clip. 

	On the command line, type the following:
	
	`sox filename1.wav whiteNoise16.wav filename2.wav new_name_of_combined_files.wav` 

2. Run the chopper and vocal activity detector

	Using the command line, move inside of `1_chunk-and-label/` and run the following where childID is the ID of the participant (any length or format), birthdate is YYMMDD, recordingdate is YYYYMMDD, and gender is any way that you would like to code participant gender (e.g. 'Female', 'Non-binary', etc.). 
	
	`python3 split_app.py childID birthdate recordingdate gender`
	
	An example of this is the following:
	
	`python3 split_app.py 6396 180612 20190515 female`
	
	After starting the application, you will be prompted with a window to select an audio file on your local machine to process:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/audio_cut_prompt.png "audio file prompt")
	
	You will be then prompted with a window to select a directory to store the chopped files and generated `config.csv` file:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/output_directory_prompt.png "output_directory_prompt")
	
	The speed of the VAD depends on your machine, but a good estimate is 1 second/clip or 24 minutes for a 12 hour recording. 
	
3. (Optional) Delimit parts of the recording that you may not want to annotate. 

	For example, you may not want to listen to any clips where the child is sleeping or where the researcher is present in the recording. That would be a waste of your time. The following example is our approach to finding and eliminating clips where the child is sleeping. You can always modify the source code of `split_app.py` to add additional parameters. 
	
	Open `config.csv` and note in the `percents_voc` column the clips that have a very, very low percentage of vocal activity (in the realm of 0-7%). Listen to the parts of the recording with this low activity/compare the timestamps to daily activity logs (if you have them) to ensure that the child is in fact sleeping. 
	
	Mark all of the clips where you believe the child to be sleeping with a `1` and all of the remaining clips with `0`. 
	
	Now when you annotate, you will continue to draw clips where the child is sleeping. However, you will not have to listen to them. Instead you will be prompted with the message `Child is sleeping. Press Next.` on the command line. So press next!
	
4. Begin annotation

	Again on the command line, run the annotation application `2_categorize_app_CDS.py`. You will be prompted to select a `config.csv` file so it does not matter where `2_categorize_app_CDS.py` is stored on your machine.
	
	`python3 2_categorize_app_CDS.py`
	
	You will be prompted with a window to select the metadata file that you previously created (`config.csv`):
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/metadata_prompt.png "metadata_prompt")

	You will be prompted with a window to enter your name (to calculate inter-rater reliability in the event that you have multiple annotators):
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/name_prompt.png "name_prompt")
	
	The main interactive window will appear, which can be easily modified in the source code according to your annotation goals. In the current example, the following window is displayed:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/annotation_window.png "annotation_window")
	
	Press "Play." Various metadata details will display in the command line. After the clip, make your selection from the menus and hit "Next" or "Repeat". You can repeat as many times as you would like. To play the next clip in your current annotation session, always press "Next." 
	
	When you have completed with that annotation session, you can close the application and restart at any time. There is nothing else that you have to do. Your responses will always be recorded in `responses.csv`
	
5. After you have annotated for a while, you may be interested in your progress. The next step is to run a notebook to evaluate when the ratio between annotation categories has asymptoted for a given recording, indicating that you can stop annotation. An example of this for language annotations in bilingual environments and speech type choices (e.g. child-directed speech) is the following:

	Move to the directory where you are storing `3a_bilingual_ratio.ipynb` and/or `3b_cds_biling_ratio.ipynb` and type:
	
	`jupyter notebook`
	
	Select the notebook you would like to use from the webpage. 
	
	In the second cell of the notebook, write the path name to the `responses.csv` file on your computer for the participant. 
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/path_cell.png "path_cell")

	Run the remainder of the notebook and evaluate your progress. For example, the following area plot demonstrates that the language categories have stablized for this participant:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/stable_area_plot.png "stable_area_plot")
	

## Research Output
  `Cychosz_Villaneuva_Weisleder` - poster from recent Many Paths to Language Acquisition Conference demosntrating the validity of the random sampling approach
  
  `Villaneuva_Cychosz_Weisleder` - poster from recent Many Paths to Language Acquisition Conference documenting dual language input in the US and Bolivia
  
  `validation_results.Rmd` - R notebook to generate results and analyses for `MPAL_poster`
  
  `validation_results.pdf` - Results PDF generated by `validation_results.Rmd`
  
  `validation_results_files/` - directory with figures generated by `validation_results.Rmd`

## Citations

Villaneuva, A., Cychosz, M., & Weisleder, A. (2020). Dual language input from adults and older children in two communities. Poster to given at the Many Paths to Language Acquisition Workshop, Nijmegen, The Netherlands.

Cychosz, M., Villanueva, A., & Weisleder, A. (2020). Efficient estimation of bilingual children’s language exposure from daylong audio recordings. Poster to given at the Many Paths to Language Acquisition Workshop, Nijmegen, The Netherlands.

Usoltsev, A. (2015). Voice Activity Detector-Python. GitHub Repository. https://github.com/marsbroshok/VAD-python
