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

def ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles,peakpedestal,GainHistograms):

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

    count = 0
    wavecounter = 0

    xvals = []
    yvals = []
    ysum = 0.0

    for line in rawText.readlines():

        splits = line.split(",")
        if len(splits) == 6:
            if float(splits[0]) == count:
                xvals.append(float(splits[0])*4) 
                #Multiply by 4 since one sample is 4 nanoseconds
                yvals.append(float(splits[1]))
                count += 1

                if SingleThresholdPassed and not NextValueChecked:
                    NextValueChecked = True
                    if float(splits[1]) > PreviousYval:
                        NumPulseFiles["byIncreasingAmplitude"] += 1
                        IncreasingAmplitudePassed = True
                    if float(splits[1]) > Threshold:
                        NumPulseFiles["byDoubleThreshold"] += 1
                        DoubleThresholdPassed = True
                    if float(splits[1]) > SecondThreshold:
                        NumPulseFiles["bySecondThreshold"] += 1
                        SecondThresholdPassed = True
                    if float(splits[1]) + PreviousYval > SumThreshold:
                        NumPulseFiles["bySumThreshold"] +=1
                        SumThresholdPassed = True

                if not SingleThresholdPassed:
                    if float(splits[1]) > Threshold:
                        NumPulseFiles["bySingleThreshold"] += 1
                        PreviousYval = float(splits[1])
                        SingleThresholdPassed = True

            if len(yvals) == ymax:

                topcount = yvals.index(max(yvals))

                if (topcount+20) > ymax-1:
                    for val in range(215, 255):
                        ysum += yvals[val]
                elif (topcount-20) < 0:
                    for val in range(0, 40):
                        ysum += yvals[val]
                else:
                    for val in range(topcount - 20, topcount + 20):
                        ysum += yvals[val]

                if ysum > TotalSumThreshold:
                    NumPulseFiles["byTotalAmplitudeSum"] += 1
                    TotalSumThresholdPassed = True

                if ysum > DoublePulseThreshold:
                    NumPulseFiles["PossibleDoublePulses"] += 1
                    DoublePulseThresholdPassed = True

                if peakpedestal:
                    GainHistograms[0].Fill(ysum)
                    if ysum > TotalSumThreshold:
                        GainHistograms[2].Fill(ysum)
                    else:
                        GainHistograms[1].Fill(ysum)


                wavecounter += 1
                Titlesplits = infile.split("/")
                outfile.write("%-*s %-*s %-*s %-*s %-*s %-*s %-*s %-*s\n" % 
                              (11,Titlesplits[-1].split(".txt")[0]+"wave%05i"%wavecounter,
                               11,TotalSumThresholdPassed,
                               11,SingleThresholdPassed,
                               11,IncreasingAmplitudePassed,
                               11,DoubleThresholdPassed,
                               11,SecondThresholdPassed,
                               11,SumThresholdPassed,
                               11,DoublePulseThresholdPassed))

                if save_figs:

                    WaveSignal = ROOT.TGraph(len(xvals))
                    i = 0
                    for xval, yval in zip(xvals, yvals):
                        WaveSignal.SetPoint(i,xval,yval)
                        i += 1

                    WaveSignal.GetXaxis().SetTitle('Time (ns)')
###                    WaveSignal.GetXaxis().SetRangeUser(500,800)
                    WaveSignal.GetXaxis().SetRangeUser(200,900)
                    WaveSignal.GetYaxis().SetTitle('Amplitude (ADC Counts)')
                    WaveSignal.GetYaxis().SetRangeUser(4750,4850)
                    Titlesplits = infile.split("/")
                    WaveSignal.SetTitle('%s %s DDC2 Waveform from file %s wave %s' % (Titlesplits[1], Titlesplits[2], Titlesplits[-2]+"/"+Titlesplits[-1].split(".txt")[0],str(wavecounter)))
            
                    c2 = ROOT.TCanvas()
                    c2.cd()

                    WaveSignal.Draw()

                    Filesplits = infile.split(Titlesplits[-2])
                    c2.SaveAs(outdir+Titlesplits[-1].split(".txt")[0]+"wave%05i.png"%wavecounter)

                    c2.Close()

                xvals = []
                yvals = []
                ysum = 0.0
                count = 0
                topcount = 0
                SingleThresholdPassed = False
                NextValueChecked = False
                IncreasingAmplitudePassed = False
                DoubleThresholdPassed = False
                SecondThresholdPassed = False
                SumThresholdPassed = False
                TotalSumThresholdPassed = False
                DoublePulseThresholdPassed = False
                PreviousYval = 0.0

    return wavecounter

def CreateGainHistograms(infile,oscilloscope,DDC2):
    
    GainHistograms = []
    Titlesplits = infile.split("/")
    
    if oscilloscope:
        TotalGainHistogram = ROOT.TH1D('TotalGainHistogram',
                                       'TGH',
                                       101,
                                       -1500.0,
                                       500.0)
        TotalGainHistogram.GetXaxis().SetTitle('Summed Amplitude (mV)')
        TotalGainHistogram.GetYaxis().SetTitle('Counts per 20 mV')
        TotalGainHistogram.SetTitle('Histogram of Summed Amplitudes for Oscilloscope Data %s %s' % (Titlesplits[-2],Titlesplits[1]))
        PedestalHistogram = ROOT.TH1D('PedestalHistogram',
                                      'PedH',
                                      71,
                                      -400.0,
                                      300.0)
        PedestalHistogram.GetXaxis().SetTitle('Summed Amplitude (mV)')
        PedestalHistogram.GetYaxis().SetTitle('Counts per 20 mV')
        PedestalHistogram.SetTitle('Histogram of Summed Amplitudes for Oscilloscope Data %s %s focusing on Pedestal' % (Titlesplits[-2],Titlesplits[1]))
        PeakHistogram = ROOT.TH1D('PeakHistogram',
                                  'PeakH',
                                  22,
                                  -7000.0,
                                  -300.0)
        PeakHistogram.GetXaxis().SetTitle('Summed Amplitude (mV)')
        PeakHistogram.GetYaxis().SetTitle('Counts per 20 mV')
        PeakHistogram.SetTitle('Histogram of Summed Amplitudes for Oscilloscope Data %s %s focusing on Peak' % (Titlesplits[-2],Titlesplits[1]))
        GainHistograms.append(TotalGainHistogram)
        GainHistograms.append(PedestalHistogram)
        GainHistograms.append(PeakHistogram)

    if DDC2:
        TotalGainHistogram = ROOT.TH1D('TotalGainHistogram',
                                       'TGH',
                                       51,
                                       191000.0,
                                       192000.0)
        TotalGainHistogram.GetXaxis().SetTitle('Summed Amplitude in Time Window Around Peak (ADC Counts)')
        TotalGainHistogram.GetYaxis().SetTitle('Counts per 20 ADC Counts')
        TotalGainHistogram.SetTitle('Histogram of Summed Amplitudes for DDC2 Data %s %s' % (Titlesplits[-2],Titlesplits[1]))
        PedestalHistogram = ROOT.TH1D('PedestalHistogram',
                                      'PedH',
                                      26,
                                      191000.0,
                                      191300.0)
        PedestalHistogram.GetXaxis().SetTitle('Summed Amplitude in Time Window Around Peak (ADC Counts)')
        PedestalHistogram.GetYaxis().SetTitle('Counts per 12 ADC Counts')
        PedestalHistogram.SetTitle('Histogram of Summed Amplitudes for DDC2 Data %s %s focusing on Pedestal' % (Titlesplits[-2],Titlesplits[1]))
        PeakHistogram = ROOT.TH1D('PeakHistogram',
                                  'PeakH',
                                  26,
                                  191300.0,
                                  192300.0)
        PeakHistogram.GetXaxis().SetTitle('Summed Amplitude in Time Window Around Peak (ADC Counts)')
        PeakHistogram.GetYaxis().SetTitle('Counts per 40 ADC Counts')
        PeakHistogram.SetTitle('Histogram of Summed Amplitudes for DDC2 Data %s %s focusing on Peak' % (Titlesplits[-2],Titlesplits[1]))
        GainHistograms.append(TotalGainHistogram)
        GainHistograms.append(PedestalHistogram)
        GainHistograms.append(PeakHistogram)

    return GainHistograms

def SaveGainHistograms(GainHistograms,outdir):

    c2 =  ROOT.TCanvas()
    c2.cd()
    GainHistograms[0].Draw()
    c2.SaveAs(outdir+"PeakPedestal/SummedAmplitudeHist.png")
    GainHistograms[1].Draw()
    c2.SaveAs(outdir+"PeakPedestal/SummedAmplitudePedestalHist.png")
    GainHistograms[2].Draw()
    c2.SaveAs(outdir+"PeakPedestal/SummedAmplitudePeakHist.png")
    c2.Close()

def CBFitGainHistogram(infile,GainHistogram,outdir,oscilloscope,DDC2):

    Titlesplits = infile.split("/")

    c3 = ROOT.TCanvas()
    c3.cd()

    xLow = GainHistogram.GetXaxis().GetXmin()
    xHigh = GainHistogram.GetXaxis().GetXmax()
    Mean = GainHistogram.GetBinCenter(GainHistogram.GetMaximumBin())
    Sigma = GainHistogram.GetStdDev()

    SA = ROOT.RooRealVar("SA","Summed Amplitude",xLow,xHigh)
    SAmean = ROOT.RooRealVar("SAMean","Summed Amplitude Mean",Mean,0.9*Mean,1.1*Mean)
    SAsigma = ROOT.RooRealVar("SASigma","Summed Amplitude Sigma",0.5*Sigma,0.4*Sigma,0.6*Sigma)
    SAa = ROOT.RooRealVar("SAa","Summed Amplitude a parameter",-0.5,-0.7,-0.1)
    SAn = ROOT.RooRealVar("SAn","Summed Amplitude n parameter",120,120,200)
    SACB = ROOT.RooCBShape("CBFit","CBFit",SA,SAmean,SAsigma,SAa,SAn)

    SAList = ROOT.RooArgList(SA)
    SAHist = ROOT.RooDataHist("SAData","SADatahist",SAList,GainHistogram)

    SACB.fitTo(SAHist)
    SAframe = SA.frame()
    SAframe.GetXaxis().SetTitle(GainHistogram.GetXaxis().GetTitle())
    SAframe.GetYaxis().SetTitle(GainHistogram.GetYaxis().GetTitle())
    
    SAHist.plotOn(SAframe)
    SACB.plotOn(SAframe)

    if oscilloscope:
        SAframe.SetTitle('Histogram of Summed Amplitudes for Oscilloscope Data %s %s with RooCrystalBall Fit' % (Titlesplits[-2],Titlesplits[1]))
    if DDC2:
        SAframe.SetTitle('Histogram of Summed Amplitudes for DDC2 Data %s %s with RooCrystalBall Fit' % (Titlesplits[-2],Titlesplits[1]))

    SAframe.Draw()
    c3.SaveAs(outdir+"PeakPedestal/SummedAmplitudePedestalHistwCrystalBallFit.png")

def NovoFitGainHistogram(infile,GainHistogram,outdir,oscilloscope,DDC2):

    Titlesplits = infile.split("/")

    c3 = ROOT.TCanvas()
    c3.cd()

    xLow = GainHistogram.GetXaxis().GetXmin()
    xHigh = GainHistogram.GetXaxis().GetXmax()
    Mean = GainHistogram.GetBinCenter(GainHistogram.GetMaximumBin())
    Sigma = GainHistogram.GetStdDev()

    SA = ROOT.RooRealVar("SA","Summed Amplitude",xLow,xHigh)
    SAmean = ROOT.RooRealVar("SAMean","Summed Amplitude Mean",Mean,1.1*Mean,0.9*Mean)
    SAsigma = ROOT.RooRealVar("SASigma","Summed Amplitude Sigma",0.6*Sigma,0.5*Sigma,0.7*Sigma)
    SAtail = ROOT.RooRealVar("SAtail","Summed Amplitude tail parameter",-0.1,-0.2,-0.05)
    SANovo = ROOT.RooNovosibirsk("NovoFit","NovoFit",SA,SAmean,SAsigma,SAtail)

    SAList = ROOT.RooArgList(SA)
    SAHist = ROOT.RooDataHist("SAData","SADatahist",SAList,GainHistogram)

    SANovo.fitTo(SAHist)
    SAframe = SA.frame()
    SAframe.GetXaxis().SetTitle(GainHistogram.GetXaxis().GetTitle())
    SAframe.GetYaxis().SetTitle(GainHistogram.GetYaxis().GetTitle())
    
    SAHist.plotOn(SAframe)
    SANovo.plotOn(SAframe)

    if oscilloscope:
        SAframe.SetTitle('Histogram of Summed Amplitudes for Oscilloscope Data %s %s with RooNovosibirsk Fit' % (Titlesplits[-2],Titlesplits[1]))
    if DDC2:
        SAframe.SetTitle('Histogram of Summed Amplitudes for DDC2 Data %s %s with RooNovosibirsk Fit' % (Titlesplits[-2],Titlesplits[1]))

    SAframe.Draw()
    c3.SaveAs(outdir+"PeakPedestal/SummedAmplitudePedestalHistwNovosibirskFit.png")

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
    #ROOT.gSystem.Load("libRooFit")

DoIt = False
if DDC2:
    if ymax is not None:
        DoIt = True
    else:
        print "If you want to analyse DDC2 data you need to provide the number of counts in a single pulse window."
        
if oscilloscope:
    DoIt = True

if DoIt:

    if outdir == 'CWD':
        outdir = os.getcwd()
        outdir = outdir + "/"

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

    if peakpedestal:
        GainHistograms = CreateGainHistograms(files[0],oscilloscope,DDC2)

    for infile in files:

        if oscilloscope:

            ReadOscilloscopeData(infile,outfile,save_figs,outdir,NumPulseFiles,peakpedestal,GainHistograms)
            TotalFiles = int(len(files))

        if DDC2:

            TotalFiles = ReadDDC2Data(infile,outfile,save_figs,outdir,ymax,NumPulseFiles,peakpedestal,GainHistograms)

    if peakpedestal:
        SaveGainHistograms(GainHistograms,outdir)
        #CBFitGainHistogram(files[0],GainHistograms[1],outdir,oscilloscope,DDC2)
        NovoFitGainHistogram(files[0],GainHistograms[1],outdir,oscilloscope,DDC2)

    print "Total files: %f" % int(TotalFiles+1)
    print "Number with identified pulse (by threshold on amplitude): %f" % int(NumPulseFiles["bySingleThreshold"])
    print "Number with identified pulse (by increasing amplitude after threshold): %f" % int(NumPulseFiles["byIncreasingAmplitude"])
    print "Number with identified pulse (by exceeding threshold twice): %f" % int(NumPulseFiles["byDoubleThreshold"])
    print "Number with identified pulse (by exceeding second higher threshold): %f" % int(NumPulseFiles["bySecondThreshold"])
    print "Number with identified pulse (by exceeding threshold on sum of first two bins of supposed pulse): %f" % int(NumPulseFiles["bySumThreshold"])
    print "Number with identified pulse (by sum on total amplitude): %f" % int(NumPulseFiles["byTotalAmplitudeSum"])
    print "Number with identified double pulse (by sum on total amplitude): %f" %int(NumPulseFiles["PossibleDoublePulses"])
    print "\n"
    print "Threshold - %f" % float(Threshold)
    print "SecondThreshold - %f" % float(SecondThreshold)
    print "SumThreshold - %f" % float(SumThreshold)
    print "TotalSumThreshold - %f" % float(TotalSumThreshold)
    print "DoublePulseThreshold - %f" % float(DoublePulseThreshold)

else:

    print "DDC2 or oscilloscope data type must be specified."
