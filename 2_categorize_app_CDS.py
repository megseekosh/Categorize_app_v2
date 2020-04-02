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
import tkinter.font as tkFont
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
    speaker1category.set("Categorize adult speaker(s)")
    lang1category.set("Categorize adult language")
    speech1category.set("Categorize adult speech")
    #speaker2category.set("Categorize speaker 2")
    lang2category.set("Categorize child language")
    speech2category.set("Categorize child speech")
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

        subprocess.call(["play", audiofile])



#go to the next audio file 
def next_audio():

    global repeat_ct


    speaker1 = speaker1category.get() # get the speaker classification
    language1 = lang1category.get() # get the language classification
    speech1 = speech1category.get() # get the speech classification
    #speaker2 = speaker2category.get() # get the speaker classification
    language2 = lang2category.get() # get the language classification
    speech2 = speech2category.get() # get the speech classification
    media = mediacategory.get() # get the media classification

    childvoc = childvoccat.get() # 0=absent, 1=present
    annotate_date_YYYYMMDD = datetime.datetime.now() # get current annotation time
    print(speaker1, language1, speech1, language2, speech2, media, childvoc, annotate_date_YYYYMMDD, content) 

    global row
    global resp_df
    allcols = pd.DataFrame([row]).assign(Adult_Speaker=speaker1, Adult_Language=language1, Adult_Speech=speech1, Other_Child_Language=language2, Other_Child_Speech=speech2, Media=media, Childvoc=childvoc, annotate_date_YYYYMMDD=annotate_date_YYYYMMDD, annotator=content, repeats=repeat_ct) 
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



def main():
	global speaker1category
	global lang1category
	global speech1category
	#global speaker2category
	global lang2category
	global speech2category
	global mediacategory
	global childvoccat

	root = tk.Tk() # refers to annotation window 

	root.update()

	root.title("Categorize")

	frame = tk.Frame(root, bg="white")
	frame.grid(row=15, column=15)

	speaker1category = tk.StringVar()
	lang1category = tk.StringVar() 
	speech1category = tk.StringVar()
	#speaker2category = tk.StringVar()
	lang2category = tk.StringVar() 
	speech2category = tk.StringVar()
	mediacategory = tk.StringVar()


	speaker1_choices = {"Single Adult Male", "Single Adult Female", "Multiple Adults", "Unsure", "Researcher", "PID", "No speech"}
	langchoices = {"Spanish", "English/Quechua", "Mixed", "Unsure"}
	speech_choices = {"ODS", "CDS", "Both", "Unsure"}
	#speaker2_choices = {"Other Child(ren)", "Unsure"}
	media_choices = {"No media", "Spanish", "Quechua", "Mixed", "Unsure", "No Language"}


	speaker1category.set("Categorize adult speaker")
	lang1category.set("Categorize adult language")
	speech1category.set("Categorize adult speech")
	#speaker2category.set("Categorize child speaker")
	lang2category.set("Categorize child language")
	speech2category.set("Categorize child speech")
	mediacategory.set("Categorize media")


	popupMenu = tk.OptionMenu(frame, speaker1category, *speaker1_choices)
	popupMenu1 = tk.OptionMenu(frame, lang1category, *langchoices)
	popupMenu2 = tk.OptionMenu(frame, speech1category, *speech_choices)
	#popupMenu3 = tk.OptionMenu(frame, speaker2category, *speaker2_choices)
	popupMenu4 = tk.OptionMenu(frame, lang2category, *langchoices)
	popupMenu5 = tk.OptionMenu(frame, speech2category, *speech_choices)
	popupMenu6 = tk.OptionMenu(frame, mediacategory, *media_choices)

	popupMenu.grid(row=4, column=1)
	popupMenu1.grid(row=5, column=1)
	popupMenu2.grid(row=6, column=1)
	#popupMenu3.grid(row=8, column=1)
	popupMenu4.grid(row=8, column=1)
	popupMenu5.grid(row=9, column=1)
	popupMenu6.grid(row=11, column=1)


	fontStyle = tkFont.Font(family="Lucida Grande", size=16, weight="bold")

	tk.Label(frame, font=fontStyle, text="Classify adults").grid(row=3, column=0)

	tk.Label(frame, text="Adult Speaker(s): ").grid(row = 4, column = 0)
	tk.Label(frame, text="Adult Language: ").grid(row = 5, column = 0)
	tk.Label(frame, text="Adult Speech: ").grid(row = 6, column = 0)

	tk.Label(frame, font=fontStyle, text="Classify other children").grid(row=7, column=0)

	#tk.Label(frame, text="Other Child Speaker(s): ").grid(row = 8, column = 0)
	tk.Label(frame, text="Other Child Language: ").grid(row = 8, column = 0)
	tk.Label(frame, text="Other Child Speech: ").grid(row = 9, column = 0)
	
	tk.Label(frame, font=fontStyle, text="Classify media").grid(row=10, column=0)

	tk.Label(frame, text="Media: ").grid(row = 11, column = 0)


	tk.Label(frame, font=fontStyle, text="Classify target child").grid(row=12, column=0)

	tk.Label(frame, text="Is the child vocalizing?").grid(row=13, column=0)
	childvoccat = tk.IntVar()
	tk.Checkbutton(frame, text='Yes', variable=childvoccat).grid(row=13, column=1)

	tk.Button(frame, text="     Play     ", command=combine_funcs(play_audio, clear), bg="gray").grid(row=1, column=0) 

	tk.Button(frame, text="        Next       ", command=combine_funcs(next_audio, clear), bg="gray").grid(row=1, column=2) 

	tk.Button(frame, background="gray", text="   Repeat   ", command=repeat).grid(row=1, column=1)

	app = annotatorinfo()
	root.mainloop()  

if __name__ == "__main__":
	main()
