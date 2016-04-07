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
        

