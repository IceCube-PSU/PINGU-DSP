import numpy as np
import os
import matplotlib.pyplot as plt
import pickle

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles):

    rawText = open(infile)
    # Load in template waveform.
    template_file = open("/Users/cowen/Dropbox/SingleChannelDAQ/template.dat","r")
    Template_Waveform = pickle.load(template_file)
    template_file.close()

    xvals = []
    xvalskeep = []
    yvals = []
    yvals_B = []
    AllYvals = []
    yvals_conv_valid = []
    yvals_conv_full = []
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
                    NWaveforms += 1
                    
                    Baseline = np.average(yvals[0:100]) # Use first 100 samples to calculate baseline
                    yvals_B = yvals - Baseline

                # FIR: Perform convolution of yvals_B with time-reversed template
                # First, normalize template area to 1.0 so that the convolution has
                # the same amplitude as the input waveform.
                                
                Template_sum = sum(Template_Waveform)
                
                yvals_conv_full = np.convolve(yvals_B,Template_Waveform/Template_sum,mode='full') # full convolution, including past signal boundaries
                yvals_conv_valid = np.convolve(yvals_B,Template_Waveform/Template_sum,mode='valid') # only convolve where template does not go past signal boundaries
                
                # Then, plot each resulting waveform--before and after FIR

                plt.ylim(-10.,40.)
                plt.ylabel('Counts')
                plt.xlabel('time (ns)')
                plt.plot(xvalskeep,yvals_B,'b')
                plt.show()
                xvals = range(0,len(yvals_conv_full)*4,4)
#                print len(xvals),len(yvals_conv_full),len(yvals_conv_valid)
                plt.ylim(-10.,40.)
                plt.ylabel('Counts (conv full)')
                plt.plot(xvals,yvals_conv_full,'b')
                plt.show()


                yvals = []
                xvals = []
                
        if NWaveforms >= 30: break

    print "NWaveforms: ",NWaveforms                    
                                                            


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
