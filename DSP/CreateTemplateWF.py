class CreateTemplateWaveform:
    """Read in many waveforms, subtract baseline, select ones likely to have SPEs, average them."""
        
    def __init__(self,GetWaveform,CleanWaveform):
        self.Get = GetWaveform
        self.Clean = CleanWaveform
        self.NPulses = 0
        
    def FindAverage(self,NumberToAverage):
        self.NumberToAverage = NumberToAverage
        print "Processing ",self.NumberToAverage," waveforms..."
        for i in range(0,NumberToAverage):
            self.WF = self.Get.NewWaveform()
            if self.WF != None:
#                print "FindAverage WF = ",self.WF
#                CleanWF = self.Clean(self.WF)
                self.BaselineSubtractedWF = self.Clean.SubtractBaseline(self.WF,0,100)
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
            print "Averaged NPulses = ",self.NPulses
            return self.SummedWF/self.NPulses
        elif self.NPulses == 0:
            print "Found no pulses!"
                
