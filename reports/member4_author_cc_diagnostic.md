# Member 4 XJTU Candidate Extraction and Validation

## Status

All reported values are candidate approximations. The original workbook feature-generation source was not located; numerical agreement does not verify a formula.

- Features with at least one valid comparison: 67/67.
- No feature is source-verified. The four entropy columns have unknown original definitions; their histogram values are diagnostics only.
- CC selection method: `author_documented`.
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
| CC_energy | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.0591279 | 0.0845927 | 1.95672 | 1.20965 |
| CC_Q | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.0141363 | 0.0206067 | 0.487267 | 1.12826 |
| CC_t_mean | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.0904209 | 0.111898 | 3.66214 | 1.04938 |
| CC_V_mean | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.00343047 | 0.00454062 | 0.0876618 | 0.0874244 |
| CC_T_mean | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.0193083 | 0.0473758 | 4.69486 | 0.0700866 |
| CC_V_std | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.00172388 | 0.00240089 | 0.0325778 | 1.29023 |
| CC_T_std | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.00947191 | 0.0363798 | 3.98816 | 0.718908 |
| CC_V_skewness | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.068404 | 0.0934109 | 1.23976 | 26.9603 |
| CC_T_skewness | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.0164421 | 0.0270347 | 0.700805 | 3.18192 |
| CC_V_kurtosis | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.123566 | 0.182948 | 1.94783 | 5.33301 |
| CC_T_kurtosis | Original formula implementation not located; candidate approximation only. | 25149 | 1171 | 0.0373622 | 0.179803 | 7.1377 | 1.61721 |
| CC_CCCT | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.180543 | 0.222438 | 7.30887 | 1.04763 |
| CC_entropy | Original formula unknown; histogram proxy is diagnostic only. | 25149 | 1171 | 5.08626 | 5.08682 | 5.97346 | 66.2908 |
| dV_energy | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.00974197 | 0.0474203 | 0.945185 | 1.00572 |
| dV_Q | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.00246832 | 0.012035 | 0.239573 | 1.00559 |
| dV_t_mean | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.00856564 | 0.0184993 | 1.80084 | 0.514543 |
| dV_V_mean | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.000246578 | 0.00113935 | 0.0320106 | 0.00624817 |
| dV_T_mean | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.00675357 | 0.0317609 | 4.46835 | 0.024157 |
| dV_V_std | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.000126108 | 0.00020817 | 0.0162042 | 0.437323 |
| dV_T_std | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.00751303 | 0.0187942 | 0.584155 | 2.99002 |
| dV_V_skewness | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.00741742 | 0.0468744 | 0.545697 | 4.87781 |
| dV_T_skewness | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.122259 | 0.358999 | 15.7682 | 50.1472 |
| dV_V_kurtosis | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.00440704 | 0.021496 | 0.287332 | 0.241534 |
| dV_T_kurtosis | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.272641 | 2.55133 | 252.696 | 13.1812 |
| dV_dV_devide_dt | Original formula implementation not located; candidate approximation only. | 25148 | 1172 | 0.000499412 | 0.00526856 | 0.483132 | 1.67083 |
| dV_entropy | Original formula unknown; histogram proxy is diagnostic only. | 25148 | 1172 | 4.76763 | 4.76898 | 4.99295 | 63.3067 |
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
