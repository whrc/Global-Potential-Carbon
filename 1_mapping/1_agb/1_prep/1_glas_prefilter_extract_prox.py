#!/usr/bin/env python3
"""Extracts road and Loss/Gain distance, plus Hansen data within GLAS footprint

Extracts values for filtering actual and potential GLAS shots.
proximity_extracts() extracts the distances to road and Hansen loss/gain
footprint_extracts() extracts data within GLAS footprint for.
"""

import numpy as np
import sys
import gdal
import pandas as pd
import subprocess
import math
from pyproj import Proj, transform
import os

tile_id = sys.argv[1]
in_roads = sys.argv[2]
in_csv_path = sys.argv[3]
out_csv_path = sys.argv[4]
hansen_dir = sys.argv[5]
temp_dir = sys.argv[6]

lossgain_dis = 500
vrt_padding = 0.06 # in degrees
dir_dict = {'S':-1,'N':1,'W':-1,'E':1}
lat_dir_dict = {True:'N',False:'S'}
lon_dir_dict = {True:'E',False:'W'}
subprocess.call(['mkdir','-p',temp_dir])
rd_dist_list = [2] # in km

# settings for footprint extract
num_sample_points = 2000
buffer_radius = 35

def meters_to_dd(meter_distance,lat):
    """Converts meters to decimal degrees (then used for ellipse axes)."""
    lat_equator = 110574.27
    lon_equator = 111319.46
    lon_meters = lon_equator * np.cos(np.radians(lat))
    lat_meters = lat_equator * (1 + 0*lat)
    dd_distance_lat = meter_distance/lat_meters
    dd_distance_lon = meter_distance/lon_meters
    return(dd_distance_lon,dd_distance_lat)


def generate_random_points(center_x,center_y, x_axis, y_axis, N):
    """ Generates N random points in an ellipse.
    Instead of doing it a better way, I generate 2*N points then clip to N.
    Takes ~20 seconds for 100,000 coords w/ N = 100."""
    xmin,xmax,ymin,ymax = (center_x - x_axis, center_x + x_axis,
                           center_y - y_axis, center_y + y_axis)
    sample_coords = np.random.rand(N*2,2) * [xmax-xmin,ymax-ymin] + [xmin,ymin]
    clip_array = (((((sample_coords[:,0] - center_x)**2)/(x_axis**2) + ((sample_coords[:,1] - center_y)**2)/(y_axis**2)) <= 1))
    clipped_coords = sample_coords[clip_array]
    clipped_final = clipped_coords[np.random.choice(clipped_coords.shape[0], N, replace=False), :]
    return(clipped_final)


def buffer_extract_point(point_coords,im_band,geotrans,ellipse_axes,raster_dims):
    """ Takes one set of coordinates and returns array of extracted point values"""
    ellipse_x_axis = ellipse_axes[0]
    ellipse_y_axis = ellipse_axes[1]
    # Get buffered coordinates
    buff_coords = generate_random_points(point_coords[0],point_coords[1],ellipse_x_axis,ellipse_y_axis,num_sample_points)
    # Get indices
    y_indices, x_indices = get_indices(buff_coords,geotrans)
    # Eliminate oob observations
    oob_obs = np.where((y_indices < 0) | (y_indices >= raster_dims[1]) |
                       (x_indices < 0) | (x_indices >= raster_dims[0]))[0]
    del_mask = np.ones(len(y_indices), dtype=bool)
    del_mask[oob_obs]=False
    if(len(oob_obs)>0):
        print(("oob_obs_count = " + str(len(oob_obs))))
    y_indices = y_indices[del_mask]
    x_indices = x_indices[del_mask]
    # Get unique indices and how many of each
    unique_indices,indices_counts = np.unique(np.vstack((x_indices,y_indices)).T,axis=0,return_counts=True)
    # Extract
    extracted_vals_unique = [im_band.ReadAsArray(unique_indices[i,0],unique_indices[i,1],1,1) for i in range(0,unique_indices.shape[0])]
    # Repeat to make array
    extracted_array = np.repeat(extracted_vals_unique,indices_counts)
    # Return array
    return(extracted_array)


def extract_hansen_footprint(image_path,coords_array,reducer_function=None):
    """Reducer function is a numpy function to apply to the array extracted from image
    Examples: np.unique (default),np.mean,np.max,np.min."""
    if reducer_function is None:
        reducer_function = np.unique
    # Get image filehandle, band, and geotrans
    im_fh = gdal.Open(image_path)
    im_band = im_fh.GetRasterBand(1)
    im_geotrans = im_fh.GetGeoTransform()
    im_rastersize = [im_fh.RasterXSize,im_fh.RasterYSize]
    output_list = [reducer_function(buffer_extract_point(coords_array[i,:],im_band,im_geotrans,meters_to_dd(buffer_radius,coords_array[i,1]),im_rastersize)) for i in range(0,coords_array.shape[0])]
    return(output_list)


def check_delete(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
    return()


def find_utm_zone(lon):
    """Find approximate utm zone given longitude"""
    return(int(math.floor((lon+180)/6) + 1))


def get_indices(coords,geotrans):
    """Given the points, find the lookup indices in the image array"""
    x_indices,y_indices = (((coords[:,0]-geotrans[0])/geotrans[1]).astype(int),
                           ((coords[:,1]-geotrans[3])/geotrans[5]).astype(int))
    return(y_indices,x_indices)


def build_3x3_vrt(tile_id,type_string,pad):
    combined_vrt = temp_dir + "/tiled_" + type_string + ".vrt"
    check_delete(combined_vrt)
    lat_deg = int(tile_id[0:2])*dir_dict[tile_id[2]]
    lon_deg = int(tile_id[4:7])*dir_dict[tile_id[7]]
    new_lats = np.array([-10,0,10]) + lat_deg
    new_lons = np.array([-10,0,10]) + lon_deg
    new_lats_dirs = [str(abs(x)).zfill(2)+lat_dir_dict[x>=0] for x in new_lats]
    new_lon_dirs = [str(abs(x)).zfill(3) + lon_dir_dict[x>=0] for x in new_lons]
    tile_ids_list = [x + "_" + y for y in new_lon_dirs for x in new_lats_dirs]
    full_paths_list = [hansen_dir + "/" +  type_string + "/Hansen_" +
                       type_string + "_" + tid + ".tif"for tid in tile_ids_list]
    subprocess.call(['gdalbuildvrt','-te',str(lon_deg-pad),str(lat_deg-10-pad),str(lon_deg+10+pad),str(lat_deg+pad),
                     combined_vrt] + full_paths_list)
    return(combined_vrt)


def prep_loss_gain(type_string,utm_zone,tile_id,dist):
    # File Paths
    in_tif = "/Hansen/" + type_string + "/Hansen_" + type_string + "_" + tile_id + ".tif"
    temp_vrt = build_3x3_vrt(tile_id,type_string,lossgain_padding)
    warp_tif = temp_dir + "/warp_" + type_string + ".tif"
    prox_tif = temp_dir + "/prox_" + type_string + ".tif"
    check_delete(warp_tif)
    check_delete(prox_tif)
    # Warp
    subprocess.call(['gdalwarp','--config','GDAL_CACHEMAX','1000','-wm','1000','-co','COMPRESS=LZW','-tr','100','100','-srcnodata','0','-r','average',
                     '-t_srs','+proj=utm +zone='+str(utm_zone)+' +datum=WGS84','-overwrite',temp_vrt,warp_tif])
    # Prox
    subprocess.call(['gdal_proximity.py',warp_tif,prox_tif,'-nodata','32767','-distunits','GEO','-ot','Int16','-maxdist',str(dist)])
    return(warp_tif,prox_tif)


def check_valid_indices(y_indices,x_indices,y_size,x_size):
    on_border_list = (((y_size - y_indices) <= 1) + ((x_size - x_indices) <= 1)
                      + (y_indices<=0) + (x_indices<=0))
    return(on_border_list > 0)


def proximity_extracts(glas_df):
    # A whole bunch of filepaths
    raster_roads = temp_dir + "/raster_roads.tif"
    warp_roads = temp_dir + "/warp_roads.tif"

    ### Prep coordinates ###
    # Get corner coords from full raster
    sample_tif = hansen_dir + "/gain/Hansen_gain_" + tile_id + ".tif"
    full_geotrans = gdal.Open(sample_tif).GetGeoTransform()
    full_xmin = full_geotrans[0]
    full_ymax = full_geotrans[3]

    # Find UTM
    utm_zone = find_utm_zone(full_xmin + 5)

    glas_coords = glas_df.as_matrix(['LON','LAT'])
    myProj = Proj("+proj=utm +zone="+str(utm_zone)+"+datum=WGS84")
    glas_coords_utm_y,glas_coords_utm_x = myProj(glas_coords[:,0],glas_coords[:,1])
    glas_coords_utm = np.column_stack([glas_coords_utm_y,glas_coords_utm_x])

    ### Loss Year and Forest Gain ###
    for type_string in ['lossyear','gain']:
        # Prep
        (warp_tif,prox_tif) = prep_loss_gain(type_string,utm_zone,tile_id,lossgain_dist)
        # Extract
        file_handle = gdal.Open(prox_tif)
        im_array = file_handle.GetRasterBand(1).ReadAsArray()
        geotrans = file_handle.GetGeoTransform()
        y_indices, x_indices = get_indices(glas_coords_utm,geotrans)
        vals = im_array[y_indices, x_indices]
        glas_df[type_string] = vals
        del im_array
        del vals
        del file_handle

    ### Roads ###
    # First need to delete a few temporary files if they exist
    check_delete(raster_roads)
    # Rasterize roads
    subprocess.call(['gdal_rasterize','-burn','1','-tr','.001','.001','-te',str(full_xmin-0.6),str(full_ymax-10.6),str(full_xmin+10.6),str(full_ymax+0.6),
                     '-ot','Byte','-co','COMPRESS=LZW',in_roads,raster_roads])
    # Warp to UTM
    subprocess.call(['gdalwarp','--config','GDAL_CACHEMAX','1000','-wm','1000','-co','COMPRESS=LZW','-tr','100','100','-srcnodata','0','-r','average','-t_srs',
                     '+proj=utm +zone='+str(utm_zone)+' +datum=WGS84','-overwrite',raster_roads,warp_roads])

    # First get a list for exact roads
    file_handle = gdal.Open(warp_roads)
    exact_rd_array = file_handle.GetRasterBand(1).ReadAsArray()
    geotrans = file_handle.GetGeoTransform()
    y_indices, x_indices = get_indices(glas_coords_utm,geotrans)
    exact_rd = exact_rd_array[y_indices, x_indices]

    # For each distance, check if glas shots within buffer
    for d in rd_dist_list:
        prox_path = temp_dir + "/prox_roads" + str(d) + "k.tif"
        check_delete(prox_path) # delete if already exists
        subprocess.call(['gdal_proximity.py',warp_roads,prox_path,'-nodata','0','-distunits','GEO','-ot','Byte','-co','COMPRESS=LZW','-maxdist',str(d*1000),'-fixed-buf-val','1'])
        file_handle = gdal.Open(prox_path)
        rd_array = file_handle.GetRasterBand(1).ReadAsArray()
        geotrans = file_handle.GetGeoTransform()
        y_indices, x_indices = get_indices(glas_coords_utm,geotrans)
        rd = rd_array[y_indices, x_indices]
        rd[np.where(rd==255)]=0
        glas_df['roads' + str(d) + "k"] = (rd + exact_rd)
        del rd_array
    del file_handle
    del exact_rd_array


    return(glas_df)


def footprint_extracts(glas_df):
    ### Get coords
    glas_coords = glas_df.as_matrix(['LON','LAT'])

    ### Treecover
    #Build vrt
    tc_image = build_3x3_vrt(cur_tile_id,'treecover2000',vrt_padding,temp_dir)
    #Extract
    tc_list = extract_hansen(tc_image,glas_coords,reducer_function=np.max)
    glas_df['treecover2000_pymax'] = tc_list
    tc_mean_list = extract_hansen_footprint(tc_image,glas_coords,reducer_function=np.mean)
    glas_df['treecover2000_pymean'] = tc_mean_list

    ### Gain
    #Build vrt
    gain_image = build_3x3_vrt(cur_tile_id,'gain',vrt_padding,temp_dir)
    #Extract
    gain_list = extract_hansen_footprint(gain_image,glas_coords,reducer_function=np.max)
    glas_df['gain_pymax'] = gain_list

    ### Loss year
    # Build vrt
    lossyear_image = build_3x3_vrt(cur_tile_id,'lossyear',vrt_padding,temp_dir)
    #Extract
    lossyear_list = extract_hansen_footprint(lossyear_image,glas_coords,reducer_function=np.unique)
    glas_df['lossyear_pyunique'] = lossyear_list

    ### Water
    # Build vrt
    water_image = build_3x3_vrt(cur_tile_id,'datamask',vrt_padding,temp_dir)
    #Extract
    water_list = extract_hansen_footprint(water_image,glas_coords,reducer_function=np.unique)
    glas_df['datamask_pyunique'] = water_list

    return(glas_df)


def main():
    # Read csv
    glas_df = pd.read_csv(in_csv_path)
    # Get coords and convert to utm
    if not 'LAT' in glas_df.columns:
        glas_df = glas_df.rename(index=str,columns={'LAT.x':'LAT','LON.x':'LON'})

    # Run extracts
    glas_df = proximity_extracts(glas_df)
    glas_df = footprint_extracts(glas_df)


    # Write CSV
    glas_df.to_csv(out_csv_path,header=True,mode='w',index=False)

    return

if __name__ == '__main__':
    main()

