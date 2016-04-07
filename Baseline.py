import numpy as np
import os

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def ReadOscilloscopeData(infile,outfile,save_figs,outdir,NumPulseFiles,peakpedestal,GainHistograms):

    rawText = open(infile)
    SingleThresholdPassed = False
    NextValueChecked = False
    IncreasingAmplitudePassed = False
    DoubleThresholdPassed = False
    SecondThresholdPassed = False
    SumThresholdPassed = False
    TotalSumThresholdPassed = False
    DoublePulseThresholdPassed = False
    PreviousYval = 0.0

    xvals = []
    yvals = []
    ysum = 0.0
    
    for line in rawText.readlines():

        splits = line.split(",")
        if len(splits) == 2:
            if splits[0] != 'Time':

                xvals.append(float(splits[0])*1e9)
                yvals.append(float(splits[1])*1e3)
                ysum += float(splits[1])*1e3

                if SingleThresholdPassed and not NextValueChecked:
                    NextValueChecked = True
                    if float(splits[1])*1e3 < PreviousYval:
                        NumPulseFiles["byIncreasingAmplitude"] += 1
                        IncreasingAmplitudePassed = True
                    if float(splits[1])*1e3 < Threshold:
                        NumPulseFiles["byDoubleThreshold"] += 1
                        DoubleThresholdPassed = True
                    if float(splits[1])*1e3 < SecondThreshold:
                        NumPulseFiles["bySecondThreshold"] += 1
                        SecondThresholdPassed = True
                    if float(splits[1])*1e3 + PreviousYval < SumThreshold:
                        NumPulseFiles["bySumThreshold"] +=1
                        SumThresholdPassed = True

                if not SingleThresholdPassed:
                    if float(splits[1])*1e3 < Threshold:
                        NumPulseFiles["bySingleThreshold"] += 1
                        PreviousYval = float(splits[1])*1e3
                        SingleThresholdPassed = True

    if ysum < TotalSumThreshold:
        NumPulseFiles["byTotalAmplitudeSum"] += 1
        TotalSumThresholdPassed = True

    if ysum < DoublePulseThreshold:
        NumPulseFiles["PossibleDoublePulses"] += 1
        DoublePulseThresholdPassed = True

    if peakpedestal:
        GainHistograms[0].Fill(ysum)
        if ysum < TotalSumThreshold:
            GainHistograms[2].Fill(ysum)
        else:
            GainHistograms[1].Fill(ysum)

    Titlesplits = infile.split("/")
    outfile.write("%-*s %-*s %-*s %-*s %-*s %-*s %-*s %-*s\n" % 
                  (11,Titlesplits[-1].split(".txt")[0],
                   11,TotalSumThresholdPassed,
                   11,SingleThresholdPassed,
                   11,IncreasingAmplitudePassed,
                   11,DoubleThresholdPassed,
                   11,SecondThresholdPassed,
                   11,SumThresholdPassed,
                   11,DoubleThresholdPassed))

    if save_figs:

        WaveSignal = ROOT.TGraph(len(xvals))

        i = 0
        for xval, yval in zip(xvals, yvals):
            WaveSignal.SetPoint(i,xval,yval)
            i += 1

        WaveSignal.GetXaxis().SetTitle('Time (ns)')
        WaveSignal.GetYaxis().SetTitle('Amplitude (mV)')
        WaveSignal.GetYaxis().SetRangeUser(-30.0,3.0)
        WaveSignal.SetTitle('%s %s Oscilloscope Waveform from file %s' % (Titlesplits[1], Titlesplits[2], Titlesplits[-2]+"/"+Titlesplits[-1].split(".txt")[0]))

        c2 = ROOT.TCanvas()
        c2.cd()

        WaveSignal.Draw()

        c2.SaveAs(outdir+Titlesplits[-1].split(".txt")[0]+".png")
        
        c2.Close()

###def ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles,peakpedestal,GainHistograms):
def ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles,Histograms):

    rawText = open(infile)

    wavecounter = 0

    xvals = []
    yvals = []
    ysum = 0.0
    baseline = 0.0
    baseline_std = 0.0
    nlines = 0
    bins = 0

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
            # various statistical quantities.

            else:
                baseline = np.average(yvals)
                baseline_std = np.std(yvals)

                area_offset_left  = 5  # number of bins to left of current bin used to find area
                area_offset_right = 15 # number of bins to right of current bin used to find area
                baseline_offset = 100  # use bins between baseline_offset and area_offset_left
                                       #    to left of current bin to calculate running baseline
                cur_baseline = 0
                areas = []
                # Loop over all bins in this waveform, leaving margins on left and right hand sides.
                for i in range(baseline_offset,len(yvals)-area_offset_right):
                    if (i % 20) == 0.0: # Just look at every 20th bin such that each 80ns window is unique
                        cur_baseline = np.average(yvals[i-baseline_offset:i-area_offset_right])
                        Histograms[0].Fill(cur_baseline)
                        yvals_bc = [] # baseline-corrected ADC counts
                        for j in range(i-area_offset_left,i+area_offset_right):
                            yval_baseline_corrected = float(yvals[j]) - float(cur_baseline) # remove baseline
                            yvals_bc.append(yval_baseline_corrected) # baseline-corrected adc counts
                        area = np.sum(yvals_bc)
                        areas.append(area)
                        Histograms[1].Fill(area)


                # make a histogram of the areas and normalize the histogram to 1.0
                # areas_hist[0][0..max] holds the bin contents, areas_hist[1] the bin numbers
                areas_hist = np.histogram(areas,bins=100,range=(-100.,100))
                areas_hist_cum = np.cumsum(areas_hist[0])
                areas_hist_cum_max = np.amax(areas_hist_cum)
                areas_hist_cum = areas_hist_cum/float(areas_hist_cum_max)

                fraction_of_areas_above = 0.99
                
#                index = 0
#                for y in areas_hist_cum:
#                    if y > fraction_of_areas_above:
#                        print "y,index: ",y,index
#                        print "Areas larger than ",areas_hist[1][index]," will only randomly occur ",1.0-fraction_of_areas_above," of the time"
#                        break
#                    index += 1
                        

                yvals = []
                xvals = []

#                print "number of bins, baseline ave and std: ",bins,baseline,baseline_std
                bins = 1

            

    print "Number of lines processed in file: ",infile," = ",nlines

    return 1 # hack to prevent error message at end of processing

def InitializeHistograms(infile,oscilloscope,DDC2):
    
    Histograms = []
    Titlesplits = infile.split("/")
    
    if DDC2:
        BaselinesHistogram = ROOT.TH1D('BaselinesHistogram',
                                       'BH',
                                       100,
                                       4760.0,
                                       4790.0)
        BaselinesHistogram.GetXaxis().SetTitle('Counts')
        BaselinesHistogram.GetYaxis().SetTitle('Entries')
        BaselinesHistogram.SetTitle('Baseline in region preceding pulse window %s %s %s %s' % 
                                    (Titlesplits[-4],Titlesplits[-3],Titlesplits[-2],Titlesplits[-1]))

        AreasHistogram = ROOT.TH1D('AreasHistogram',
                                       'BH',
                                       100,
                                       -100.0,
                                        100.0)
        AreasHistogram.GetXaxis().SetTitle('Counts')
        AreasHistogram.GetYaxis().SetTitle('Entries')
        AreasHistogram.SetTitle('Areas in pulse window (baseline subtracted) %s %s %s %s' % 
                                (Titlesplits[-4],Titlesplits[-3],Titlesplits[-2],Titlesplits[-1]))

        Histograms.append(BaselinesHistogram)
        Histograms.append(AreasHistogram)

    return Histograms

def FitHistograms(infile,Histograms,outdir):

    Titlesplits = infile.split("/")

    c3 = ROOT.TCanvas()
    c3.cd()

    xLow = Histograms[1].GetXaxis().GetXmin()
    xHigh = Histograms[1].GetXaxis().GetXmax()
    Mean = Histograms[1].GetBinCenter(Histograms[1].GetMaximumBin())
    Sigma = Histograms[1].GetStdDev()

    print "xLow,xHigh,Mean,Sigma",xLow,xHigh,Mean,Sigma

    x        = ROOT.RooRealVar("Areas","Areas",xLow,xHigh)
    mean     = ROOT.RooRealVar("Areas mean","mean of Areas",Mean,Mean-0.1*abs(Mean),Mean+0.1*abs(Mean))
    sigma    = ROOT.RooRealVar("Areas sigma","sigma of Areas",0.7*Sigma,0.8*Sigma,0.9*Sigma)
    gaussian = ROOT.RooGaussian("gauss","Gaussian PDF",x,mean,sigma)

    xList = ROOT.RooArgList(x)
#    print "xList: ",xList
    histogram = ROOT.RooDataHist("Area data","Area data histogram",xList,Histograms[1])
#    histogram = ROOT.RooDataHist("Area data","Area data histogram",x,Histograms[1])

    gaussian.fitTo(histogram)

    frame = x.frame()
    frame.GetXaxis().SetTitle(Histograms[1].GetXaxis().GetTitle())
    frame.GetYaxis().SetTitle(Histograms[1].GetYaxis().GetTitle())

    histogram.plotOn(frame)
    gaussian.plotOn(frame)

    frame.SetTitle('Gaussian fit to Areas in sliding pulse window %s %s %s %s' % 
                   (Titlesplits[-4],Titlesplits[-3],Titlesplits[-2],Titlesplits[-1]))


    frame.Draw()

    c3.SaveAs(outdir+"/AreasWithGaussianFit.png")

    c3.Close()


def SaveHistograms(Histograms,outdir):

    c2 =  ROOT.TCanvas()
    c2.cd()
    Histograms[0].Draw()
    c2.SaveAs(outdir+"/Baselines.png")
    Histograms[1].Draw()
    c2.SaveAs(outdir+"/Areas.png")
    c2.Close()

    RootFile = ROOT.TFile("Baseline.root","recreate")
    Histograms[0].Write()
    Histograms[1].Write()
#    RootFile.Write()
    RootFile.Close()


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

if save_figs or peakpedestal:
    print "Importing ROOT..."
    import ROOT
    ROOT.gROOT.SetBatch(True)
    print "Loading libRooFit..."
    ROOT.gSystem.Load("libRooFit")

#DoIt = False
#if DDC2:
#    if ymax is not None:
#        DoIt = True
#    else:
#        print "If you want to analyse DDC2 data you need to provide the number of counts in a single pulse window."
#        
#if oscilloscope:
#    DoIt = True
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

    Histograms = InitializeHistograms(files[0],oscilloscope,DDC2)

    for infile in files:

        if oscilloscope:

            ReadOscilloscopeData(infile,outfile,save_figs,outdir,NumPulseFiles,peakpedestal,GainHistograms)
            TotalFiles = int(len(files))

        if DDC2:

#            TotalFiles = ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles,peakpedestal,GainHistograms)
            print "Processing file: ",infile
            TotalFiles = ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles,Histograms)
###            FitHistograms(infile,Histograms,outdir)
            SaveHistograms(Histograms,outdir)

    print "Total files: %f" % int(TotalFiles+1)
#    print "Number with identified pulse (by threshold on amplitude): %f" % int(NumPulseFiles["bySingleThreshold"])
#    print "Number with identified pulse (by increasing amplitude after threshold): %f" % int(NumPulseFiles["byIncreasingAmplitude"])
#    print "Number with identified pulse (by exceeding threshold twice): %f" % int(NumPulseFiles["byDoubleThreshold"])
#    print "Number with identified pulse (by exceeding second higher threshold): %f" % int(NumPulseFiles["bySecondThreshold"])
#    print "Number with identified pulse (by exceeding threshold on sum of first two bins of supposed pulse): %f" % int(NumPulseFiles["bySumThreshold"])
#    print "Number with identified pulse (by sum on total amplitude): %f" % int(NumPulseFiles["byTotalAmplitudeSum"])
#    print "Number with identified double pulse (by sum on total amplitude): %f" %int(NumPulseFiles["PossibleDoublePulses"])
#    print "\n"
#    print "Threshold - %f" % float(Threshold)
#    print "SecondThreshold - %f" % float(SecondThreshold)
#    print "SumThreshold - %f" % float(SumThreshold)
#    print "TotalSumThreshold - %f" % float(TotalSumThreshold)
#    print "DoublePulseThreshold - %f" % float(DoublePulseThreshold)

else:

    print "DDC2 or oscilloscope data type must be specified."
