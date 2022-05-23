#!/usr/bin/env python3
"""Apply potential biomass filters and group shots by pixel
Reads in glas shot csvs with pixel id
Applies filters
Then groups them by id
Then summarizes the groups (e.g. averaging the biomass) and writes the results
The output file can then be used for extracting predictor variables
"""

import numpy as np
import sys
import pandas as pd
import subprocess
import math
import os
import glob

# Args
reg_name = sys.argv[1]
in_csv = sys.argv[2]
out_csv = sys.argv[3]

# Define filter key.
# This a shorthand way of setting the potential filters
# For example: 'h500-r2k-i-s15-tc10-w'
# Options are:
# h500 = At least 500m from Hansen loss gain
# h = At least 1km from Hansen loss/gain
# r2k, r3k, r4k, r5k, r10k = At least # km from road.
# i = Not in one on of the igbp_exclude landcover classes.
# s# = Set slope filter to # percentage (e.g. s15 for 15)
# tc# = Set treecover 0-setting to # percent. Anything below this will be set to
#       0 Mg/ha
# w = Filter out water using Hansen datamask
filter_key = 'h500-r2k-i-s15-tc10-w'

# Min number of shots per pixel
shot_thresh = 3

# Relax filters in counties where we were far below FIA county-level data.
# This csv just contains county IDs with the difference between the county-mean
# using the FIA dataset and v3 of the actual 500m biomass map.
county_csv_path = './county_mean_diff_v2.csv'

# Which igbp classes to exclude
igbp_exclude = [12,13,14]

def dmask_check(row):
    dmask_array = np.fromstring(row['datamask_pyunique'][1:-1],dtype=int,
                                sep=' ')
    dmask_out = np.invert(np.any(dmask_array != 1))
    return(dmask_out*1)

def get_county_diffs(df,county_csv):
    county_df = pd.read_csv(county_csv)
    df = df.set_index('county_fip').join(county_df.set_index('county_fip'))
    return(df)

# Function to apply filters to csv based on supplied key. Returns filtered df
def apply_filters(temp_df,filt_key):
    if 'h500' in filt_key:
        temp_df = temp_df.loc[(temp_df.lossyear >= 500) & (temp_df.gain >= 500)]
    elif 'h' in filt_key:
        temp_df = temp_df.loc[(temp_df.lossyear >= 1000) & (temp_df.gain >= 1000)]
    if 'r2k' in filt_key:
        temp_df = temp_df.loc[temp_df.roads2k==0]
    if 'r3k' in filt_key:
        temp_df = temp_df.loc[temp_df.roads3k==0]
    if 'r4k' in filt_key:
        temp_df = temp_df.loc[temp_df.roads4k==0]
    if 'r5k' in filt_key:
        temp_df = temp_df.loc[temp_df.roads5k==0]
    if 'r10k' in filt_key:
        temp_df = temp_df.loc[temp_df.roads10k==0]
    if 'i' in filt_key:
        temp_df = temp_df.loc[~temp_df.igbp.isin(igbp_exclude)]
    if 's' in filt_key:
        slope_filt = int((filt_key.split('s')[-1]).split('-')[0])
        # Slope filter of 25 if within target county
        temp_df = temp_df.loc[temp_df['slope_percent.mean'] <= \
                    (slope_filt*np.logical_not(temp_df['relax_filts']) + 25*temp_df['relax_filts'])]
    if 'tc' in filt_key:
        tc_rule = int((filt_key.split('tc')[-1]).split('-')[0])
        temp_df.loc[temp_df['treecover2000_max'] <= tc_rule,'glasBM'] = 0
    if 'w' in filt_key:
        temp_df['hansen_dmask'] = temp_df.apply(dmask_check,axis=1,reduce=True)
        temp_df = temp_df.loc[temp_df.hansen_dmask==1]
    return(temp_df)

def main():

    # Read input csv
    cur_df = pd.read_csv(in_csv)

    # If the difference between averaged whrc and FIA county data is > 20 Mg/ha,
    # relax the slope filter by 10%
    if not 'county_fip' in cur_df.columns:
        cur_df['county_fip'] = -9999
    cur_df = get_county_diffs(cur_df,county_csv_path)
    cur_df['relax_filts'] = abs(cur_df['whrcfia_diff'])>20
    cur_df.loc[cur_df['whrcfia_diff'].isnull(),'relax_filts'] = False

    # Calculate slope percent
    cur_df['slope_percent.mean'] = np.tan(cur_df['slope.mean'] * (np.pi/180)) * 100

    # Isolate any within IFL layer
    ifl_df = cur_df.loc[cur_df['IFL13'] == 1]
    ifl_df = apply_filters(ifl_df,'s15-w') # Only filter slope & water within IFL

    # Apply potential filters to shots outside IFL
    nonifl_df = cur_df.loc[cur_df['IFL13'] != 1]
    nonifl_df = apply_filters(nonifl_df,filter_key)

    # Merge IFL and non-IFL Shots
    cur_df = pd.concat([ifl_df,nonifl_df])

    # Filter out heights >60
    cur_df = cur_df.loc[cur_df['HEIGHT2']<=60]

    # Toss out any NaN biomass
    cur_df = cur_df.loc[cur_df['glasBM'].notnull()]

    # For various rules, set glasBM to 0
    cur_df.loc[(cur_df['HEIGHT2'] < 2) | (cur_df['glasBM'] <= 1),'glasBM'] = 0

    # For palearctic, delete all values > 2000
    if reg_name == 'palearctic':
        cur_df = cur_df.loc[cur_df['glasBM'] < 2000]

    # Select groups that have enough shots to pass threshold
    enough_shots = cur_df.groupby('pixel_id',sort=False).filter(lambda x: len(x) >= shot_thresh)
    grp_max = enough_shots.groupby('pixel_id',sort=False).max()
    grp_mean = enough_shots.groupby('pixel_id',sort=False).mean()

    # Assign glasBM values
    grp_final = grp_mean
    grp_final['glasBM_mean'] = grp_mean['glasBM']
    grp_final['glasBM_max'] = grp_max['glasBM']
    grp_final.loc[(grp_final['IFL13'] == 1.0),'glasBM'] = grp_final['glasBM_mean']
    grp_final.loc[(grp_final['IFL13'] != 1.0),'glasBM'] = grp_final['glasBM_max']
    grp_final['pixel_id'] = grp_final.index

    # Write out to csv
    if grp_final.shape[0] > 0:
        grp_final.to_csv(out_csv,index=False,header=True,mode='w')

    return()

if __name__ == '__main__':
    main()




