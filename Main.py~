
import pickle

from Classes.GetWaveform import GetWaveform
from Classes.CreateTemplateWaveform import CreateTemplateWaveform
from Classes.CleanWaveform import CleanWaveform
from Classes.AddNoise import AddNoise
from Classes.PlotWaveform import PlotWaveform

# Won't normally need this--plotting function will 
# assume x-values if not provided explicitly
xvals = range(0,1020,4)

# Make a template waveform.  First, get average waveform.
    
xx = CreateTemplateWaveform("/Users/steven/IceCube/HardwareWork/gen2dom-sw/Data/PennStateMeasurements/150606-150610/1230VGain1e7/DDC2Data/PulsedWithLED/Run1/data_0.txt")
AverageWF = xx.FormAverage(1000)
xRange = [0,256]
xLabel = 'time (4 ns bins)'
yRange = [-20,40]
yLabel = 'Count'
color = 'b'
PlotFileBasename = 'AverageWaveform'
PlotWF = PlotWaveform(PlotFileBasename)
PlotWF.Linear(AverageWF,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot
    

# Definitions for waveform cleaning algorithms

# FFT:
ExcludedFreqs = [(0.,0.),(50.,1000.)]
RemoveBaseline = True

# IIR
Tau = 16.0e-9
T = 4.0e-9

# FIR
# Get template waveform
TemplateFile = open("/Users/cowen/Dropbox/SingleChannelDAQ/template.dat","r")
TemplateWaveform = pickle.load(TemplateFile)
TemplateFile.close()


# Definitions for plotter
PlotFileBasename = 'IIR_Waveform'
# Instantiate new plot maker
PlotWF = PlotWaveform(PlotFileBasename)
# Instantiate a new waveform getter
x = GetWaveform("test.dat")
for i in range(0,3):

    # Get a new waveform
    WF = x.NewWaveform()
    
    # Instantiate new waveform cleaner
    y = CleanWaveform(WF)
    # Subtract baseline
    BaselineSubtractedWF = y.SubtractBaseline(0,100)
        
    # run FFT
    # FFTCleanedWF = y.BandFilterFFT(ExcludedFreqs,RemoveBaseline)
    # run IIR   
    IIRCleanedWF = y.FilterIIR(Tau,T)
    
    # define plot params
    xRange = [0,256]
    xLabel = 'time (4 ns)'
    yRange = [-20,40]
    yLabel = 'Count'
    color = 'b'
    # PlotWF.Linear(IIRCleanedWF,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot

    z = AddNoise(BaselineSubtractedWF)
    BipolarSpikeWF = z.BipolarSpike(20.,70.)
    y = CleanWaveform(BipolarSpikeWF)
    IIRCleanedBipolarSpikeWF = y.FilterIIR(Tau,T) 
    yLabel = 'Count w/spike-'+str(i)
    PlotWF.Linear(BipolarSpikeWF,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot
    yLabel = 'Count w/spike (IIR cleaned)-'+str(i)
    PlotWF.Linear(IIRCleanedBipolarSpikeWF,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot

        
    xRange = [0,256]
    xLabel = 'time (ns)'
    yRange = [-10,40]
    yLabel = 'Counts (FIR)'
    color = 'b'
    PlotFilename = "WaveformFIRCLeaned.pdf"
