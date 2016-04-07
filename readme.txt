Number of waveform records in 1e7 gain datafiles:

cat 150606-150610/1230VGain1e7/DDC2Data/PMTWaveforms/Run1/data_0.txt | grep "    0,  " | wc
  105382  526910 3372224

cat 150606-150610/1230VGain1e7/DDC2Data/PMTWaveforms/Test/testdata_0.txt  | grep "    0,  " | wc
   16137   80685  516384

cat 150606-150610/1230VGain1e7/DDC2Data/BaselineMeasurements/Run1  | grep "    0,  " | wc
    3323   16615  106336

cat 150606-150610/1230VGain1e7/DDC2Data/BaselineMeasurements/Test/data_0.txt  | grep "    0,  " | wc
     281    1405    8992
