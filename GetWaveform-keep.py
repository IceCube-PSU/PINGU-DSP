import numpy as np
import matplotlib.pyplot as plt
 
#
# Class GetWaveform: Opens specified waveform-containing file,
# gets new waveform,
# removes baseline if requested.
#

class GetWaveform:
    """Open waveform file, get waveforms, optionally remove baseline"""
    def __init__(self,WaveformFilename):
        self.WaveformFilename = WaveformFilename
        self.WaveformFile = open(self.WaveformFilename,'r')
        self.LastPosition = self.WaveformFile.tell()
        print "Opened waveform file: ",WaveformFilename

    def NewWaveform(self):
        """Get a new waveform from the designated file."""

        WaveformYvals = []

        NextWaveform = False
        line = "blah"
        self.WaveformFile.seek(self.LastPosition)        
        while not NextWaveform and line != "":
            line = self.WaveformFile.readline()
                        
            splits = line.split(",")
                        
            if len(splits) == 6:
                adcval = float(splits[1])
                NextWaveform = int(splits[4]) # Waveform ends when last number in row==1
                if not NextWaveform:
                    WaveformYvals.append(adcval)
                                
        self.LastPosition = self.WaveformFile.tell()
        if len(WaveformYvals) > 200: # only take cases with sufficient number of digitizations
            return WaveformYvals
        else:
            return None
                        
class CreateTemplateWaveform:
    """Read in many waveforms, subtract baseline, select ones likely to have SPEs, average them."""
    def __init__(self,WaveformFilename):
        self.x = GetWaveform(WaveformFilename)
        self.NPulses = 0
        
    def FormAverage(self,NumberToAverage):
        self.NumberToAverage = NumberToAverage
        for i in range(0,NumberToAverage):
            self.WF = self.x.NewWaveform()
            if self.WF != None:
                self.y = CleanWaveform(self.WF)
                self.BaselineSubtractedWF = self.y.SubtractBaseline(0,100)
                PulsePresent = False
                for bin in range(0,255):
                    if self.BaselineSubtractedWF[bin] > 10: PulsePresent = True
                if PulsePresent:
                    self.NPulses += 1
                    if self.NPulses == 1:
                        self.SummedWF = self.BaselineSubtractedWF
                    else:
                        self.SummedWF += self.BaselineSubtractedWF
        if self.NPulses > 0:
            return self.SummedWF/self.NPulses
                


class CleanWaveform:
    """Various methods for cleaning waveforms, e.g., via band filter with FFT, or FIR, or IIR..."""
    def __init__(self,Waveform):
        self.Waveform = Waveform

    def SubtractBaseline(self,FirstSample,LastSample):

        """Subtract off the baseline, calculated as the average of the first LastSample-FirstSample samples"""

        self.FirstSample = FirstSample
        self.LastSample = LastSample
        
        Baseline = np.average(self.Waveform[self.FirstSample:self.LastSample])
        self.Waveform = self.Waveform - Baseline
        return (self.Waveform)

    def BandFilterFFT(self,ExcludedFreqs,RemoveBaseline):
        self.ExcludedFreqs = ExcludedFreqs # form: [(fmin1,fmax1),(fmin2,fmax2),...] in MHz
        self.RemoveBaseline = RemoveBaseline # if True, zero out the zero freq bin
        
        StdFFT = np.fft.fft(self.Waveform) # Perform the FFT
        FFTLen = len(StdFFT)
        StdFrequencies = np.fft.fftfreq(FFTLen,4.e-9)/1.e6 # units are MHz
#        StdPowerSpectrum = np.abs(StdFFT)**2


        if RemoveBaseline:
            StdFFT[0] = 0.0 # remove mean (baseline)
        
        for ExcludedFreq in self.ExcludedFreqs: # form: [(fmin1,fmax1),(fmin2,fmax2),...] in MHz
            MinFreq = ExcludedFreq[0]
            MaxFreq = ExcludedFreq[1]
            for Freq in StdFrequencies:
                if ((Freq>=MinFreq and Freq<=MaxFreq) or (Freq<=-MinFreq and Freq>=-MaxFreq)):
                    StdFFT[Freq] = 0.0
                                                
        CleanedWaveform = np.fft.ifft(StdFFT).real
        
        return CleanedWaveform
        
    def FilterFIR(self, TemplateWaveform, FullOrValid):
        """Run a Finite Impulse Response filter on the data by convolving them with a template waveform"""

        self.TemplateWaveform = TemplateWaveform
        self.FullOrValid = FullOrValid # Full means to include data past signal boundaries, valid means don't

        CleanedWaveform = np.convolve(self.Waveform,self.TemplateWaveform,mode=self.FullOrValid) 
        
        return CleanedWaveform
        
    def FilterIIR(self, Tau, T):
        """Run an Infinite Impulse Response filter on the data"""
        
        self.Tau = Tau # e.g. 8.0e-9
        self.T = T
        CleanedWaveform = []
        
        # Filter definition: x = input, y = output, t = time, T = sampling period, tau = filter time constant
        #    y[0] = x[0]*T/tau
        #    y[t] = exp[-T/tau]*y[t-T] + x[t]*T/tau                   
                                                
        CleanedWaveform.append(self.Waveform[0]*self.T/self.Tau)
        for TimeBin in range(1,len(self.Waveform)-1):
            CleanedWaveform.append(np.exp(-self.T/self.Tau)*CleanedWaveform[TimeBin - 1] + self.Waveform[TimeBin]*self.T/self.Tau)
              
        return CleanedWaveform
        
class AddNoise:
    """Add various kinds of noise to test robustness of algorithm"""
    
    def __init__(self,Waveform):
        self.Waveform = Waveform
        
    def BipolarSpike(self,Amplitude,Position):
        # Add bipolar spike with given amplitude at given position
        self.Amplitude = Amplitude
        self.Position = Position
        
        self.Waveform[self.Position] += self.Amplitude
        self.Waveform[self.Position+1] -= self.Amplitude
        
        return self.Waveform
        
    def BaselineDrift(self,Slope):
        # Add sloped line to mimic baseline drift
        pass
        

class PlotWaveform:
 
    """Plot a single waveform"""
                                   
    def __init__(self,PlotFileBasename):
        self.PlotFileBasename = PlotFileBasename  
        self.PlotNum = 0

        
    def Linear(self,Waveform,xvals,xRange,xLabel,yRange,yLabel,color):
        
        self.Waveform = Waveform
        self.xvals = xvals
        self.xmin = xRange[0]
        self.xmax = xRange[1]
        self.xLabel = xLabel
        self.ymin = yRange[0]
        self.ymax = yRange[1]
        self.yLabel = yLabel
        self.color = color    
                        
        plt.xlim(self.xmin,self.xmax)
        plt.xlabel(self.xLabel)
        plt.ylim(self.ymin,self.ymax)
        plt.ylabel(self.yLabel)
        plt.plot(self.Waveform,self.color)

        self.PlotNum += 1
        if self.PlotNum < 10:
            NumLabel = '0' + str(self.PlotNum)
        else:
            NumLabel = str(self.PlotNum)
        PlotFilename = self.PlotFileBasename + "_" + NumLabel + ".pdf"
        plt.savefig(PlotFilename)
        plt.close()
        
if __name__ == '__main__':

    import pickle

    # Won't normally need this--plotting function will 
    # assume x-values if not provided explicitly
    xvals = range(0,1020,4)

    # Make a template waveform.  First, get average waveform.
    
    xx = CreateTemplateWaveform("/Users/cowen/Desktop/PennStateMeasurements/150606-150610/1230VGain1e7/DDC2Data/PMTWaveforms/Run1/data_0.txt")
    AverageWF = xx.FormAverage(1000)
    xRange = [0,256]
    xLabel = 'time (4 ns bins)'
    yRange = [-20,40]
    yLabel = 'Count'
    color = 'b'
    PlotFileBasename = 'AverageWaveform'
    PlotWF = PlotWaveform(PlotFileBasename)
    PlotWF.Linear(AverageWF,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot

    # Clean average waveform
    ExcludedFreqs = [(0.,0.),(50.,1000.)]   

    # Definitions for waveform cleaning algorithms

    # FFT:
    ExcludedFreqs = [(0.,0.),(60.,65.),(99.,103.),(110.,1000.,)(-65.,-60),(-103.,-99.),(-110.,-1000.)]
    RemoveBaseline = True

    TemplateClean = CleanWaveform(AverageWF)
    FFTTemplateClean = TemplateClean.BandFilterFFT(ExcludedFreqs,RemoveBaseline)

    PlotFileBasename = 'TemplateWaveform'
    PlotTemplateClean = PlotWaveform(FFTTemplateClean,xvals,PlotFileBasename)
    PlotTemplateClean.Linear(xRange,xLabel,yRange,yLabel,color) # make a linear plot
        
        
    xRange = [0,256]
    xLabel = 'time (ns)'
    yRange = [-10,40]
    yLabel = 'Counts (FFT)'
    color = 'b'
    PlotFilename = "WaveformFFTCLeaned.pdf"


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
#        PlotWF.Linear(IIRCleanedWF,xvals,xRange,xLabel,yRange,yLabel,color) # make a linear plot

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
    
