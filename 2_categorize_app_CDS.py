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




# clear category selection   
def clear():
    #mediacat.set(0)
    langcategory.set("Categorize language")
    speechcategory.set("Categorize speech")
    speakercategory.set("Categorize speaker")
    mediacategory.set("Categorize media")




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
	
	def close_window(annotate):
		annotate.destroy()

	tk.Label(annotate, text="What is your name?").grid(row=0)
	name = tk.Entry(annotate)
	def return_name():
		global content
		content = name.get()
	name.grid(row=0, column=1)


	tk.Button(annotate, text="Enter", command=combine_funcs(return_name, partial(close_window, annotate))).grid(row=7,column=1,columnspan=2)







#index and play audio file aloud
def play_audio():

    global row
    global audiofile
    row = df.sample(n=1).iloc[0] # just randomly sample from entire df
    if row['researcher_present']==1:
    	print('Researcher present in recording. Press Next.')
    elif row['percents_voc']==0: # if no vocal activity, skip the clip
        print('No vocal activity in clip. Press Next.')
   
    else:
        audiofile = os.path.join(row.outdir, row.file_name)
        row_file_name = row.file_name
    
        print(idx, row.file_name) # keep us updated about progress in terminal 

        subprocess.call(["play", audiofile])



#go to the next audio file 
def next_audio():

    language = langcategory.get() # get the language classification
    speech = speechcategory.get() # get the speech classification
    speaker = speakercategory.get() # get the speaker classification
    media = mediacategory.get() # get the media classification

    #media = mediacat.get() # 0=absent, 1=present
    annotate_date_YYYYMMDD = datetime.datetime.now() # get current annotation time
    print(language, speech, speaker, media, annotate_date_YYYYMMDD, content) 

    global row
    global resp_df
    allcols = pd.DataFrame([row]).assign(Language=language, Speech=speech, Speaker=speaker, Media=media, annotate_date_YYYYMMDD=annotate_date_YYYYMMDD, annotator=content) 
    resp_df = pd.concat([resp_df, allcols], sort=True)
    resp_df.to_csv(os.path.join(outdir, "responses.csv"), index=False)  # yes, this overwrites responses.csv each time  

    global idx 
    idx += 1 # update the global idx

    play_audio()


def repeat():
	subprocess.call(["play", audiofile])



def main():
	global langcategory
	global speechcategory
	global speakercategory
	global mediacategory
	#global mediacat

	root = tk.Tk() # refers to annotation window 

	root.update()

	root.title("Categorize")

	frame = tk.Frame(root, bg="white")
	frame.grid(row=8, column=8)

	langcategory = tk.StringVar() 
	speechcategory = tk.StringVar()
	speakercategory = tk.StringVar()
	mediacategory = tk.StringVar()


	langchoices = {"Spanish", "English/Quechua", "Mixed", "Unsure", "No speech", "PID"}
	speech_choices = {"ODS", "CDS", "Both", "Unsure"}
	speaker_choices = {"Single Adult Male", "Single Adult Female", "Multiple Adults", "Target Child", "Other Child(ren)", "Target Child & Adult(s)", "Other Child & Adult(s)", "Target Child & Other Child(ren)",  "Unsure", "Researcher"}
	media_choices = {"No media", "Spanish", "Quechua", "Mixed", "Unsure", "No Language"}


	langcategory.set("Categorize language")
	speechcategory.set("Categorize speech")
	speakercategory.set("Categorize speaker")
	mediacategory.set("Categorize media")


	popupMenu = tk.OptionMenu(frame, langcategory, *langchoices)
	popupMenu2 = tk.OptionMenu(frame, speechcategory, *speech_choices)
	popupMenu3 = tk.OptionMenu(frame, speakercategory, *speaker_choices)
	popupMenu4 = tk.OptionMenu(frame, mediacategory, *media_choices)

	popupMenu.grid(row=4, column=1)
	popupMenu2.grid(row=5, column=1)
	popupMenu3.grid(row=6, column=1)
	popupMenu4.grid(row=7, column=1)


	tk.Label(frame, text="Language: ").grid(row = 4, column = 0)
	tk.Label(frame, text="Speech: ").grid(row = 5, column = 0)
	tk.Label(frame, text="Speaker: ").grid(row = 6, column = 0)
	tk.Label(frame, text="Media: ").grid(row = 7, column = 0)

	#tk.Label(root, text="Media?").grid(row=10, column=8)
	#mediacat = tk.IntVar()
	#tk.Checkbutton(root, text='Yes', variable=mediacat).grid(row=10, column=9)

	tk.Button(frame, text="   Play   ", command=combine_funcs(play_audio, clear), bg="gray").grid(row=1, column=0) 

	tk.Button(frame, text="   Next   ", command=combine_funcs(next_audio, clear), bg="gray").grid(row=1, column=2) 

	tk.Button(frame, background="gray", text="   Repeat   ", command=repeat).grid(row=1, column=1)

	app = annotatorinfo()
	root.mainloop()  

if __name__ == "__main__":
	main()
