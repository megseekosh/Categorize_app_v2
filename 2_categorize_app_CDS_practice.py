#!/usr/bin/env python3

'''
app to read in and classify chunks of audio
Meg Cychosz & Ronald Sprouse
UC Berkeley

'''


try:
    import Tkinter as tk  # Python2
except ImportError:
    import tkinter as tk  # Python3
import pandas as pd
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
from functools import partial
import os
import subprocess
import datetime

from math import ceil, log10

#number of minute-audio-clips in folder; index of row in df
idx = 0
df = None
row = None
resp_df = None


# close window
def close_window(window):
	window.destroy()

# clear category selection   
def clear_speaker_window():
    speakercategory.set("Categorize speaker")

def clear_lang_window():
	langcategory.set("Categorize language")
	speechcategory.set("Categorize speech")
	mediacategory.set("Categorize media")
	childvoccat.set(0)





# need to give multiple commands to button below
def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func



# get initial info about annotator
def annotatorinfo():
	global df
	global outdir
	global content
	global resp_df

	showinfo('Window', "Select a metadata file")

	fname = askopenfilename()
	outdir = os.path.split(fname)[0]

	df = pd.read_csv(fname).assign(outdir=outdir) # the master config file that won't change

	try:
		resp_df = pd.read_csv(os.path.join(outdir, "responses.csv")) # if available, open the response df in read mode 

	except: # if not, create one
		empty = pd.DataFrame().assign(id=None, age_YYMMDD=None, date_YYYYMMDD=None, gender=None, timestamp_HHMMSS=None, percents_voc=None, outdir=None, researcher_present=None) # add addtl columns, file_name=None, 
		empty.to_csv(os.path.join(outdir, "responses.csv"), index=False) 
		resp_df = pd.read_csv(os.path.join(outdir, "responses.csv")) 


	annotate = tk.Toplevel()
	annotate.title("Annotator information")
	annotateSize = 220

	tk.Label(annotate, text="What is your name?").grid(row=0)
	name = tk.Entry(annotate)
	def return_name():
		global content
		content = name.get()
	name.grid(row=0, column=1)


	tk.Button(annotate, fg="blue", text="Enter", command=combine_funcs(return_name, partial(close_window, annotate))).grid(row=7,column=1,columnspan=2)







#index and play audio file aloud
def play_audio():

    global repeat_ct
    repeat_ct = 0 

    global row
    global audiofile
    row = df.sample(n=1).iloc[0] # just randomly sample from entire df
    if row['researcher_present']==1:
    	print('Researcher present in recording. Press Next.')
    elif row['percents_voc']==0: # if no vocal activity, skip the clip
        print('No vocal activity in clip. Press Next.')
    elif row['is_sleeping']==1: # if child is sleeping
        print('Child is sleeping. Press Next.')
   
    else:
        audiofile = os.path.join(row.outdir, row.file_name)
        row_file_name = row.file_name
    
        print(idx, row.file_name) # keep us updated about progress in terminal 

        #subprocess.call(["play", audiofile])



#go to the next audio file from the speaker categorization window
def next_audio_speaker():

    global repeat_ct

    speaker = speakercategory.get() # get the speaker classification, which will be 'no speech', 'researcher', or 'PID'

    
    language = 'NA' # these categories will be filled in for the purposes of the dataframe
    speech = 'NA'
    media = 'NA' 
    childvoc = 'NA'

    annotate_date_YYYYMMDD = datetime.datetime.now() # get current annotation time
    print(speaker, language, speech, media, childvoc, annotate_date_YYYYMMDD, content) 

    global row
    global resp_df
    allcols = pd.DataFrame([row]).assign(Speaker=speaker, Language=language, Speech=speech, Media=media, Childvoc=childvoc, annotate_date_YYYYMMDD=annotate_date_YYYYMMDD, annotator=content, repeats=int(repeat_ct)) 
    resp_df = pd.concat([resp_df, allcols], sort=True)
    resp_df.to_csv(os.path.join(outdir, "responses.csv"), index=False)  # yes, this overwrites responses.csv each time  

    global idx 
    idx += 1 # update the global idx

    repeat_ct = 0 

    play_audio()



def next_audio_lang():

    global repeat_ct # TODO this needs to be updated and counted across the two annotation windows


    speaker = speakercategory.get() # TODO this needs to be selected prior to running this function
    language = langcategory.get() # get the language classification
    speech = speechcategory.get() # get the speech classification
    media = mediacategory.get() # get the media classification

    childvoc = childvoccat.get() # 0=absent, 1=present
    annotate_date_YYYYMMDD = datetime.datetime.now() # get current annotation time
    print(speaker, language, speech, media, childvoc, annotate_date_YYYYMMDD, content) 

    global row
    global resp_df
    allcols = pd.DataFrame([row]).assign(Speaker=speaker, Language=language, Speech=speech, Media=media, Childvoc=childvoc, annotate_date_YYYYMMDD=annotate_date_YYYYMMDD, annotator=content, repeats=int(repeat_ct)) 
    resp_df = pd.concat([resp_df, allcols], sort=True)
    resp_df.to_csv(os.path.join(outdir, "responses.csv"), index=False)  # yes, this overwrites responses.csv each time  

    global idx 
    idx += 1 # update the global idx

    repeat_ct = 0 

    play_audio()


	
def repeat():

	subprocess.call(["play", audiofile])

	global repeat_ct

	repeat_ct = repeat_ct + 1




def speaker_choice():
	global speakercategory

	speak_root = tk.Toplevel() # refers to annotation window 

	speak_root.update()

	speak_root.title("Speaker categorization")

	speak_frame = tk.Frame(speak_root, bg="white")
	speak_frame.grid(row=10, column=10)

	speakercategory = tk.StringVar()

	speaker_choices = {"Single Adult Male", "Single Adult Female", "Multiple Adults", "Other Child(ren)", "Other Child(ren) & Adult(s)", "Unsure", "Researcher", "PID", "No speech"}

	speakercategory.set("Categorize speaker")

	popupMenu3 = tk.OptionMenu(speak_frame, speakercategory, *speaker_choices)

	popupMenu3.grid(row=4, column=1)

	tk.Label(speak_frame, text="Speaker: ").grid(row = 4, column = 0)

	tk.Button(speak_frame, text="   Play   ", command=combine_funcs(play_audio, clear_speaker_window), bg="gray").grid(row=1, column=0) # potential remove this from main function

	tk.Button(speak_frame, text="   Next   ", command=combine_funcs(next_audio_speaker, clear_speaker_window), bg="gray").grid(row=1, column=2) 

	tk.Button(speak_frame, background="gray", text="   Repeat   ", command=repeat).grid(row=1, column=1) 

	def close_window(speak_root):
		speak_root.destroy()	

	def choose_function():
		if speakercategory.get() == "Other Child(ren) & Adult(s)":
			main()

		else:
			main_else()

	tk.Button(speak_frame, fg="blue", text="Enter", command=combine_funcs(choose_function, partial(close_window, speak_root))).grid(row=6,column=2) # note that this hasn't returned the object...


	app = annotatorinfo() # causes metadata prompt to pop up
	speak_root.mainloop()






def main(): # the function that gives 2 options for language and 2 for speech
	global childlangcategory
	global childspeechcategory
	global adultlangcategory
	global adultspeechcategory
	global mediacategory
	global childvoccat

	root = tk.Toplevel() # refers to annotation window 

	root.update()

	root.title("Language and media categorization")

	frame = tk.Frame(root, bg="white")
	frame.grid(row=20, column=20)

	childlangcategory = tk.StringVar() 
	childspeechcategory = tk.StringVar()
	adultlangcategory = tk.StringVar() 
	adultspeechcategory = tk.StringVar()
	mediacategory = tk.StringVar()


	childlangchoices = {"Spanish", "English/Quechua", "Mixed", "Unsure"}
	adultlangchoices = {"Spanish", "English/Quechua", "Mixed", "Unsure"}
	child_speech_choices = {"ODS", "CDS", "Both", "Unsure"}
	adult_speech_choices = {"ODS", "CDS", "Both", "Unsure"}
	media_choices = {"No media", "Spanish", "Quechua", "Mixed", "Unsure", "No Language"}


	childlangcategory.set("Categorize child language")
	childspeechcategory.set("Categorize child speech")
	adultlangcategory.set("Categorize adult language")
	adultspeechcategory.set("Categorize adult speech")
	mediacategory.set("Categorize media")


	popupMenu = tk.OptionMenu(frame, childlangcategory, *childlangchoices)
	popupMenu1 = tk.OptionMenu(frame, childspeechcategory, *child_speech_choices)
	popupMenu2 = tk.OptionMenu(frame, adultlangcategory, *adultlangchoices)
	popupMenu3 = tk.OptionMenu(frame, adultspeechcategory, *adult_speech_choices)
	popupMenu4 = tk.OptionMenu(frame, mediacategory, *media_choices)

	popupMenu.grid(row=5, column=1)
	popupMenu1.grid(row=6, column=1)
	popupMenu2.grid(row=7, column=1)
	popupMenu3.grid(row=8, column=1)
	popupMenu4.grid(row=9, column=1)


	tk.Label(frame, text="Child Language: ").grid(row = 5, column = 0)
	tk.Label(frame, text="Child Speech: ").grid(row = 6, column = 0)
	tk.Label(frame, text="Adult Language: ").grid(row = 7, column = 0)
	tk.Label(frame, text="Adult Speech: ").grid(row = 8, column = 0)
	tk.Label(frame, text="Media: ").grid(row = 9, column = 0)

	tk.Label(frame, text="Is the child vocalizing?").grid(row=14, column=0)
	childvoccat = tk.IntVar()
	tk.Checkbutton(frame, text='Yes', variable=childvoccat).grid(row=14, column=1)

	#tk.Button(frame, text="   Play   ", command=combine_funcs(play_audio, clear_lang_window), bg="gray").grid(row=1, column=0) 

	tk.Button(frame, text="   Next   ", command=combine_funcs(next_audio_lang, clear_lang_window), bg="gray").grid(row=1, column=2) 

	tk.Button(frame, background="gray", text="   Repeat   ", command=repeat).grid(row=1, column=1)

	#app2 = speaker_choice()
	root.mainloop()  

def main_else(): # the function that only gives 1 option for language and speech
	global langcategory
	global speechcategory
	global mediacategory
	global childvoccat

	root = tk.Toplevel() # refers to annotation window 

	root.update()

	root.title("Language and media categorization")

	frame = tk.Frame(root, bg="white")
	frame.grid(row=8, column=8)

	langcategory = tk.StringVar() 
	speechcategory = tk.StringVar()
	mediacategory = tk.StringVar()


	langchoices = {"Spanish", "English/Quechua", "Mixed", "Unsure"}
	speech_choices = {"ODS", "CDS", "Both", "Unsure"}
	media_choices = {"No media", "Spanish", "Quechua", "Mixed", "Unsure", "No Language"}


	langcategory.set("Categorize language")
	speechcategory.set("Categorize speech")
	mediacategory.set("Categorize media")


	popupMenu = tk.OptionMenu(frame, langcategory, *langchoices)
	popupMenu2 = tk.OptionMenu(frame, speechcategory, *speech_choices)
	popupMenu4 = tk.OptionMenu(frame, mediacategory, *media_choices)

	popupMenu.grid(row=5, column=1)
	popupMenu2.grid(row=6, column=1)
	popupMenu4.grid(row=7, column=1)


	tk.Label(frame, text="Language: ").grid(row = 5, column = 0)
	tk.Label(frame, text="Speech: ").grid(row = 6, column = 0)
	tk.Label(frame, text="Media: ").grid(row = 7, column = 0)

	tk.Label(frame, text="Is the child vocalizing?").grid(row=10, column=8)
	childvoccat = tk.IntVar()
	tk.Checkbutton(frame, text='Yes', variable=childvoccat).grid(row=10, column=9)

	#tk.Button(frame, text="   Play   ", command=combine_funcs(play_audio, clear_lang_window), bg="gray").grid(row=1, column=0) 

	tk.Button(frame, text="   Next   ", command=combine_funcs(next_audio_lang, clear_lang_window), bg="gray").grid(row=1, column=2) 

	tk.Button(frame, background="gray", text="   Repeat   ", command=repeat).grid(row=1, column=1)

	#app2 = speaker_choice()
	root.mainloop()  

if __name__ == "__main__":
	speaker_choice()
	#main()
