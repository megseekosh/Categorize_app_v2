# Categorize_app 

GUI to chop, categorize, and annotate audio clips from daylong recordings.

## What's new in this fork

* Includes segments.pl to make use of LENA .its files (source: [https://github.com/HomeBankCode/lena-its-tools/blob/master/segments.pl](https://github.com/HomeBankCode/lena-its-tools/blob/3ae8e06b1042956ac9e0cf273be926a6764594e1/segments.pl))
* Used LENA annotations rather than the original vocal activity detector. Now you can filter to only certain LENA annotations, or exclude certain ones.
* Modified annotation script to use `playaudio` so that it can be used on Windows
* Slightly simplified annotation workflow - no need to press "Play" for the first file you annotate
* Annotation script keeps track of the total duration of annotated clips so far and stops you when you've annotated an hour of clips
* Dropdown menu options are read from a text file to allow easier editing by users who don't want to modify the python script

## What's what in this repo

* [A description of the materials](#description-of-materials-in-the-repo)
* [An example work flow to process and annotate recordings](#example-work-flow)

## Dependencies 
The following dependencies are required to run the applications and scripts in this repo: `ffprobe`, `ffmpeg`, (both available [here](https://evermeet.cx/ffmpeg/)), `playaudio`, `pydub`, `matplotlib`, `scipy`, and `pandas`. In addition, this repo is configured for Python 3.7.0 or older. That doesn't mean it's unworkable with newer versions, but you may have to create some work arounds. One solution is to configure a Python 3.7.0 environment within Anaconda:

	conda create --name py37 python=3.7.0 pip

	conda activate py37

## Description of Materials In The Repo

### To prepare daylong audio recordings for annotation and annotate them

`1_split_app_basel.py`
	- chops longform recordings into clips according to their LENA annotations
	- Creates accompanying metadata file `config.csv` which contains % vocal acvitity, timestamp of clip in original file, speaker metadata, filename, etc.
	  
`2_categorize_app_biling.py` - GUI to walk research assistants through annotatating clips derived from `1_chunk-and-label/split_app_basel.py`. Categorize_app creates new file `responses.csv` that records annotations made through application + speaker and file metadata.

### To estimate ambient language characteristics

Several notebooks to reliably estimate ambient language characteristics of daylong audio recordings. As of March 15 2023 these have not been updated from the original repo and may need adjustments to work properly.

`4_rater_reliability.ipynb` - estimates intra- and inter-rater agreement for language annotation on the basis of clips annotated two and three times. Also concatenates all clips annotated as 'unsure' into `filename_relisten.csv` to be fed into the Relisten application and listened to again by two annotators.

## Example Work Flow

This is an example of a workflow to get you from a full daylong recording to one annotated for ambient language characteristics like language choice and speech type via random sampling. It assumes that you have all relevant libraries and contingencies installed. 

0. Collect a .wav file you want to annotate and a corresponding LENA .its file

2. Run `segments.pl`, e.g. by `perl segments.pl itsfile segments.csv`

3. Run `1_split_app_basel.py`

	Using the command line, move inside of `1_chunk-and-label/` and run the following where childID is the ID of the participant (any length or format), birthdate is YYMMDD, recordingdate is YYYYMMDD, and gender is any way that you would like to code participant gender (e.g. 'Female', 'Non-binary', etc.). 
	
	`python3 split_app.py childID birthdate recordingdate gender`
	
	An example of this is the following:
	
	`python3 split_app.py 6396 180612 20190515 female`
	
	After starting the application, you will be prompted with a window to select an audio file on your local machine to process:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/audio_cut_prompt.png "audio file prompt")
	
	You will be then prompted with a window to select a directory to store the chopped files and generated `config.csv` file:
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/output_directory_prompt.png "output_directory_prompt")
	
4. Customize dropdown menu options if desired

	`2a_categorize_beginoptions.txt`, `2b_categorize_language.txt`, `2c_categorize_speaker.txt`, and `2d_categorize_register.txt` should be placed in the same directory as `2_categorize_app_basel.py`. `2_categorize_app_basel.py` will automatically read these files and use them to populate the dropdown menu options for annotation.
	If you'd like to change these options, just edit the appropriate text file. Each option should be followed by a line break. You can use the default options as examples.

6. Begin annotation

	Again on the command line, run the annotation application `2_categorize_app_basel.py`. You will be prompted to select a `config.csv` file so it does not matter where `2_categorize_app_basel.py` is stored on your machine.
	
	`python3 2_categorize_app_CDS.py`
	
	You will be prompted with a window to select the metadata file that you previously created (`config.csv`):
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/metadata_prompt.png "metadata_prompt")

	You will be prompted with a window to enter your name (to calculate inter-rater reliability in the event that you have multiple annotators):
	
	![alt text](https://github.com/megseekosh/Categorize_app_v2/blob/master/name_prompt.png "name_prompt")
	
	The main interactive window will appear, which can be easily modified in the source code according to your annotation goals.
	
	As you annotate, various metadata details will display in the command line. After the clip, make your selection from the menus and hit "Next" or "Play." You can repeat as many times as you would like. To play the next clip in your current annotation session, press "Next." 
	
	When you have completed that annotation session, you can close the application and restart at any time. There is nothing else that you have to do. Your responses will always be recorded in `responses.csv` - they are saved when you press "Next."
	
	When you have annotated 60 minutes of audio, you will be prompted with a message indicating that you have finished annotation. You can change this duration by changing the variable `desired_duration` in `2_categorize_app_basel.py`.

## Citations

Villaneuva, A., Cychosz, M., & Weisleder, A. (2020). Dual language input from adults and older children in two communities. Poster to given at the Many Paths to Language Acquisition Workshop, Nijmegen, The Netherlands.

Cychosz, M., Villanueva, A., & Weisleder, A. (to appear). Efficient estimation of children’s language exposure in two bilingual communities. *Journal of Speech, Language, and Hearing Research.* https://psyarxiv.com/dy6v2/

Usoltsev, A. (2015). Voice Activity Detector-Python. GitHub Repository. https://github.com/marsbroshok/VAD-python
