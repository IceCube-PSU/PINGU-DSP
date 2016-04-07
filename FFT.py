import numpy as np
import os
import matplotlib.pyplot as plt

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles):

    rawText = open(infile)

    wavecounter = 0

    xvals = []
    yvals = []
    ysum = 0.0
    baseline = 0.0
    baseline_std = 0.0
    nlines = 0
    bins = 0
    areas = []
    FFTLen = 0

    for line in rawText.readlines():
        
#        if nlines > 100:
#            break

        nlines += 1

        splits = line.split(",")
        if len(splits) == 6:
            adcbin = int(splits[0])
            adcval = float(splits[1])
            newWaveform = int(splits[4]) # Waveform ends when last number in row==1
            if not newWaveform:
                xvals.append(float(adcbin)*4) # Multiply by 4 since one sample is 4 nanoseconds
                yvals.append(adcval)
                bins += 1

            # we're finished with the current waveform and can calculate
            # the area and peak pulseheight under the putative pulse
            else:

                 if len(xvals) > 200: # skip cases with too few digitizations
                     
                    print "Length of yvals: ",len(yvals)
                     
                    StdFFT = np.fft.fft(yvals)
                    FFTLen = len(StdFFT)
                    StdFrequenciesFFT = np.fft.fftfreq(FFTLen)
                    StdFrequencies = np.fft.fftfreq(FFTLen,4.e-9)/1.e6 # units are MHz
                    StdPowerSpectrum = np.abs(StdFFT)**2

                    StdFFT_LowPass = StdFFT.copy()
                    StdFFT_LowPass[0] = 0.0 # remove mean (baseline) 
                    MaxFreq = 50. # maximum frequency in MHz                       
                    StdFFT_LowPass[(StdFrequencies>MaxFreq)] = 0.0     # remove high frequencies
                    StdFFT_LowPass[(StdFrequencies<-MaxFreq)] = 0.0     # remove high negative frequencies, too
                    StdPowerSpectrum_LowPass = np.abs(StdFFT_LowPass)**2
                                                            
                    yvals_LowPass = np.fft.ifft(StdFFT_LowPass)
                    
#                    print yvals
#                    print yvals_LowPass
                    
#                    fig, axes = plt.subplots(nrows=4, ncols=4)
#                    fig.tight_layout() # Or equivalently,  "plt.tight_layout()"
                                                            
                                                                                                                                                                                                        
                    plt.subplot2grid((2,2), (0, 0), colspan=1)
                    plt.ylim(4760.,4840.)
                    plt.ylabel('Counts')
                    plt.xlabel('time (ns)')
                    plt.plot(xvals,yvals,'b')
 
                    plt.subplot2grid((2,2), (0, 1), colspan=1)
                    plt.xlim(-10.,140.)
                    plt.ylim(1.0e-2,1.0e8)
                    plt.ylabel('Std Power Spectrum')
                    plt.xlabel('Frequency (MHz)')
                    plt.semilogy(StdFrequencies[0:FFTLen/2+1],StdPowerSpectrum[0:FFTLen/2+1],'r')

                    plt.subplot2grid((2,2), (1, 0), colspan=1)
                    plt.ylim(-40.,40.)
                    plt.ylabel('Counts (LowPass)')
                    plt.xlabel('time (ns)')
                    plt.plot(xvals,yvals_LowPass,'b')
 
                    plt.subplot2grid((2,2), (1, 1), colspan=1)
                    plt.xlim(-10.,140.)
                    plt.ylim(1.0e-2,1.0e8)
                    plt.ylabel('Std Power Spectrum (LowPass)')
                    plt.xlabel('Frequency (MHz)')
                    plt.semilogy(StdFrequencies[0:FFTLen/2+1],StdPowerSpectrum_LowPass[0:FFTLen/2+1],'r')
                    
                    plt.tight_layout()

#                    plt.subplot2grid((3,1), (2, 0), colspan=1)
#                    plt.ylim(4750.,4850.)
#                    plt.ylabel('iFFT Counts')
#                    plt.xlabel('time (ns)')
#                    plt.plot(xvals,iStdFFT,'b')
 
                   
#                    plt.subplot2grid((3,1), (2, 0), colspan=1)
#                    plt.ylim(1.0e-2,1.0e8)
#                    plt.ylabel('Std Power Spectrum')
#                    plt.xlabel('Frequency (MHz)')
#                    plt.semilogy(StdFrequencies[0:FFTLen/2+1],StdPowerSpectrum[0:FFTLen/2+1],'r')
                                                            
                    plt.show()

                    yvals = []
                    xvals = []

                    bins = 1

    print "Number of lines processed in file: ",infile," = ",nlines

    return 1 # hack to prevent error message at end of processing


parser = ArgumentParser(description=
                        '''Plots the waveforms for some input files''',
                        formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument('-f','--file_list',
                    nargs='*',
                    required = True,
                    help="Input waveform files to analyse")
parser.add_argument('-osc','--oscilloscope',
                    action = 'store_true',
                    default = False,
                    help="Flag for oscilloscope waveforms")
parser.add_argument('-ddc2','--DDC2',
                    action = 'store_true',
                    default = False,
                    help="Flag for DDC2 waveforms")
parser.add_argument('-n','--numcounts',
                    type=int,
                    help="Number of DDC2 samples in single pulse window")
parser.add_argument('-o','--output',
                    type=str,
                    default="output.txt",
                    metavar='TXTFILE',
                    help="Name of output file to read whether the pulses pass the threshold(s) or not")
parser.add_argument('-s','--save_figs',
                    action='store_true',
                    default = False,
                    help="Saves all of the waveform plots")
parser.add_argument('-d','--save_dir',
                    action='store',
                    default='CWD',
                    help="Directory to save output waveform plots")
parser.add_argument('-p','--peakpedestal',
                    action='store_true',
                    default=False,
                    help="Plot and save the gain histograms for all entries")

args = parser.parse_args()

files = args.file_list
save_figs = args.save_figs
outfile = args.output
outdir = args.save_dir
oscilloscope = args.oscilloscope
DDC2 = args.DDC2
ymax = args.numcounts
peakpedestal = args.peakpedestal

DoIt = True
if DoIt:

    if outdir == 'CWD':
        outdir = os.getcwd()

    if oscilloscope:

        Threshold = -5
        SecondThreshold = -7
        SumThreshold = -15
        TotalSumThreshold = -500
        DoublePulseThreshold = -3500

    elif DDC2:

        Threshold = 4790
        SecondThreshold = 4800
        SumThreshold = 10000
        TotalSumThreshold = 191300.0
        DoublePulseThreshold = 191560.0

    NumPulseFiles = {}
    NumPulseFiles["bySingleThreshold"] = 0
    NumPulseFiles["byIncreasingAmplitude"] = 0
    NumPulseFiles["byDoubleThreshold"] = 0
    NumPulseFiles["bySecondThreshold"] = 0
    NumPulseFiles["bySumThreshold"] = 0
    NumPulseFiles["byTotalAmplitudeSum"] = 0
    NumPulseFiles["PossibleDoublePulses"] = 0

    outfile = open(outfile, 'w')

    outfile.write("\n")
    outfile.write("Explanation of headers:\n")
    outfile.write("\n")
    outfile.write("FN - File Name\n")
    outfile.write("TA - Total Amplitude. Requires total amplitude of all bins to be above %f\n"%TotalSumThreshold)
    outfile.write("SiT - Single Threshold. Requires one bin to go above %f\n"%Threshold)
    outfile.write("IA - Increasing Amplitude. Requires SiT and then subsequent bin to increase from this.\n")
    outfile.write("DT - Double Threshold. Requires SiT and then subsequent bin to also be above %f\n"%Threshold)
    outfile.write("SeT - Second Threshold. Requires SiT and then subsequent bin to be above %f\n"%SecondThreshold)
    outfile.write("SuT - Sum Threshold. Requires SiT and then sum of this plus subsequent bin to be above %f\n"%SumThreshold)
    outfile.write("DP - Possible Double Pulse Files. The total amplitude is above %f\n"%DoublePulseThreshold)
    outfile.write("\n")
    outfile.write("%-*s %-*s %-*s %-*s %-*s %-*s %-*s %-*s\n" % (11,"FN",11,"TA",11,"SiT",11,"IA",11,"DT",11,"SeT",11,"SuT",11,"DP"))

#    if peakpedestal:
#        GainHistograms = CreateGainHistograms(files[0],oscilloscope,DDC2)

    for infile in files:

        if DDC2:

#            TotalFiles = ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles,peakpedestal,GainHistograms)
            print "Processing file: ",infile
            TotalFiles = ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles)
###            FitHistograms(infile,Histograms,outdir)

    print "Total files: %f" % int(TotalFiles+1)

else:

    print "DDC2 or oscilloscope data type must be specified."
