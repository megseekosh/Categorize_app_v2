from pydub import AudioSegment
from pydub.utils import mediainfo

from math import ceil, log10
import sys

# Split file
# source_file is the filename of the audio we will be splitting
def split_file(source_file, output_directory="output"):
    child_ID = sys.argv[1]
    birth_date = sys.argv[2]


    # This is the audio input which we will be splitting
    sound = AudioSegment.from_file(source_file)

    # This is metadata about the file we will be splitting
    data = mediainfo(source_file)

    # This is a conversaion factor used to cut apart the audio into one minute
    #  chunks. Often sample_rate given can be slightly off, so I decided to use
    #  a more base approach, dividing the length (samples) by the duration (seconds)
    #  and scaling up by a factor of 60 (seconds per minute)
    #samples_per_minute = int(60*len(sound)/float(data["duration"]))

    #### NOW USING 30 SECOND CHUNKS 
    samples_per_minute = int(30*len(sound)/float(data["duration"]))

    # Get log_base_10 of number of minutes in the file to figure out how long
    #  the filename ids must be. If it is between 10 and 99 then all outputs
    #  must be formatted to length 2, i.e. 00, 01, 02... 10, 11, 12... 97, 98, 99
    #name_size = ceil(log10(float(data["duration"])/60))

    #### NOW USING 30 SECOND CHUNKS 
    name_size = ceil(log10(float(data["duration"])/30))


    # Number of minutes in the file, rounded upwards
    minutes = int(ceil(float(len(sound))/samples_per_minute))


###when hard coding add id and age in here
    #child_id = '1006'
    #child_age = '_060015_'

    # Loop through every minute of the audio and output it into the folder
    #  output as "output{n}.wav" where {n} = the minute id (starts at minute 0)
    #output_format = "%s/output%0"+str(name_size)+"d.wav"

    #changing the naming system of the file
    #output_format = "%s/output%0"+str(name_size)+"d" 
    output_format = '%s/'+ child_ID + '_' + birth_date + '_' + "%0"+str(name_size) +"d" 


    for i in range(minutes):
        #print("\t"+output_format % (output_directory, i))
        #split_sound = sound[i*samples_per_minute:(i+1)*samples_per_minute]
        #split_sound.export(output_format % (output_directory, i),
        #                    format="wav",
        #                    bitrate=data["bit_rate"])

        #adding in the variable 
        name_of_file = output_format % (output_directory, i)


        #name_of_file = name_of_file + child_id + child_age + ".wav"
        name_of_file = name_of_file + ".wav"
        print(name_of_file)
        split_sound = sound[i*samples_per_minute:(i+1)*samples_per_minute]
        split_sound.export(name_of_file,
                            format="wav",
                            bitrate=data["bit_rate"])

    return minutes
