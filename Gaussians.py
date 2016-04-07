from scipy import special
from scipy import stats
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

baseline_probs = []
baseline_rates = []
spe_probs = []
spe_rates = []
ratios = []
pas = []
purities = []
acceptances = []
sns = []
SampleRate = 250.e6 # ADC runs at 250 MHz
ScaleFactor = 20.0 # Each bin appears 20 times in the 80ns window
IntrinsicNoiseRate = 500. # Intrinsic noise rate of DOM is 500Hz
x = np.linspace(50,80,30)
for Acut in range(50,80,1):
    baseline_prob = stats.norm.sf(float(Acut),0.0,13.5)
    baseline_probs.append(baseline_prob)
    baseline_rates.append(SampleRate*baseline_prob/ScaleFactor)
    spe_prob = stats.norm.sf(float(Acut),81.6,26.8)
    spe_probs.append(spe_prob)
    spe_rates.append(IntrinsicNoiseRate*spe_prob)
    ratios.append(IntrinsicNoiseRate*spe_prob/(SampleRate*baseline_prob/ScaleFactor))
    
    N_bg = baseline_prob * 4365.0 * 13.5 * np.sqrt(2*np.pi) # Number of false positives = prob * area = prob * p0 * sigma * sqrt(2pi)
    N_sigtot = 139.4 * 26.8 * np.sqrt(2*np.pi) # Total number of signal events = integral under right hand (high area) gaussian
    N_sig = spe_prob * N_sigtot # fraction of integral above Acut given by spe_prob
    
    purity = 1. - (N_bg/N_sig)
    acceptance = N_sig/N_sigtot # This also equals spe_prob.  Doing it this way for clarity.
    
    purities.append(purity)
    acceptances.append(acceptance)
    pas.append(purity*acceptance)
    sns.append(N_sig/np.sqrt(N_bg))
    
    print N_sig,N_bg,N_sig/np.sqrt(N_bg)
    
plt.suptitle('SPE Triggering Prob and Rate vs. Area_Cut (assume 250MHz clock, 500Hz noise)')

plt.subplot2grid((3,2), (0, 0), colspan=1)
plt.ylim(1.0e-8,1.0e-4)
plt.ylabel('Prob, A > A_Cut')
plt.semilogy(x,baseline_probs,'r')

plt.subplot2grid((3,2), (0, 1), colspan=1)
plt.ylim(0.5,1.0)
plt.plot(x,spe_probs,'g')

plt.subplot2grid((3,2), (1, 0), colspan=2)
plt.ylim(0.01,1000.0)
#plt.xlabel('A_Cut, baseline subtracted (counts)')
plt.ylabel('Rate (Hz), A > A_Cut')
line_bl, = plt.semilogy(x,baseline_rates,'r',label='No LED')
line_spe, = plt.semilogy(x,spe_rates,'g',label='SPE')
line_ratio, = plt.semilogy(x,ratios,'b',label='Ratio')
# Add a legend
plt.legend(handles=[line_spe,line_bl,line_ratio], loc=4)

plt.subplot2grid((3,2), (2, 0), colspan=2)
plt.ylim(10.0,1.0e5)
plt.xlabel('A_Cut, baseline subtracted (counts)')
#plt.ylabel('P*A, A > A_Cut')
#line_pa, = plt.plot(x,pas,'b',label='Purity*Acceptance')

plt.ylabel('S/sqrt(N), A > A_Cut')
line_sn, = plt.semilogy(x,sns,'b',label='S/sqrt(N)')

#line_p, = plt.plot(x,purities,'r',label='Purity')
#line_a, = plt.plot(x,acceptances,'g',label='Acceptance')
# Add a legend
#plt.legend(handles=[line_pa,line_p,line_a], loc=4)
plt.legend(handles=[line_sn], loc=4)

plt.show()
