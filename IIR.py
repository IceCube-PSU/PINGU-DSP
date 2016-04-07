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
    NWaveforms = 0
    areas = []
    yIIT = []
    Areas = []
    Areas8 = []
    Areas12 = []
    Areas16 = [] # Check that area is preserved after application of IIR
    Period = T = 4.0e-9 # sampling period
    tau = 10.0e-9 # filter time constant default value

    for line in rawText.readlines():
        
        nlines += 1

        splits = line.split(",")
        if len(splits) == 6:
            adcbin = int(splits[0])
            adcval = float(splits[1])
            newWaveform = int(splits[4]) # Waveform ends when last number in row==1
            if not newWaveform:
                xvals.append(float(adcbin)*4) # Multiply by 4 since one sample is 4 nanoseconds
                yvals.append(adcval)
                yIIT.append(0.0)
                bins += 1

            # we're finished with the current waveform and can calculate
            # the area and peak pulseheight under the putative pulse
            else:

                if len(xvals) > 200: # skip cases with too few digitizations
                     
                    NWaveforms += 1
                     
                    plt.subplot2grid((4,1), (0, 0), colspan=1)
                    plt.ylim(4760.,4840.)
                    plt.ylabel('Counts')
                    plt.xlabel('time (ns)')
                    plt.plot(xvals,yvals,'b')
 
                    Baseline = np.average(yvals[0:100]) # Use first 100 samples to calculate baseline
                    yvals_B = yvals - Baseline

                    thisArea = sum(yvals_B[150:200])
                    if thisArea > 50: Areas.append(thisArea)

                    # Filter definition: x = input, y = output, t = time, T = sampling period, tau = filter time constant
                    #    y[0] = x[0]*T/tau
                    #    y[t] = exp[-T/tau]*y[t-T] + x[t]*T/tau                   
                                                         
                    tau = 8.0e-9
                    yIIT[0] = yvals_B[0]*T/tau
                    for TimeBin in range(1,len(xvals)-1):
                        yIIT[TimeBin] = np.exp(-T/tau)*yIIT[TimeBin - 1] + yvals_B[TimeBin]*T/tau
                    
                    thisArea = sum(yIIT[150:200])
                    if thisArea > 50: Areas8.append(thisArea)

                                         
                    plt.subplot2grid((4,1), (1, 0), colspan=1)
                    plt.ylim(-20.,40.)
                    plt.ylabel('tau=8ns')
                    plt.xlabel('time (ns)')
                    plt.plot(xvals,yIIT,'b')

                    tau = 12.0e-9
                    yIIT[0] = yvals_B[0]*T/tau
                    for TimeBin in range(1,len(xvals)-1):
                        yIIT[TimeBin] = np.exp(-T/tau)*yIIT[TimeBin - 1] + yvals_B[TimeBin]*T/tau
                          
                    thisArea = sum(yIIT[150:200])
                    if thisArea > 50: Areas12.append(thisArea)
                                   
                    plt.subplot2grid((4,1), (2, 0), colspan=1)
                    plt.ylim(-20.,40.)
                    plt.ylabel('tau=12ns')
                    plt.xlabel('time (ns)')
                    plt.plot(xvals,yIIT,'b')

                    tau = 16.0e-9
                    yIIT[0] = yvals_B[0]*T/tau
                    for TimeBin in range(1,len(xvals)-1):
                        yIIT[TimeBin] = np.exp(-T/tau)*yIIT[TimeBin - 1] + yvals_B[TimeBin]*T/tau

                    thisArea = sum(yIIT[150:200])
                    if thisArea > 50: Areas16.append(thisArea)
                                                             
                    plt.subplot2grid((4,1), (3, 0), colspan=1)
                    plt.ylim(-20.,40.)
                    plt.ylabel('tau=16ns')
                    plt.xlabel('time (ns)')
                    plt.plot(xvals,yIIT,'b')
                     
                    
#                    plt.tight_layout()

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
                                                            
###                    plt.show()
                    
#                    Areas_hist = np.histogram(Areas,bins=100,range=(-100.,100))
#                    Areas8_hist = np.histogram(Areas8,bins=100,range=(-100.,100))
#                    Areas12_hist = np.histogram(Areas12,bins=100,range=(-100.,100))
#                    Areas16_hist = np.histogram(Areas16,bins=100,range=(-100.,100))

                    yvals = []
                    xvals = []
                    yIIT = []
                    
                    bins = 1
                    

    hist, bins = np.histogram(Areas, bins=50)
    hist8, bins = np.histogram(Areas8, bins=50)
    hist12, bins = np.histogram(Areas12, bins=50)
    hist16, bins = np.histogram(Areas16, bins=50)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2

    plt.subplot2grid((2,2), (0, 0), colspan=1)
    plt.bar(center, hist, align='center', width=width)
    plt.subplot2grid((2,2), (1, 0), colspan=1)
    plt.bar(center, hist8, align='center', width=width)
    plt.subplot2grid((2,2), (0, 1), colspan=1)
    plt.bar(center, hist12, align='center', width=width)
    plt.subplot2grid((2,2), (1, 1), colspan=1)
    plt.bar(center, hist16, align='center', width=width)
    
    plt.show()

    print "Number of lines processed in file: ",infile," = ",nlines
    print "Number of waveforms processed in file: ",infile," = ",NWaveforms
#    print Areas
#    print Areas8
#    print Areas12
#    print Areas16

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
