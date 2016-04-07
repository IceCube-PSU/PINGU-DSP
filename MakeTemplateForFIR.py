import numpy as np
import os
import matplotlib.pyplot as plt
import pickle

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles):

    rawText = open(infile)

    xvals = []
    xvalskeep = []
    yvals = []
    yvals_B = []
    AllYvals = []
    nlines = 0
    bins = 0
    NWaveforms = 0
    Baseline = 0.0

    for index in range(0,255):
        AllYvals.append(0)
    
            
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
                bins += 1

            # we're finished with the current waveform and can calculate
            # the area and peak pulseheight under the putative pulse
            else:

                if len(xvals) == 255: # skip cases with too few digitizations
                    xvalskeep = xvals
                    
                    Baseline = np.average(yvals[0:100]) # Use first 100 samples to calculate baseline
                    yvals_B = yvals - Baseline

                    PulsePresent = False
                    for i in range(0,255):
                        if yvals_B[i] > 10: PulsePresent = True
                                                                             
                    if PulsePresent:
                        NWaveforms += 1
                        for j in range(0,255):
                            AllYvals[j] += yvals_B[j] # sum up all ADC vals, bin by bin
                    
#                    Baseline = np.average(yvals[0:100]) # Use first 100 samples to calculate baseline
#                    


                yvals = []
                xvals = []
                
        if NWaveforms >= 1000: break

    print "NWaveforms: ",NWaveforms                    
                                                            
    for index in range(0,255):
        AllYvals[index] = AllYvals[index]/float(NWaveforms) # get average waveform
    
    plt.ylim(-10.,40.)
    plt.ylabel('Counts')
    plt.xlabel('time (ns)')
    plt.plot(xvalskeep,AllYvals,'b')
    plt.show()
                    
    # Average waveform has some oscillation in it--try to remove via FFT analysis
    
    StdFFT = np.fft.fft(AllYvals)
    FFTLen = len(StdFFT)
#    StdFrequenciesFFT = np.fft.fftfreq(FFTLen)
    StdFrequencies = np.fft.fftfreq(FFTLen,4.e-9)/1.e6 # units are MHz
    StdPowerSpectrum = np.abs(StdFFT)**2

    plt.xlim(-10.,140.)
    plt.ylim(1.0e-2,1.0e8)
    plt.ylabel('Std Power Spectrum')
    plt.xlabel('Frequency (MHz)')
    plt.semilogy(StdFrequencies[0:FFTLen/2+1],StdPowerSpectrum[0:FFTLen/2+1],'r')

    plt.show()
    
    # Remove frequencies around 62.5MHz (1/4 of 250MHz ADC sampling rate), etc
    
    MinFreq1 = 60.0
    MaxFreq1 = 65.0
    MinFreq2 = 99.0
    MaxFreq2 = 103.0
    MaxFreq3 = 110.0
    
    StdFFT_LowPass = StdFFT.copy()
    for Freq in StdFrequencies:
        if ((Freq>MinFreq1 and Freq<MaxFreq1) or (Freq<-MinFreq1 and Freq>-MaxFreq1)):
            StdFFT_LowPass[Freq] = 0.0
        if ((Freq>MinFreq2 and Freq<MaxFreq2) or (Freq<-MinFreq2 and Freq>-MaxFreq2)):
            StdFFT_LowPass[Freq] = 0.0
        if (Freq>MaxFreq3):
            StdFFT_LowPass[Freq] = 0.0
      
          
#    StdFFT_LowPass[(StdFrequencies>MinFreq) and (StdFrequencies<MaxFreq)] = 0.0     # remove notch around 62.5
#    StdFFT_LowPass[(StdFrequencies<-MinFreq) and (StdFrequencies>-MaxFreq)] = 0.0     # remove high negative frequencies, too
    StdPowerSpectrum_LowPass = np.abs(StdFFT_LowPass)**2
                                            
    AllYvals_LowPass = np.fft.ifft(StdFFT_LowPass)
    
    # There are 256 samples, 4ns per sample.  The pulse(s) are between about 620ns and 670ns.
    # Use 12 samples = 48ns in between those two times to represent the template pulse.
    
    Yvals_Template_realonly = []
    index = 0
    for time in xvalskeep:
        if (time > 620. and time < 670.):
#            print time
            Yvals_Template_realonly.append(np.real(AllYvals_LowPass[index]))
        index += 1

    template_file = open("/Users/cowen/Dropbox/SingleChannelDAQ/template.dat","w")
    pickle.dump(Yvals_Template_realonly,template_file) #use Yvals... = pickle.load(template_file)
    template_file.close()
    
#    print Yvals_Template
#    print np.real(Yvals_Template)
#    print np.abs(Yvals_Template)
#    print np.abs(Yvals_Template) - np.real(Yvals_Template) # Values are small.  Complex part of Yvals_Template is small.
    
    
    
    plt.ylim(-10.,40.)
    plt.ylabel('LowPass Counts')
    plt.xlabel('time (ns)')
    plt.plot(xvalskeep,AllYvals_LowPass,'b')
    plt.show()

    plt.ylim(-10.,40.)
    plt.ylabel('delta Counts')
    plt.xlabel('time (ns)')
    plt.plot(xvalskeep,AllYvals-AllYvals_LowPass,'b')
    plt.show()

    plt.ylim(-10.,40.)
    plt.xlim(600.,700.)
    plt.ylabel('LowPass Counts')
    plt.xlabel('time (ns)')
    plt.plot(xvalskeep,AllYvals_LowPass,'b')
    plt.show()
    
    plt.ylim(-10.,40.)
    plt.xlim(600.,700.)
    plt.ylabel('Counts')
    plt.xlabel('time (ns)')
    plt.plot(xvalskeep,AllYvals,'b')
    plt.show()
    


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
