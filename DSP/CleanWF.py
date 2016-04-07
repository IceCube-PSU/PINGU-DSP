import numpy as np
class CleanWaveform:
    """Various methods for cleaning waveforms, e.g., via band filter with FFT, or FIR, or IIR..."""
#    def __init__(self):
#        pass
        
    def SubtractBaseline(self,Waveform,FirstSample,LastSample):

        """Subtract off the baseline, calculated as the average of the first LastSample-FirstSample samples"""

        self.Waveform = Waveform
        self.FirstSample = FirstSample
        self.LastSample = LastSample
        
        Baseline = np.average(self.Waveform[self.FirstSample:self.LastSample])
        self.Waveform = self.Waveform - Baseline
        return (self.Waveform)

    def BandFilterFFT(self,Waveform,ExcludedFreqs,RemoveBaseline):

        self.Waveform = Waveform
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
        
    def FilterFIR(self, Waveform, TemplateWaveform, FullOrValid):
        """Run a Finite Impulse Response filter on the data by convolving them with a template waveform"""

        self.Waveform = Waveform
        self.TemplateWaveform = TemplateWaveform
        self.FullOrValid = FullOrValid # Full means to include data past signal boundaries, valid means don't

        CleanedWaveform = np.convolve(self.Waveform,self.TemplateWaveform,mode=self.FullOrValid) 
        
        return CleanedWaveform
        
    def FilterIIR(self, Waveform, Tau, T):
        """Run an Infinite Impulse Response filter on the data"""
        
        self.Waveform = Waveform
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
        
