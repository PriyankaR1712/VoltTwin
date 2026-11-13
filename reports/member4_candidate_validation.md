# Member 4 XJTU Candidate Extraction and Validation

## Status

All reported values are candidate approximations. The original workbook feature-generation source was not located; numerical agreement does not verify a formula.

- Features with at least one valid comparison: 67/67.
- No feature is source-verified. The four entropy columns have unknown original definitions; their histogram values are diagnostics only.
- CC selection method: `adaptive_candidate`.
- CV begins at the first rising 4.199 V crossing.
- Candidate dV window: 3.9-4 V; candidate dI window: 1-0.9 A.
- The optional author-documented CC selector uses current >= 3.9 A and voltage <= 4.199 V; it is not evidence that the workbook used that rule.
- Statistics use a 257-point uniform-time interpolation grid; integrals use trapezoidal integration over stored timestamps and interpolated boundaries.
- Entropy is an explicitly diagnostic 16-bin histogram proxy; the original entropy definition remains unknown.

## Alignment and limitations

Equal-count profiles are compared positionally and labeled `positional_unverified_equal_counts`; this does not prove cycle identity. Unequal-count profiles use unique monotone capacity-label matches only. Ambiguous or unmatched rows are excluded and reported in the CSV.
The benchmark MAT traces contain 128 samples per cycle with nonuniform `relative_time_min` spacing. No resampling is assumed to recover the original acquisition samples.

## Batch alignment coverage

| Batch | Paired rows | Unmatched workbook rows | Ambiguous rows | Alignment method | Mean absolute label difference |
|---|---:|---:|---:|---|---:|
| batch-1 | 3211 | 0 | 0 | positional_unverified_equal_counts | 0 |
| batch-2 | 3727 | 0 | 0 | positional_unverified_equal_counts | 0.000136303 |
| batch-3 | 4608 | 0 | 0 | positional_unverified_equal_counts | 1.00249e-05 |
| batch-4 | 5670 | 0 | 0 | positional_unverified_equal_counts | 0.000853106 |
| batch-5 | 1975 | 0 | 0 | positional_unverified_equal_counts | 0.000269891 |
| batch-6 | 7129 | 617 | 489 | unique_monotone_capacity_diagnostic | 7.5811e-11 |

Capacity-label agreement does not prove cycle identity; equal-count profiles remain positional and unequal-count matches are conservative diagnostics only.

## Overall candidate metrics

| Feature | Status | Valid pairs | Invalid candidates | MAE | RMSE | Max abs error | Relative error (%) |
|---|---|---:|---:|---:|---:|---:|---:|
| CC_energy | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.05827 | 0.0837421 | 1.95672 | 1.21149 |
| CC_Q | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0139619 | 0.0204608 | 0.487267 | 1.1326 |
| CC_t_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.170495 | 1.39068 | 29.446 | 1.93215 |
| CC_V_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0033789 | 0.00448881 | 0.0876618 | 0.0860544 |
| CC_T_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.018639 | 0.0463517 | 4.69486 | 0.0682144 |
| CC_V_std | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00172823 | 0.00245684 | 0.0325778 | 1.3036 |
| CC_T_std | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00939202 | 0.0357819 | 3.98816 | 0.743237 |
| CC_V_skewness | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0662954 | 0.0922408 | 1.23976 | 26.4033 |
| CC_T_skewness | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0358548 | 0.251666 | 8.95146 | 6.83491 |
| CC_V_kurtosis | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.1192 | 0.179649 | 1.94783 | 5.18061 |
| CC_T_kurtosis | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.108124 | 1.36246 | 92.7884 | 4.50042 |
| CC_CCCT | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.340691 | 2.78206 | 58.9 | 1.93045 |
| CC_entropy | Original formula unknown; histogram proxy is diagnostic only. | 26320 | 0 | 5.08989 | 5.09048 | 5.97346 | 66.2489 |
| dV_energy | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.00938004 | 0.0463554 | 0.945185 | 0.979687 |
| dV_Q | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.00237649 | 0.0117648 | 0.239573 | 0.979531 |
| dV_t_mean | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.0193947 | 0.174317 | 2.80205 | 1.13005 |
| dV_V_mean | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.000240161 | 0.00111403 | 0.0320106 | 0.00608541 |
| dV_T_mean | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.00661501 | 0.0310676 | 4.46835 | 0.0238683 |
| dV_V_std | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.000124404 | 0.000204795 | 0.0162042 | 0.431356 |
| dV_T_std | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.0074668 | 0.0184635 | 0.584155 | 3.08826 |
| dV_V_skewness | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.0071889 | 0.0458259 | 0.545697 | 4.86226 |
| dV_T_skewness | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.147387 | 0.479917 | 19.3106 | 53.1487 |
| dV_V_kurtosis | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.00430572 | 0.0210237 | 0.287332 | 0.236127 |
| dV_T_kurtosis | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.460804 | 4.69338 | 253.437 | 20.6592 |
| dV_dV_devide_dt | Original formula implementation not located; candidate approximation only. | 26319 | 1 | 0.000489833 | 0.00515942 | 0.483132 | 1.66954 |
| dV_entropy | Original formula unknown; histogram proxy is diagnostic only. | 26319 | 1 | 4.78007 | 4.78173 | 5.16378 | 63.3644 |
| CV_energy | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0318277 | 0.040548 | 1.37877 | 2.17362 |
| CV_Q | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00757787 | 0.00965442 | 0.328575 | 2.17355 |
| CV_t_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0631136 | 0.130323 | 6.77555 | 0.448565 |
| CV_C_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0106936 | 0.0177545 | 1.16126 | 1.42371 |
| CV_T_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0150715 | 0.0979953 | 15.5315 | 0.0612713 |
| CV_C_std | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0186477 | 0.023706 | 0.905932 | 2.09118 |
| CV_T_std | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00978819 | 0.0387091 | 5.42331 | 0.442356 |
| CV_C_skewness | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0160773 | 0.0229722 | 1.28264 | 0.81927 |
| CV_T_skewness | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0136273 | 0.0825089 | 3.76948 | 1.95576 |
| CV_C_kurtosis | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0775899 | 0.102024 | 3.82326 | 1.21442 |
| CV_T_kurtosis | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0180148 | 0.127118 | 19.5024 | 0.856228 |
| CV_CVCT | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.118418 | 0.255437 | 13.5619 | 0.420934 |
| CV_entropy | Original formula unknown; histogram proxy is diagnostic only. | 26320 | 0 | 4.69812 | 4.69892 | 4.9541 | 71.8325 |
| dI_energy | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.00120781 | 0.00321231 | 0.113078 | 2.66033 |
| dI_Q | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.000287578 | 0.000764846 | 0.0269253 | 2.66033 |
| dI_t_mean | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.00907109 | 0.0241702 | 0.845233 | 2.65277 |
| dI_C_mean | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.000565289 | 0.00175747 | 0.0488971 | 0.0596005 |
| dI_T_mean | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.0156944 | 0.144606 | 21.5505 | 0.0594066 |
| dI_C_std | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.000321975 | 0.00109549 | 0.0311349 | 1.1137 |
| dI_T_std | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.0122647 | 0.0156039 | 0.170183 | 11.7917 |
| dI_C_skewness | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.0092242 | 0.0193847 | 0.550399 | 14.8784 |
| dI_T_skewness | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.273947 | 0.457013 | 16.185 | 100.821 |
| dI_C_kurtosis | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.0110464 | 0.0164893 | 0.420673 | 0.611908 |
| dI_T_kurtosis | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.447181 | 2.99022 | 253.268 | 21.2894 |
| dI_dI_devide_dt | Original formula implementation not located; candidate approximation only. | 26245 | 75 | 0.00120525 | 0.00482653 | 0.123063 | 0.818599 |
| dI_entropy | Original formula unknown; histogram proxy is diagnostic only. | 26245 | 75 | 2.56788 | 2.58154 | 3.53344 | 48.1058 |
| Charge_energy | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0052803 | 0.0332949 | 2.08451 | 0.0841218 |
| Charge_Q | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00129092 | 0.00814812 | 0.517682 | 0.0816022 |
| Charge_t_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.128569 | 1.92342 | 39.1466 | 0.562149 |
| Charge_V_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.000927417 | 0.00135476 | 0.0320822 | 0.0226667 |
| Charge_C_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00181077 | 0.0088228 | 1.25698 | 0.0877917 |
| Charge_T_mean | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00690731 | 0.0710677 | 11.2514 | 0.0269862 |
| Charge_C_std | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00115757 | 0.00371013 | 0.368709 | 0.0633581 |
| Charge_V_std | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00182831 | 0.00251069 | 0.0553236 | 1.18148 |
| Charge_T_std | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00674249 | 0.0668666 | 6.31915 | 0.284609 |
| Charge_C_skewness | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00249677 | 0.00977719 | 0.915336 | 0.675472 |
| Charge_V_skewness | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0317812 | 0.0605213 | 4.19982 | 2.52401 |
| Charge_T_skewness | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00907193 | 0.0651468 | 1.45896 | 4.75128 |
| Charge_C_kurtosis | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.00505621 | 0.0306704 | 1.94705 | 0.370303 |
| Charge_V_kurtosis | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.183477 | 0.483252 | 41.2223 | 5.42302 |
| Charge_T_kurtosis | Original formula implementation not located; candidate approximation only. | 26320 | 0 | 0.0152727 | 0.105186 | 2.04314 | 0.947001 |
