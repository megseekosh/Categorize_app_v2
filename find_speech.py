'''
    This file is meant to find speech in short audio files of one minute
'''
from pydub import AudioSegment
from pydub.utils import mediainfo
from pydub import silence

from vad import VoiceActivityDetector

# This simply looks for whether the volume is greater than a threshhold for
#   a given percentage of time
def volume_trial(file):
    # The threshhold of volume (decibels)
    threshhold = -45
    # The threshhold of total time over volume threshhold (seconds)
    length_seconds = 5

    # Get audio from file and data about audio
    audio = AudioSegment.from_file(file)
    data = mediainfo(file)

    # The number of samples in the audio per second of audio
    samples_per_second = int(len(audio)/float(data["duration"]))

    # The time threshhold in samples
    length_samples = length_seconds * samples_per_second

    # Find all sets of nonsilent samples
    nonsilences = silence.detect_nonsilent(audio, 1, silence_thresh=threshhold)

    # calculate total amount of nonsilences
    total = 0
    for i in nonsilences:
        total += i[1]-i[0]

    print(total/samples_per_second)
    if total >= length_samples:
        return True
    else:
        return False

# This gives the percentage of time in the audio file which has
#   triggers our voice activation tester
def vad_trial(file):
    # Create our detector
    v = VoiceActivityDetector(file)
    # Generate VAD intervals for the file
    speech_labels = v.convert_windows_to_readible_labels(v.detect_speech())

    # Get file info
    data = mediainfo(file)

    # Add all the times together
    total_time = 0
    for speech_data in speech_labels:
        # add the length of the speech
        total_time += speech_data['speech_end'] - speech_data['speech_begin']

    percent = total_time / float(data['duration'])

    return percent
