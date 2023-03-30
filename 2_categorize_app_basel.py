#!/usr/bin/env python3

'''
app to read in and classify chunks of audio
Meg Cychosz & Ronald Sprouse
UC Berkeley

'''

import tkinter as tk
import tkinter.font as tkFont
import pandas as pd
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
from functools import partial
import os
import datetime
from playsound import playsound


# set how many ms of audio you want to annotate
desired_duration = 60 * 60 * 1000	 # in ms

#number of minute-audio-clips in folder; index of row in df
idx = 0
config_df = None
row = None
resp_df = None

duration_so_far = 0		# default value - nothing annotated so far
job_done = False		# will be true when we're done annotating
# if you want to change how many decimals the "annotation complete" window shows:
minute_decimals = 2


# clear category selection   
def clear():
	beginoptionscat.set("Categorize clip")
	langcategory.set("Categorize language")
	speakercategory.set("Categorize speaker")
	registercategory.set("Categorize register")
	comments.delete(0, 'end')


# need to give multiple commands to button below
def combine_funcs(*funcs):
	def combined_func(*args, **kwargs):
		for f in funcs:
			f(*args, **kwargs)
	return combined_func


# check if we are done annotating
def check_done(source_df, annotated_dur, desired_dur=desired_duration):
	# return True if done, False if not
	# check if we've annotated enough
	if annotated_dur > desired_dur:
		return True
	# check if there are more rows
	elif len(source_df) == 0:
		return True
	else:
		return False


# for notifying annotator that there's nothing left to code
def notify_finished():
	global job_done
	job_done = True
	# report duration annotated in minutes to 2 decimal places
	if duration_so_far > (60 * 1000):	# if duration > 1 min, print in min
		printed_duration = round(duration_so_far/1000/60, minute_decimals)
		unit = 'minutes'
	else:
		printed_duration = int(duration_so_far)
		unit = 'ms'
	return showinfo('Annotation complete', str(printed_duration) + ' ' + unit + " of audio have been"
		" annotated. Annotation is complete. You can close this app.")


# get initial info about annotator
def annotatorinfo():
	global config_df
	global outdir
	global content
	global resp_df
	global desired_duration
	global duration_so_far

	showinfo('Window', "Select a metadata file")
	fname = askopenfilename(filetypes =(("CSV File", "*.csv"),("all files","*.*")),
			 title = "Please choose a config.csv file")
	outdir = os.path.split(fname)[0]
	config_df = pd.read_csv(fname).assign(outdir=outdir) # the master config file

	try:
		resp_df = pd.read_csv(os.path.join(outdir, "responses.csv")) # if available, open the response df in read mode 
	except: # if not, create one
		empty = pd.DataFrame().assign(id=None, age_YYMMDD=None, date_YYYYMMDD=None, gender=None, file_name=None, percents_voc=None, outdir=None, researcher_present=None) # add addtl columns, file_name=None, 
		empty.to_csv(os.path.join(outdir, "responses.csv"), index=False) 
		resp_df = pd.read_csv(os.path.join(outdir, "responses.csv"))

	# we need to know the duration of clips that have been annotated so far
	if len(resp_df) > 0:
		# filter out anything annotated as non-speech
		filterdf = resp_df[resp_df['beginoptions'] != 'No speech']
		duration_so_far = sum(filterdf.tolist())
		# no change made to resp_df so that those annotations are preserved
	# it was already set to 0 at start of script, so no need for an else

	# we don't want to repeat any annotations. delete from df any rows with the same filename as one of the rows from resp_df
	forbidden_files = resp_df['file_name'].tolist()
	# if resp_df doesn't have any file names, we don't need to proceed
	if forbidden_files:
		# loop over df, check if its filename is in the prohibited list
		mask = config_df['file_name'].isin(forbidden_files)
		masked_df = config_df[mask]
		# get a list of indices for rows whose filenames we don't want to re-annotate
		forbidden_indices = [row.Index for row in masked_df.itertuples()]
		# drop them from df
		for i in forbidden_indices:
			config_df = config_df.drop(i, axis='index')
	# if config_df is empty, it means we don't have anything else to annotate
	if check_done(config_df, duration_so_far):
		notify_finished()
	else:
		annotate = tk.Toplevel()
		annotate.title("Annotator information")
		
		def close_window(annotate):
			annotate.destroy()

		tk.Label(annotate, text="What is your name?").grid(row=0)
		name = tk.Entry(annotate)
		def return_name():
			global content
			content = name.get()
		name.grid(row=0, column=1)

		# clicking "enter" also plays the first clip
		tk.Button(annotate, text="Enter", command=combine_funcs(return_name, partial(close_window, annotate), play_new_clip)).grid(row=7,column=1,columnspan=2)

# go to the next audio file
def next_audio():
	global repeat_ct
	global duration_so_far
	global config_df
	global row
	global resp_df

	beginoptions = beginoptionscat.get() # get the speaker classification	
	language = langcategory.get() # get the classification
	speaker = speakercategory.get() 
	register = registercategory.get() 
	clip_comments = comments.get()
	annotate_date_YYYYMMDD = datetime.datetime.now() # get current annotation time
	print(beginoptions, language, speaker, register, annotate_date_YYYYMMDD, content, clip_comments) 

	allcols = pd.DataFrame([row]).assign(beginoptions=beginoptions, Language=language, Speaker=speaker,  Register=register, comments=clip_comments, annotate_date_YYYYMMDD=annotate_date_YYYYMMDD, annotator=content, repeats=repeat_ct) 
	resp_df = pd.concat([resp_df, allcols], sort=True)
	resp_df.to_csv(os.path.join(outdir, "responses.csv"), index=False)  # yes, this overwrites responses.csv each time

	# update our duration counter
	duration_so_far += row['duration']

	# check if we are done, then ensure we don't pick this row again
	
	# check if we're done annotating
	if check_done(config_df, duration_so_far):
		notify_finished()
	else:
		# ensure we don't randomly select this row in the future
		config_df = config_df.drop(row.name)  # .name is where the original index is stored
		global idx 
		idx += 1 # update the global idx
		repeat_ct = int(0)

#index and play audio file aloud
def play_new_clip():
	global repeat_ct
	repeat_ct = int(0) 
	global row
	global audiofile

	# check if there's anything left to annotate. if so, randomly pick a row
	if check_done(config_df, duration_so_far):
		print("No more files to annotate")
		notify_finished()
	else:
		row = config_df.sample(n=1).iloc[0] # randomly sample from df
		if row['researcher_present']==1:
			print('Researcher present in recording.')
		elif row['percents_voc']==0: # if no vocal activity detected
			print('No vocal activity in clip.')
		elif row['sleeping']==1: # if child is sleeping
			print('Child is sleeping.')
		audiofile = os.path.join(row.outdir, row.file_name)
		print(idx, row.file_name) # keep us updated
		playsound(audiofile)



def next_and_play_audio():
	if not job_done:
		next_audio()
		play_new_clip()
	else:
		notify_finished()

	
def repeat():
	playsound(audiofile)
	global repeat_ct
	repeat_ct = repeat_ct + 1


def main():
	global beginoptionscat
	global langcategory
	global speakercategory
	global registercategory
	global comments

	root = tk.Tk() # refers to annotation window 
	root.update()
	root.title("Categorize")

	frame = tk.Frame(root, bg="white")
	frame.grid(row=15, column=15)
	beginoptionscat = tk.StringVar()
	langcategory = tk.StringVar()
	speakercategory = tk.StringVar() 
	registercategory = tk.StringVar()

	beginoptions_choices = {"No speech", "Unsure speaker and unsure language", "Categorize clip"}
	lang_choices = {"English", "Non-English language(s)", "Both"}
	speaker_choices = {"Main caregiver", "Not main caregiver(s)", "Both"}
	register_choices = {"ADS", "IDS", "Unsure/Both/Neither"}

	beginoptionscat.set("Categorize clip")
	langcategory.set("Categorize language")
	speakercategory.set("Categorize speaker")
	registercategory.set("Categorize register")

	popupMenu0 = tk.OptionMenu(frame, beginoptionscat, *beginoptions_choices)	
	popupMenu = tk.OptionMenu(frame, langcategory, *lang_choices)
	popupMenu1 = tk.OptionMenu(frame, speakercategory, *speaker_choices)
	popupMenu2 = tk.OptionMenu(frame, registercategory, *register_choices)

	popupMenu0.grid(row=3, column=1)
	popupMenu.grid(row=5, column=1)
	popupMenu1.grid(row=6, column=1)
	popupMenu2.grid(row=7, column=1)

	fontStyle = tkFont.Font(family="Lucida Grande", size=16, weight="bold")

	tk.Label(frame, font=fontStyle, text="Classify clip").grid(row=3, column=0)
	tk.Label(frame, text="Language: ").grid(row = 5, column = 0)
	tk.Label(frame, text="Speaker: ").grid(row = 6, column = 0)
	tk.Label(frame, text="Register:").grid(row=7, column=0)
	tk.Label(frame, font=fontStyle, text="Comments about clip?").grid(row=8, column=0)
	comments = tk.Entry(frame)
	comments.grid(row=8, column=1, columnspan=2)


	tk.Button(frame, background="gray", text="   Play   ", command=repeat).grid(row=1, column=0)
	tk.Button(frame, text="		Next	   ", command=combine_funcs(next_and_play_audio, clear), bg="gray").grid(row=1, column=2) 

	app = annotatorinfo()
	root.mainloop()

if __name__ == "__main__":
	main()
