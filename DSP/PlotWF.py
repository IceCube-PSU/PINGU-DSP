class PlotWaveform:
 
    """Plot a single waveform"""
                                   
    def __init__(self,PlotFileBasename):
        self.PlotFileBasename = PlotFileBasename  
        self.PlotNum = 0
        
    def Linear(self,Waveform,plt,xvals,xRange,xLabel,yRange,yLabel,color):
                
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
        plt.clf()
        
