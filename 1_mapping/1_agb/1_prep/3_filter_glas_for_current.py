#!/usr/bin/env python3
"""Apply current biomass filters and group shots by pixel
Reads in glas shot csvs with pixel id
Applies filters
Then groups them by id and adds "count column"
Then summarizes the groups (e.g. averaging the biomass) and writes the results
The output file can then be used for extracting predictor variables
"""

import sys
import pandas as pd
import numpy as np

# Args
reg_name = sys.argv[1]
in_csv = sys.argv[2]
out_csv = sys.argv[3]

# Min number of shots per pixel
shot_thresh = 5

# Set slope % filter
slope_filt = 15

# Relax filters in counties where we were far below FIA county-level data.
# This csv just contains county IDs with the difference between the county-mean
# using the FIA dataset and v3 of the current 500m biomass map.
county_csv_path = './county_mean_diff_v2.csv'

def ly_check(row):
    ly_array = np.fromstring(row['lossyear_pyunique'][1:-1],dtype=int, sep=' ')
    ly_array += 2000
    ly_array[ly_array==2000] = 0
    ly_out = np.any((ly_array >= 2006) & (ly_array <=2008))
    return(ly_out*1)

def dmask_check(row):
    dmask_array = np.fromstring(row['datamask_pyunique'][1:-1],dtype=int, sep=' ')
    dmask_out = np.invert(np.any(dmask_array != 1))
    return(dmask_out*1)

def get_county_diffs(df,county_csv):
    county_df = pd.read_csv(county_csv)
    df = df.set_index('county_fip').join(county_df.set_index('county_fip'))
    return(df)

def main():
    cur_df = pd.read_csv(in_csv)
    # Select only shots from 2006 on
    cur_df = cur_df.loc[cur_df['YEAR'] >= 2006]
    # Filter out heights >60
    cur_df = cur_df.loc[cur_df['HEIGHT2'] <= 60]
    # Toss out any NaN biomass
    cur_df = cur_df.loc[cur_df['glasBM'].notnull()]

    # Remove water
    cur_df['hansen_dmask'] = cur_df.apply(dmask_check,axis=1,reduce=True)
    cur_df = cur_df.loc[cur_df['hansen_dmask'] == 1]
    # Remove gain
    cur_df = cur_df.loc[cur_df['gain_pymax'] == 0]
    # Remove loss
    cur_df['ly_footprint'] = cur_df.apply(ly_check,axis=1)
    cur_df = cur_df.loc[cur_df['ly_footprint'] == 0]

    # For various rules, set glasBM to 0
    cur_df.loc[(cur_df['treecover2000_max'] <= 10) | (cur_df['HEIGHT2'] < 2) | (cur_df['glasBM'] <= 1),'glasBM'] = 0

    print((cur_df.shape))
    # For palearctic, delete all values > 2000
    if reg_name == 'palearctic':
        cur_df = cur_df.loc[cur_df['glasBM'] < 2000]
    print((cur_df.shape))

    # If the difference between averaged whrc and FIA county data is > 20 Mg/ha,
    # relax the slope filter by 10% AND relax shot_thresh by 1
    if not 'county_fip' in cur_df.columns:
        cur_df['county_fip'] = -9999
    cur_df = get_county_diffs(cur_df,county_csv_path)
    cur_df['relax_filts'] = abs(cur_df['whrcfia_diff'])>20
    cur_df.loc[cur_df['whrcfia_diff'].isnull(),'relax_filts'] = False

    # Slope filter
    cur_df['slope_percent.mean'] = np.tan(cur_df['slope.mean'] * (np.pi/180)) * 100
    cur_df = cur_df.loc[cur_df['slope_percent.mean'] <= (slope_filt + (10 * cur_df['relax_filts']))]
    cur_df['fip'] = cur_df.index.values
    # Group by pixel id
    grped = cur_df.groupby('pixel_id',sort=False)
    # Get mean and shot counts
    grp_mean_counts = grped.agg('mean').join(pd.DataFrame(grped.size(),columns=['shot_count']))
    # Take only with shots greater than or equal to shot_thresh or shot_thresh - 1
    # (depending on relax)
    grp_mean_counts = grp_mean_counts.loc[grp_mean_counts['shot_count'] >= (shot_thresh - (grp_mean_counts['relax_filts']))]
    # Write to csv
    if grp_mean_counts.shape[0] > 0:
        grp_mean_counts.to_csv(out_csv,index=True,header=True,mode='w')
    return()

if __name__ == '__main__':
    main()




