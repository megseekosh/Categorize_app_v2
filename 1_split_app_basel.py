# When running this in terminal, you need to specify the following args:
# child_ID birth_date record_date gender
# in that order. eg 'python split_app_luca.py 1234 20221231 20230131 baby'
# gender does not seem to be used outside of record-keeping purposes

import sys

# set global variables. otherwise functions that use sys.argv elements
# as default variables will throw errors.
if __name__ == "__main__":
    if len(sys.argv) < 5:
        raise SyntaxError("""Not enough arguments supplied. Please re-run.
            Next time, specify the following args:
            child_ID birth_date record_date gender
            in that order. eg 'python split_app_luca.py 1234 20221231 20230131 baby'""")
    child_ID = sys.argv[1]
    birth_date = sys.argv[2]
    record_date = sys.argv[3]
    gender = sys.argv[4]
else:
    child_ID = None
    birth_date = None
    record_date = None
    gender = None

# set the default value for 'globals' in main()
if "globals" in sys.argv:
    globalVars = True
else:
    globalVars = False

# For the file dialog
import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showinfo
# For the info output
import csv
import os
# These are used to split audio and tell its speech contents
from pydub import AudioSegment
from pydub.utils import mediainfo
from find_speech import vad_trial
# for merging segments
from scipy.optimize import minimize_scalar
import pandas as pd
from random import shuffle

# function to comb through a df and merge segments with the same label that are close in time
def merge_segments(df, max_distance, verbose=False, timed=False):
    """
    df: a pandas dataframe with columns ['segtype', 'startsec', 'endsec', 'duration']
    max_distance: maximum distance (in time) two segments can be from one another to be merged
    Returns the df with segments merged according to max_distance.
    Will add column 'checked_for_merge' to the original dataframe. Value is True if that row
    was checked.
    """
    if timed:
        import time
        start = time.time()
    # don't want to change original df, so will modify/return a copy (newdf)
    newdf = df.copy()
    # make a reference df that will 
    # make a list to keep track of whether we've already checked/merged a given row
    # only part of original df that will be modified
    df['checked_for_merge'] = False
    for row in df.itertuples():
        if not df.at[row.Index, 'checked_for_merge']:
            if verbose:
                print("Looking at row " + str(row.Index))
            # Merge this segment with any that have the same name, if they are
            # within a tolerable duration
            latest_startsec = row.endsec + max_distance
            # look for segments with start times between this row's start time
            # and this row's end time plus the maximum tolerable distance
            # i.e. subsequent instances of the same segment that are 'close enough'
            # (splitting the logic into multiple variables for the sake of legibility)
            timemask = (newdf['startsec'] >= row.endsec) & (newdf['startsec'] <= latest_startsec)
            segmask = newdf['segtype'] == row.segtype
            matches = newdf[timemask & segmask]
            # with those rows identified, start merging.
            if verbose:
                print(matches)
            if len(matches) > 0:  # if any rows match both masks
                # figure out the new end duration of the merged segment
                new_endsec = matches['endsec'].max()
                # we will merge all entries from the start time of our original second to 
                # the end time of the last eligible segment we are merging
                subdf = newdf[timemask & (newdf['endsec'] <= new_endsec)]
                if verbose:
                    print(subdf)
                # update the original entry with that new end duration
                newdf.at[row.Index, 'endsec'] = new_endsec
                # drop the rows we're merging from the new dataframe
                newdf = newdf.drop(subdf.index)
                # skip these rows if we would try to merge from them
                for j in subdf.index:
                    df.at[j, 'checked_for_merge'] = True
            df.at[row.Index, 'checked_for_merge'] = True
    if timed:
        end = time.time()
        print('took ' + str(end-start) + ' seconds')
    return newdf


def merge_adjacent_segments(df, max_distance=0, verbose=False):
    """
    df: a pandas dataframe with columns ['segtype', 'startsec', 'endsec', 'duration']
    max_distance: acceptable gap between two instances of the same segment
    This function goes row by row; for each row, it checks if the prev row is within
        max_distance seconds of the current row, and if they are, combines those two
        entries into one row. If there are multiple rows that satisfy these criteria
        they will be merged into one row.
    Returns the df with all merges.
    """
    # don't want to change original df, so will modify/return a copy (newdf)
    newdf = df.copy()
    # since indices were preserved from an original df, they may not be sequential
    indices = df.index
    for i in range(len(indices)):
        if verbose:
            print(i)
        # i is the index of a dataframe's index. so indices[0] is the first index of the df
        if i > 0:
            # get the df index (i is the index of that index)
            this_index = indices[i]
            # get the latest possible start time
            max_startsec = newdf.at[last_index, 'endsec'] + max_distance
            # check if the segments match and times are sequential
            mergeable = (newdf.at[last_index,'segtype'] == newdf.at[this_index, 'segtype']) and (newdf.at[this_index, 'startsec'] <= max_startsec)
            if mergeable:
                # set a new end time, merging into previous row
                newdf.at[last_index, 'endsec'] = df.at[this_index, 'endsec']
                # remove this row (as it is now merged into the prev one)
                newdf = newdf.drop(this_index)
                # don't update last_index - that index is still the one to compare against and merge into
            else:
                # get the previous df index
                last_index = this_index
        elif i == 0:
            last_index = indices[i]
    # recalculate durations
    # this is more easily vectorized so should go fast
    newdf['duration'] = newdf['endsec'] - newdf['startsec']
    return newdf


# function to evaluate how close a merge gets you to a certain distance
def evaluate_merged_durations(df, desired_median, max_distance=0):
    """
    df: a pandas dataframe with a 'duraton' column
    desired_median: the median duration you want
    max_distance: see help(merge_segments)
    Runs merge_segments, calculates the new median duration of segments, and
    returns its absolute value."""
    newdf = merge_segments(df, max_distance)
    new_median = newdf['duration'].median()
    answer = abs(new_median - desired_median)
    return answer


# optimize maximum distance
def optimize_merged_durations(dataframe, goal):
    def function_to_optimize(try_distance, goal=goal, df=dataframe):
        return evaluate_merged_durations(df, goal, max_distance=try_distance)
    return minimize_scalar(function_to_optimize, bracket=(0, goal*2), bounds=(0,9999))


# not sure why split_file was kept in a separate file before
def split_file(source_file, output_directory, segments_dataframe,
        child_ID=child_ID, record_date=record_date, verbose=True):
    # This is the audio input which we will be splitting
    sound = AudioSegment.from_file(source_file, format = 'wav')
    # This is metadata about the file we will be splitting
    data = mediainfo(source_file)
    # prepare file name format
    # figure out how many segments there are so we can prepend 0's
    # following line gets how many rows there are, converts it to a string, then counts 
    # the number of characters in the string, which will tell us how many digits we need
    # to reserve
    n_segments = len(str(len(segments_dataframe)))
    # should be like directory/childID_birthdate_rownumber
    output_format = '%s/'+ child_ID + '_' + record_date + '_%0' + str(n_segments) + 'd'
    # loop over the segments df and chop the audio file to match its segmentation
    rows_used = []
    for row in segments_dataframe.itertuples():
        # if this is a segment of interest, split it
        # identify time stamps
        start_ms = float(row.startsec) * 1000 # convert to ms
        end_ms = float(row.endsec) * 1000
        # generate file name
        this_filepath = output_format % (output_directory, row.Index)
        this_filepath = this_filepath + ".wav"
        if verbose:
            print(this_filepath)
        # remember that we are using this row (ie it's not filtered out)
        rows_used.append([row.Index, this_filepath])
        # split out the audio file
        split_sound = sound[start_ms:end_ms]
        split_sound.export(this_filepath,
                            format="wav",
                            bitrate=data["bit_rate"])
    print("Split into " + str(len(rows_used)) + " clips")
    return rows_used


def main(child_ID=sys.argv[1], birth_date=sys.argv[2], record_date=sys.argv[3], gender=sys.argv[4], globals=globalVars):
    """
    This is the user-oriented function which
       1. Asks the user for an audio file to process
       2. Asks the user for an output directory
       3. Splits the audio file using split_file()
       4. Writes the percent of vocal content found in each file to a .csv
           called config.csv in the output directory
    globals: set to True to make most variables global (eg for inspection)
    """
    # Tell the user what to do
    showinfo('Window', "Select an audio file to cut apart")
    # Get audio file
    if globals:
        global audio_file
    audio_file = askopenfilename(
                        filetypes =(("Audio File", "*.wav"),("all files","*.*")),
                        title = "Please choose a .wav file"
                    )
    print(audio_file)
    # If no file is selected
    if audio_file == '':
        return False

    # Tell the user what to do
    showinfo('Window', "Select the CSV file output by segments.pl")
    if globals:
        global segments_csv
    segments_csv = askopenfilename(
                        filetypes =(("CSV File", "*.csv"),("all files","*.*")),
                        title = "Please choose a .csv file generated by segments.pl"
                    )
    print(segments_csv)
    #if the directory was not selected
    if segments_csv == '':
        return False

    # Tell the user what to do
    showinfo('Window', "Select an output directory to save the audio chunks")
    # Select the output directory
    if globals:
        global output_dir
    output_dir = askdirectory()
    print(output_dir)

    #if the output directory was not selected
    if output_dir == '':
        return False

    # ask user to filter LENA segments
    unknown_preference = True
    # while loop means we don't crash if user gives input we don't like
    print() # line break to clearly separate this msg
    while unknown_preference:
        print("I can filter to only certain LENA annotations, or all but certain ones.")
        print("Please select the option you prefer:")
        print("1: Specify which LENA annotations to INCLUDE")
        print("2: Specify which LENA annotations to EXCLUDE")
        lena_selection_method = input("Your choice: ")
        if lena_selection_method in ("1", "2"):
            unknown_preference = False
            if lena_selection_method == "1":
                lena_selection_method = 'include'
            elif lena_selection_method == "2":
                lena_selection_method = 'exclude'
        else:
            print()
            print("Sorry, you need to type 1 or 2 and then press enter. Let's try again.")
    # check which LENA annotations to include
    if globals:
        global label_choices
    if lena_selection_method == 'include':
        print("Please type which LENA labels to include, separated by a comma. For example,"
        " typing 'FAN,MAN' (without quotes) will filter to Female Adult Near and Male Adult Near"
        " annotations.")
        label_choices = input("Labels to include: ")
    elif lena_selection_method == 'exclude':
        print("Please type which LENA labels to exclude, separated by a comma. For example,"
        " typing 'FAN,MAN' (without quotes) will filter out Female Adult Near and Male Adult Near"
        " annotations.")
        label_choices = input("Labels to exclude: ")
    # change text to uppercase in case of typo
    label_choices = label_choices.upper()
    # process label_choices from string to list
    label_choices = label_choices.split(',')
    # ask how much of a gap between segments is allowed
    print()
    print("I'll merge any sequential segments for you. How much of a gap should I allow?")
    tolerable_distance = input('Longest permissible gap (in seconds): ')
    # since we're already prompting here, also check what percentage of voicing is OK
    print("What's the minimum percentage of voicing you want? Clips with a lower percentage will be excluded.")
    minimum_voicing_percent = input("Minimum voicing percentage (eg '0.1' for 10%): ")
    minimum_voicing_percent = float(minimum_voicing_percent)
    # convert to number
    if '.' in tolerable_distance:
        tolerable_distance = float(tolerable_distance)
    else:
        tolerable_distance = int(tolerable_distance)

    # read the CSV output of segments.pl
    print("Reading segments data...")
    with open(segments_csv, newline='') as csvfile:
            segments_reader = csv.DictReader(csvfile, delimiter=',')
            segments_data = [row for row in segments_reader]

    # convert segments_data to better types, add duration
    for row in segments_data:
        row['startsec'] = float(row['startsec'])
        row['endsec'] = float(row['endsec'])
        row['duration'] = row['endsec'] - row['startsec']

    # make that into a pandas dataframe - helpful for merging segments later
    if globals:
        global segments_df
    segments_df = pd.DataFrame(segments_data)

    # filter to interesting segments
    print("Filtering segments with Lena...")
    # loop over the segments csv and chop the audio file to match its segmentation
    # limiting to choices made by user
    # add a column to the dataframe for which segments are interesting
    segments_df['interesting'] = False
    for i in range(len(segments_df)):
        row = segments_df.iloc[i]
        # filter according to user input
        if lena_selection_method == 'include':
            if row.segtype in label_choices:
                segments_df.at[i,'interesting'] = True
        elif lena_selection_method == 'exclude':
            if row.segtype not in label_choices:
                segments_df.at[i,'interesting'] = True
    # filter down to segments identified as interesting
    segments_df = segments_df[segments_df['interesting']]
    # no further need for the 'interesting' column
    segments_df = segments_df.drop(columns='interesting')

    # merge segments
    # first merge any segments that are already adjacent until there are no more
    print('Merging segments...')
    segments_df = merge_adjacent_segments(segments_df, max_distance=tolerable_distance)
    print("")    

    # Gather metadata
    print("Gathering metadata...")
    if globals:
        global rows_used
    rows_used = split_file(audio_file, output_dir, segments_df,
                           child_ID=child_ID, record_date=record_date)
    if globals:
        global clips_info
    clips_info = []     # this was originally called percents
    rejected_clips = []
    for i in range(len(rows_used)):
        # rows_used[i] is some info about a row. rows_used[i][0] is row info from segments.csv
        # rows_used[i][1] is the filepath of the audio that was split out for that segment
        filepath = rows_used[i][1]
        # categorize_app expects only the file name, not full path
        filename_for_csv = os.path.basename(filepath)
        row_index = rows_used[i][0]
        vad_percents = vad_trial(filepath)
        start_time = segments_df.at[row_index, 'startsec'] * 1000  # convert to ms
        end_time = segments_df.at[row_index, 'endsec'] * 1000
        duration = segments_df.at[row_index, 'duration']
        # clips_info will become a CSV with these columns:
        #      file name,  		 id,        age,       date,    gender,  start time,   percents,    end time,   duration of clip
        row = [filename_for_csv, child_ID, birth_date, record_date, gender, start_time, vad_percents, end_time, duration]
        # continue if this meets the voicing requirement, otherwise put it in the reject pile
        if vad_percents > minimum_voicing_percent:
            clips_info.append(row)
        else:
            rejected_clips.append(row)
    # randomize the order of rows
    shuffle(clips_info)


    # Write the config.csv data log file
    print("Writing the csv")
    with open(os.path.join(output_dir, "config.csv"), 'w') as output:
        writer = csv.writer(output, delimiter=',')
        #this makes the header for the rows
        writer.writerow(['file_name', 'id', 'age_YYMMDD', 'date_YYYYMMDD', 'gender', 'start_time', 'percents_voc', 'end_time', 'duration', 'researcher_present', 'sleeping'])
        #information for the rows
        #percents actually contains everything for all information
        writer.writerows(clips_info)
    # And the rejects.csv file
    with open(os.path.join(output_dir, "rejects.csv"), 'w') as output:
        writer = csv.writer(output, delimiter=',')
        #this makes the header for the rows
        writer.writerow(['file_name', 'id', 'age_YYMMDD', 'date_YYYYMMDD', 'gender', 'start_time', 'percents_voc', 'end_time', 'duration', 'researcher_present', 'sleeping'])
        #information for the rows
        writer.writerows(rejected_clips)
    return output_dir


# Running the script
if __name__ == '__main__':
    # Make sure the general tk window does not appear
    tk.Tk().withdraw()
    # Run the program
    output_directory = main()     # returns output directory
    print("Job's done! Output is at " + output_directory)
