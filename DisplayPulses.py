
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import subprocess

parser = ArgumentParser(description=
                        '''Displays the waveforms for some requirement on the thresholds. You must specify True of False for all thresholds you want to consider. If they remain None then they will not be considered. If all remain as None then all waveforms will be displayed.''',
                        formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument('-f','--infile',
                    action='store',
                    required = True,
                    help="List of file names and which triggers they passed")
parser.add_argument('-TA','--total_amplitude',
                    action='store',
                    help="Display pulses which passed the total amplitude threshold")
parser.add_argument('-SiT','--single_threshold',
                    action='store',
                    help="Display pulses which exceeded the required threshold at least once")
parser.add_argument('-IA','--increasing_amplitude',
                    action='store',
                    help="Display pulses which exceeded the required threshold and the subsequent bin increased in amplitude")
parser.add_argument('-DT','--double_threshold',
                    action='store',
                    help="Display pulses which exceeded the required threshold in two consecutive bins")
parser.add_argument('-SeT','--second_threshold',
                    action='store',
                    help="Display pulses which exceeded the first threshold and then exceeded a second threshold in the subsequent bin")
parser.add_argument('-SuT','--sum_threshold',
                    action='store',
                    help="Display pulses which exceeded the first threshold and then exceeded a second threshold on the sum of this and the subsequent bin")
parser.add_argument('-DP','--double_pulses',
                    action='store',
                    help="Displays pulses which passed the total amplitude threshold for a possible double pulse")
parser.add_argument('-d','--fig_dir',
                    action='store',
                    required = True,
                    help="Directory containing output waveform plots")

args = parser.parse_args()

infile = args.infile
fig_dir = args.fig_dir
TA = args.total_amplitude
SiT = args.single_threshold
IA = args.increasing_amplitude
DT = args.double_threshold
SeT = args.second_threshold
SuT = args.sum_threshold
DP = args.double_pulses

GoodInput = False

if TA is not None:
    if TA == "True" or TA == "False":
        GoodInput = True
if SiT is not None:
    if SiT == "True" or SiT == "False":
        GoodInput = True
if IA is not None:
    if IA == "True" or IA == "False":
        GoodInput = True
if DT is not None:
    if DT == "True" or DT == "False":
        GoodInput = True
if SeT is not None:
    if SeT == "True" or SeT == "False":
        GoodInput = True
if SuT is not None:
    if SuT == "True" or SuT == "False":
        GoodInput = True
if DP is not None:
    if DP == "True" or DP == "False":
        GoodInput = True

if TA == SiT == IA == DT == SeT == SuT == DP == None:
    GoodInput = True

if GoodInput == False:
    print "One of your inputs is not True of False. Try again. The capital is important..."

else:

    infile = open(infile, 'r')

    subprocess.call(["mkdir",fig_dir+"temp"])

    imglist = []

    for line in infile.readlines():

        if len(line.split()) == 8:

            if line.split()[0] != "FN":

                GoodFile = True
                if TA is not None:
                    GoodFile = GoodFile and line.split()[1] == TA
                if SiT is not None:
                    GoodFile = GoodFile and line.split()[2] == SiT
                if IA is not None:
                    GoodFile = GoodFile and line.split()[3] == IA
                if DT is not None:
                    GoodFile = GoodFile and line.split()[4] == DT
                if SeT is not None:
                    GoodFile = GoodFile and line.split()[5] == SeT
                if SuT is not None:
                    GoodFile = GoodFile and line.split()[6] == SuT
                if DP is not None:
                    GoodFile = GoodFile and line.split()[7] == DP

                if GoodFile:
                    subprocess.call(["cp",fig_dir+line.split()[0]+".png",fig_dir+"temp/"])
                    imglist.append(line.split()[0]+".png")
                

    subprocess.call(["eog",fig_dir+"temp/"+imglist[0]])
    
    subprocess.call(["rm","-r",fig_dir+"temp"])
