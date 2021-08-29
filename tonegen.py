import argparse
import math
import struct
import wave
import sys

#-------------------------------------------------------------------------------
# generate sine_list
#-------------------------------------------------------------------------------
def gen_sine_list(freq, frate, nframes):
    sine_list = []
    for x in range(nframes):
        sine_list.append(math.sin(2.0*math.pi*freq*(x/frate)))
    
    return sine_list

#-------------------------------------------------------------------------------
# save tone to wav file
#-------------------------------------------------------------------------------
def gen_wav(fname, sine_list, freq, frate, amp, nframes):
    nchannels = 1
    sampwidth = 2
    comptype = "NONE"
    compname = "not compressed"

    wav_file = wave.open(fname, "w")
    wav_file.setparams((nchannels, sampwidth, frate, nframes,
        comptype, compname))

    for s in sine_list:
        # write the audio frames to file
        wav_file.writeframes(struct.pack('h', int(s*amp/2)))

    wav_file.close()

    return

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
def generateToneFile(freq, duration, outfile):

    params = {'Frequency': freq, 'Framerate': 44100, 'Time': duration}

    filename = outfile
    amplitude = 64000     # multiplier for amplitude (max is 65,520 for 16 bit)

    nframes = int (params['Time'] * params['Framerate'])

    sine_list = gen_sine_list(params['Frequency'], params['Framerate'], nframes)
    gen_wav(filename, sine_list, params['Frequency'], params['Framerate'], amplitude, nframes)
