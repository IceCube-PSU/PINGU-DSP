#
# Class GetWaveform: Opens specified waveform-containing file,
# gets new waveform,
# removes baseline if requested.
#
class Complex:
    def __init__(self, realpart, imagpart):
#        print self.realpart 
        self.r = realpart
        self.i = imagpart

x = Complex(3.0, -4.5)        
print x.r,x.i

class GetWaveform:
    def __init__(self, WaveformFilename):
        self.WaveformFilename = WaveformFilename
        print self.WaveformFilename
        self.WaveformFile = open(self.WaveformFilename,'r')

x = GetWaveform("test.dat")
