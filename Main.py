import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import pickle

from DSP.GetWF import GetWaveform
from DSP.CreateTemplateWF import CreateTemplateWaveform
from DSP.CleanWF import CleanWaveform
from DSP.AddNoise import AddNoise
from DSP.PlotWF import PlotWaveform

#reload(GetWaveform)
#reload(CreateTemplateWF)
#reload(CleanWaveform)
#reload(AddNoise)
#reload(PlotWaveform)
 
# Won't normally need this--plotting function will 
# assume x-values if not provided explicitly
xvals = range(0,1020,4)

# Make a template waveform.  
#    First, get average waveform.

GetWFs = GetWaveform("/Users/cowen/Desktop/PennStateMeasurements/150606-150610/1230VGain1e7/DDC2Data/PMTWaveforms/Run1/data_0.txt")
WF = GetWFs.NewWaveform()
CleanWF = CleanWaveform()
ManyWFs = CreateTemplateWaveform(GetWFs,CleanWF)
AverageWF = ManyWFs.FindAverage(20)

#xRange = [0,256]
xRange = [150,180]
xLabel = 'time (4 ns bins)'
yRange = [-20,40]
yLabel = 'Count'
color = 'b'
PlotFileBasename = 'AverageWaveform'
PlotWFs = PlotWaveform(PlotFileBasename)
PlotWFs.Linear(AverageWF,plt,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot

#sys.exit()

# Clean average waveform using FFT
ExcludedFreqs = [(0.,0.),(60.,65.),(99.,103.),(110.,1000.)]
RemoveBaseline = True

TemplateWF = CleanWaveform()
FFTTemplateWF = TemplateWF.BandFilterFFT(AverageWF,ExcludedFreqs,RemoveBaseline)
FIRTemplate = FFTTemplateWF[156:169]

xRange = [150,180]
PlotFileBasename = 'TemplateWaveform'
PlotTemplateClean = PlotWaveform(PlotFileBasename)
PlotTemplateClean.Linear(FFTTemplateWF,plt,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot
          
# IIR
Tau = 20.0e-9
T = 4.0e-9

# FIR
# Get template waveform
#TemplateFile = open("/Users/cowen/Dropbox/SingleChannelDAQ/template.dat","r")
#TemplateWaveform = pickle.load(TemplateFile)
#TemplateFile.close()


# Definitions for plotter
PlotFileBasename = 'IIR_Waveform'
# Instantiate new plot maker
PlotWF = PlotWaveform(PlotFileBasename)
# Instantiate a new waveform getter
GetWFs = GetWaveform("test.dat")
for i in range(0,3):

    # Get a new waveform
    WF = GetWFs.NewWaveform()

    # Instantiate new waveform cleaner
    CleanWF = CleanWaveform()
    # Subtract baseline
    BaselineSubtractedWF = CleanWF.SubtractBaseline(WF,1,100)
    
    # run FFT
    # FFTCleanedWF = y.BandFilterFFT(ExcludedFreqs,RemoveBaseline)
    # run IIR   
    IIRCleanedWF = CleanWF.FilterIIR(BaselineSubtractedWF,Tau,T)

    # define plot params
    xRange = [0,256]
    xLabel = 'time (4 ns)'
    yRange = [-50,50]
    yLabel = 'Count'
    color = 'b'
#        PlotWF.Linear(IIRCleanedWF,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot

# Inject some noise into the waveform

    WF = AddNoise(BaselineSubtractedWF)
    BipolarSpikeWF = WF.BipolarSpike(50.,70.)
    CleanWF = CleanWaveform()
    IIRCleanedBipolarSpikeWF = CleanWF.FilterIIR(BipolarSpikeWF,Tau,T) 
    yLabel = 'Count w/spike-'+str(i)
    PlotWF.Linear(BipolarSpikeWF,plt,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot
    yLabel = 'Count w/spike (IIR cleaned)-'+str(i)
    PlotWF.Linear(IIRCleanedBipolarSpikeWF,plt,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot

    
    xRange = [0,256]
    xLabel = 'time (ns)'
    yRange = [-10,40]
    yLabel = 'Counts (FIR)'
    color = 'b'
    PlotFilename = "WaveformFIRCLeaned.pdf"
        
#    z = PlotWaveform(FFTCleanedWF,xvals,PlotFilename)
#    z.Linear(xRange,xLabel,yRange,yLabel,color) # make a linear plot
        
        
#    xRange = [0,256]
#    xLabel = 'time (ns)'
#    yRange = [-10,40]
#    yLabel = 'Counts (FFT)'
#    color = 'b'
#    PlotFilename = "WaveformFFTCLeaned.pdf"
   
#    z = PlotWaveform(FFTCleanedWF,xvals,PlotFilename)
#    z.Linear(xRange,xLabel,yRange,yLabel,color) # make a linear plot
    
#    xRange = [0,256]
#    xLabel = 'time (4ns)'
#    yRange = [-10,40]
#    yLabel = 'Counts (IIR)'
#    color = 'b'
#    PlotFilename = "WaveformIIRCLeaned.pdf"
        
#    z = PlotWaveform(IIRCleanedWF,xvals,PlotFilename)
#    z.Linear(xRange,xLabel,yRange,yLabel,color) # make a linear plot
    
