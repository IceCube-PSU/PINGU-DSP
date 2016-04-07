import numpy as np
import matplotlib.pyplot as plt
import pickle

from DSP.GetWF import GetWaveform
from DSP.CreateTemplateWF import CreateTemplateWaveform
from DSP.CleanWF import CleanWaveform
from DSP.AddNoise import AddNoise
from DSP.PlotWF import PlotWaveform
 
# Won't normally need this--plotting function will 
# assume x-values if not provided explicitly
xvals = range(0,1020,4)

# Make a template waveform.  First, get average waveform.

GetWFs = GetWaveform("/Users/cowen/Desktop/PennStateMeasurements/150606-150610/1230VGain1e7/DDC2Data/PMTWaveforms/Run1/data_0.txt")
WF = GetWFs.NewWaveform()
CleanWFs = CleanWaveform()
ManyWFs = CreateTemplateWaveform(GetWFs,CleanWFs)
AverageWF = ManyWFs.FindAverage(100)
