# For the file dialog
import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showinfo

# For the info output
import csv

import sys

# These are used to split audio and tell its speech contents
from split_audio import split_file
from find_speech import vad_trial

# Used for formatting the file outputs
from math import log10, ceil

# This is the user-oriented function which
#       1. Asks the user for an audio file to process
#       2. Asks the user for an output directory
#       3. Splits the audio file into 1-minute chunks and puts them in the
#           output directory
#       4. Writes the percent of vocal content found in each file to a .csv
#           called config.csv in the output directory
def select_and_slice_file():
    # Tell the user what to do
    showinfo('Window', "Select an audio file to cut apart")
    # Get audio file
    audio_file = askopenfilename(
                        filetypes =(("Audio File", "*.wav"),("all files","*.*")),
                        title = "Please choose a .wav file."
                    )
    print(audio_file)

    # If no file is selected
    if audio_file == '':
        return False

    # Tell the user what to do
    showinfo('Window', "Select an output directory to save the audio chunks")

    # Select the output directory
    output_dir = askdirectory()
    print(output_dir)

    #if the output directory was not selected
    if output_dir == '':
        return False

    # Split audio file
    print("splitting file")
    filecount = split_file(audio_file, output_dir)

    # Run the Voice Activation Detector on each file
    percents = []


    #to set up timestamp
    hours = 0
    mins = 0
    secs = 0

    print("vad_trial init")
    for file in range(filecount):
        #filename = (output_dir+'/output%0'+str(ceil(log10(filecount)))+'d.wav')%file
        #filename_progress = (output_dir+'/output%0'+str(ceil(log10(filecount)))+'d')%file
        #filename = filename_progress + '_1010' + '_YYMMDD' + '.wav'


        filename_progress = ('%0'+str(ceil(log10(filecount)))+'d')%file

###when hard coding add id and age in here - for next 2 lines!!
        filename = output_dir + '/' + child_ID + '_' + birth_date + '_' + filename_progress + '.wav'
        filename_for_csv = child_ID + '_' + birth_date + '_' + filename_progress + '.wav'


        print("\t" + filename)
        #percents.append([vad_trial(filename)])

        #calculating the timestamp 
        if hours < 10:
            hours_string = str(0)+str(hours)
        else:
            hours_string = str(hours)
        if mins < 10:
            mins_string = str(0)+str(mins)
        else:
            mins_string = str(mins)
        if secs == 0:
            secs_string = ':00'
        else:
            secs_string = ':30'

        timestamp = hours_string + ':' + mins_string + secs_string

        if secs == 30:
            if mins == 59:
                hours += 1
                mins = 0
                secs = 0
            else:
                mins+=1
                secs = 0
        else:
            secs = 30


###when hard coding add all details in here: id, age, date, gender 
        #to get multiple columns we add everything to what was just the "percents" list
        #in order of    file name,  		 id,        age,       date,    gender,  timestamp,   percents
        percents.append([filename_for_csv, child_ID, birth_date, record_date, gender, timestamp, vad_trial(filename)])

    # Write the csv data log file
    print("writing the csv")
    with open(output_dir+"/config.csv", 'w') as output:
        #writer = csv.writer(output)
        #writer.writerows(percents)


        #changed to add details to config
        writer = csv.writer(output, delimiter=',')

        #this makes the header for the rows 
        writer.writerow(['file_name', 'id', 'age_YYMMDD', 'date_YYYYMMDD', 'gender', 'timestamp_HHMMSS', 'percents_voc', 'researcher_present', 'sleeping'])

        #information for the rows 
        #percents actually contains everything for all information
        writer.writerows(percents)


# The running program
if __name__ == '__main__':
    child_ID = sys.argv[1]
    birth_date = sys.argv[2]
    record_date = sys.argv[3]
    gender = sys.argv[4]
    # Make sure the general tk window does not appear
    tk.Tk().withdraw()
    # Run the program
    select_and_slice_file()
