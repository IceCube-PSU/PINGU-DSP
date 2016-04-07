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
                        
