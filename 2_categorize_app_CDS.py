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
    beginoptionscat.set("Categorize clip")



    adultTCcat.set("Categorize language to target child")
    adultOCcat.set("Categorize language to other child(ren)")
    adultOtherscat.set("Categorize language to other adults")
    adultUnsurecat.set("Categorize language to someone unknown")
    


    childTCcat.set("Categorize language to target child")
    childOCcat.set("Categorize language to other child(ren)")
    childAdultscat.set("Categorize language to adults")
    childUnsurecat.set("Categorize language to someone unknown")
    


    mediacategory.set("Categorize media")
    


    childvoccat.set(0)
    adultfemalecat.set(0)
    adultmalecat.set(0)
    adultscat.set(0)
    unsurecat.set(0)
    PIDcat.set(0)    	

    comments.delete(0, 'end')






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
    elif row['sleeping']==1: # if child is sleeping
        print('Child is sleeping. Press Next.')
   
    else:
        audiofile = os.path.join(row.outdir, row.file_name)
        row_file_name = row.file_name
    
        print(idx, row.file_name) # keep us updated about progress in terminal 

        subprocess.call(["afplay", audiofile])



#go to the next audio file 
def next_audio():

    global repeat_ct

    beginoptions = beginoptionscat.get() # get the speaker classification
    
    adult_tc = adultTCcat.get() # get the classification
    adult_oc = adultOCcat.get() 
    adult_others = adultOtherscat.get() 
    adult_unsure = adultUnsurecat.get() 
    
    
    OC_tc = childTCcat.get() 
    OC_oc = childOCcat.get() 
    OC_adults = childAdultscat.get() 
    OC_unsure = childUnsurecat.get() 
    

    media = mediacategory.get() # get the media classification
    childvoc = childvoccat.get() # 0=absent, 1=present
    adultfemale = adultfemalecat.get() 
    adultmale = adultmalecat.get() 
    adults = adultscat.get() 
    unsure = unsurecat.get() 
    PID = PIDcat.get()

    clip_comments = comments.get()



    annotate_date_YYYYMMDD = datetime.datetime.now() # get current annotation time
    print(beginoptions, adult_tc, adult_oc, adult_others, adult_unsure, OC_tc, OC_oc, OC_adults, OC_unsure, media, childvoc, adultfemale, adultmale, adults, unsure, PID, annotate_date_YYYYMMDD, content, clip_comments) 

    global row
    global resp_df
    allcols = pd.DataFrame([row]).assign(beginoptions=beginoptions, Adult2TargetChild=adult_tc, Adult2OtherChild=adult_oc,  Adultfemale=adultfemale, Adultmale=adultmale, Multiple_adults=adults, Unsure_adults=unsure, Adult2Others=adult_others, Adult2unsure=adult_unsure, Otherchild2TargetChild=OC_tc, Otherchild2OtherChild=OC_oc, Otherchild2adults=OC_adults, Otherchild2unsure=OC_unsure, Media=media, Childvoc=childvoc, PID=PID, comments=clip_comments, annotate_date_YYYYMMDD=annotate_date_YYYYMMDD, annotator=content, repeats=repeat_ct) 
    resp_df = pd.concat([resp_df, allcols], sort=True)
    resp_df.to_csv(os.path.join(outdir, "responses.csv"), index=False)  # yes, this overwrites responses.csv each time  

    global idx 
    idx += 1 # update the global idx

    repeat_ct = 0 

    play_audio()


	
def repeat():

	subprocess.call(["afplay", audiofile])

	global repeat_ct

	repeat_ct = repeat_ct + 1



def main():
	global beginoptionscat
	global adultTCcat
	global adultOCcat
	global adultOtherscat
	global adultUnsurecat
	global childTCcat
	global childOCcat
	global childAdultscat
	global childUnsurecat	
	global mediacategory
	global childvoccat
	global adultfemalecat
	global adultmalecat
	global adultscat
	global unsurecat
	global PIDcat
	global comments


	root = tk.Tk() # refers to annotation window 

	root.update()

	root.title("Categorize")

	frame = tk.Frame(root, bg="white")
	frame.grid(row=15, column=15)

	beginoptionscat = tk.StringVar()

	adultTCcat = tk.StringVar()
	adultOCcat = tk.StringVar() 
	adultOtherscat = tk.StringVar()
	adultUnsurecat = tk.StringVar()
	childTCcat = tk.StringVar() 
	childOCcat = tk.StringVar()
	childAdultscat = tk.StringVar()
	childUnsurecat = tk.StringVar()


	mediacategory = tk.StringVar()


	beginoptions_choices = {"No speech", "Unsure speaker and unsure language", "Categorize clip"}
	
	lang_choices = {"Spanish", "English/Quechua", "Mixed", "Unsure", "None"}
	
	media_choices = {"No media", "Spanish", "Quechua", "Mixed", "Unsure", "No Language"}

	beginoptionscat.set("Categorize clip")

	adultTCcat.set("Categorize speech to target child")
	adultOCcat.set("Categorize speech to other child(ren)")
	adultOtherscat.set("Categorize speech to other adults")
	adultUnsurecat.set("Categorize speech to unknown")
	childTCcat.set("Categorize speech to target child")
	childOCcat.set("Categorize speech to other child(ren)")
	childAdultscat.set("Categorize speech to other adults")
	childUnsurecat.set("Categorize speech to unknown")

	
	mediacategory.set("Categorize media")


	popupMenu0 = tk.OptionMenu(frame, beginoptionscat, *beginoptions_choices)
	
	popupMenu = tk.OptionMenu(frame, adultTCcat, *lang_choices)
	popupMenu1 = tk.OptionMenu(frame, adultOCcat, *lang_choices)
	popupMenu2 = tk.OptionMenu(frame, adultOtherscat, *lang_choices)
	popupMenu3 = tk.OptionMenu(frame, adultUnsurecat, *lang_choices)
	popupMenu4 = tk.OptionMenu(frame, childTCcat, *lang_choices)
	popupMenu5 = tk.OptionMenu(frame, childOCcat, *lang_choices)
	popupMenu7 = tk.OptionMenu(frame, childAdultscat, *lang_choices)
	popupMenu8 = tk.OptionMenu(frame, childUnsurecat, *lang_choices)
	popupMenu6 = tk.OptionMenu(frame, mediacategory, *media_choices)

	popupMenu0.grid(row=3, column=1)
	
	popupMenu.grid(row=5, column=1)
	popupMenu1.grid(row=6, column=1)
	popupMenu2.grid(row=9, column=1)
	popupMenu3.grid(row=10, column=1)
	popupMenu4.grid(row=13, column=1)
	popupMenu5.grid(row=14, column=1)
	popupMenu7.grid(row=15, column=1)
	popupMenu8.grid(row=16, column=1)

	
	popupMenu6.grid(row=18, column=1)


	fontStyle = tkFont.Font(family="Lucida Grande", size=16, weight="bold")

	tk.Label(frame, font=fontStyle, text="Classify clip").grid(row=3, column=0)

	


	tk.Label(frame, font=fontStyle, text="Classify adults to children").grid(row=4, column=0)
	tk.Label(frame, text="Adult(s) to target child: ").grid(row = 5, column = 0)
	tk.Label(frame, text="Adult(s) to other child(ren): ").grid(row = 6, column = 0)
	tk.Label(frame, text="Classify the adult(s) speaking:").grid(row=7, column=0)
	adultfemalecat = tk.IntVar()
	tk.Checkbutton(frame, text='Adult Female', variable=adultfemalecat).grid(row=7, column=1)


	adultmalecat = tk.IntVar()
	tk.Checkbutton(frame, text='Adult Male', variable=adultmalecat).grid(row=7, column=2)


	adultscat = tk.IntVar()
	tk.Checkbutton(frame, text='Multiple adults', variable=adultscat).grid(row=7, column=3)

	unsurecat = tk.IntVar()
	tk.Checkbutton(frame, text='Unsure', variable=unsurecat).grid(row=7, column=4)





	tk.Label(frame, font=fontStyle, text="Classify adults to adults").grid(row=8, column=0)
	tk.Label(frame, text="Adult(s) to other adult(s): ").grid(row = 9, column = 0)
	tk.Label(frame, text="Adult(s) to unknown: ").grid(row = 10, column = 0)





	tk.Label(frame, font=fontStyle, text="Classify other children").grid(row=12, column=0)

	tk.Label(frame, text="Child to target child: ").grid(row = 13, column = 0)
	tk.Label(frame, text="Child to other child(ren): ").grid(row = 14, column = 0)
	tk.Label(frame, text="Child to adult(s): ").grid(row = 15, column = 0)
	tk.Label(frame, text="Child to unknown: ").grid(row = 16, column = 0)

	
	tk.Label(frame, font=fontStyle, text="Classify media").grid(row=17, column=0)

	tk.Label(frame, text="Media: ").grid(row = 18, column = 0)


	tk.Label(frame, font=fontStyle, text="Classify target child").grid(row=19, column=0)
	tk.Label(frame, text="Is the child vocalizing?").grid(row=20, column=0)
	childvoccat = tk.IntVar()
	tk.Checkbutton(frame, text='Yes', variable=childvoccat).grid(row=20, column=1)




	tk.Label(frame, font=fontStyle, text="PID").grid(row=21, column=0)
	tk.Label(frame, text="Is there PID in the clip?").grid(row=23, column=0)
	PIDcat = tk.IntVar()
	tk.Checkbutton(frame, text='Yes', variable=PIDcat).grid(row=23, column=1)

	


	tk.Label(frame, font=fontStyle, text="Comments about clip?").grid(row=25, column=0)
	comments = tk.Entry(frame) 
	comments.grid(row=25, column=1, columnspan=2)




	tk.Button(frame, text="     Play     ", command=combine_funcs(play_audio, clear), bg="gray").grid(row=1, column=0) 

	tk.Button(frame, text="        Next       ", command=combine_funcs(next_audio, clear), bg="gray").grid(row=1, column=2) 

	tk.Button(frame, background="gray", text="   Repeat   ", command=repeat).grid(row=1, column=1)

	app = annotatorinfo()
	root.mainloop()  

if __name__ == "__main__":
	main()
