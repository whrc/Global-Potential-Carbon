#!/usr/bin/env python3
# # -*- coding: utf-8 -*-
"""Downloads and prepares set of future WorldClim data, meaning one year/model/rcp.
"""

from __future__ import print_function
import os
import urllib.request
import zipfile
import numpy as np
import subprocess as sp
import errno
import re
import argparse
import tempfile
import multiprocessing as mp
import shutil

# List of WorldClim variables to download.
VAR_LIST = ['tmin', 'tmax', 'prec', 'bio']

class WorldClimRetrieval(object):
    """Base class for WorldClim data retrieval.

    Attributes:
        year (int): 0, 50, or 70. Current is 0, others are CMIP5 projection
            outputs for 2050 or 2070.
        cmip_gcm (str): CMIP5 GCM two letter code.
            See list: http://www.worldclim.org/cmip5_30s
        rcp (int): 26, 45, 60, or 85. Codes for RCP scenarios. See above link.
        var (str): Variable name from 'tmin', 'tmax', 'tavg', 'prec', and 'bio'.
        dest_dir (str): Destination directory for saving files.
            Must already exist.
        gcs_dest_dir (str): Destination directory on Google Cloud Storage. If
            None, will keep local file and not copy to cloud storage.
            Default is None.

    """
    def __init__(self, year, var, cmip_gcm=None, rcp=None,
                 dest_dir='./', gcs_dest_dir=None):
        self.year = year
        self.var = var
        self.cmip_gcm = cmip_gcm
        self.rcp = rcp

        if dest_dir[-1] != '/':
            dest_dir += '/'
        self.dest_dir = dest_dir

        if gcs_dest_dir is not None and gcs_dest_dir[-1] != '/':
            gcs_dest_dir += '/'
        self.gcs_dest_dir = gcs_dest_dir

    @property
    def raster_ext(self):
        """Raster files are .bil for current, .tif for future."""
        if self.year == 0:
            raster_ext = '.bil'
        else:
            raster_ext = '.tif'

        return raster_ext

    @property
    def url_prefix(self):
        """Find url prefixes needed for downloading from WorldClim server"""
        # Current vs CMIP5 data are hosted differently.
        if self.year == 0: # Current climate
            url_prefix = 'http://biogeo.ucdavis.edu/data/climate/worldclim/1_4/grid/cur/'

        else: # Future climate
            url_prefix = 'http://biogeo.ucdavis.edu/data/climate/cmip5/30s/'

        return url_prefix

    @property
    def zip_filenames(self):
        """Get filenames for zip files."""
        if self.year == 0: # Current climate
            rename_dict = {'bio': ['bio1-9', 'bio10-19'],
                            'tavg': ['tmean']}
            var_corrected = [v for v in rename_dict.get(self.var, [self.var])]
            zip_filenames = ['{}_30s_bil.zip'.format(var)
                             for var in var_corrected]

        else: # Future climate
            rename_dict = {'bio': ['bi'], 'tavg': [], 'prec': ['pr'],
                           'tmax': ['tx'], 'tmin': ['tn']}
            var_corrected = [v for v in rename_dict.get(self.var, [self.var])]
            zip_filenames = ['{}{}{}{}.zip'.format(self.cmip_gcm, self.rcp,
                                                   vc, self.year)
                             for vc in var_corrected]

        return zip_filenames

    @property
    def zip_locations(self):
        """Dict of URLs and matching local paths."""
        zip_locations = {}
        for zf in self.zip_filenames:
            remote_zip = '{}{}'.format(self.url_prefix, zf)
            local_zip = '{}{}'.format(self.dest_dir, zf)
            zip_locations[remote_zip] = local_zip

        return zip_locations

    def download(self):
        """Download zips from WorldClim server."""
        for remote_zip in self.zip_locations.keys():
            local_zip = self.zip_locations[remote_zip]
            print('Downloading {}'.format(remote_zip), flush=True)
            urllib.request.urlretrieve(remote_zip, filename = local_zip)

        return

    def get_zip_contents(self):
        """Get the contents of the zip files."""
        self.zip_contents = {}
        for zip_f in self.zip_locations.values():
            zip_ref = zipfile.ZipFile(zip_f, 'r')
            for zip_c in zip_ref.namelist():
                self.zip_contents[zip_c] = zip_f

        return

    def _unzip_raster(self, zipped_raster):
        """Unzip a single file from."""
        zip_f = self.zip_contents[zipped_raster]
        zip_ref = zipfile.ZipFile(zip_f, 'r')
        unzipped_raster = zip_ref.extract(zipped_raster, path = self.dest_dir)

        return unzipped_raster

    def _prep_raster(self, input_raster):
        """Convert raster to int16 to save some time in the padding portion."""
        output_raster = input_raster.replace(self.raster_ext, '_prep.tif')
        sp.call([
            'gdal_translate', '-ot', 'Int16', '-co', 'COMPRESS=LZW',
            input_raster, output_raster])

        return output_raster

    def _pad_raster(self, input_raster):
        """Pad a single raster using gdal_fillnodata."""
        output_raster = input_raster.replace(self.raster_ext, '_pad.tif')
        sp.call(['gdal_fillnodata.py', '-md', '4', '-si', '0', '-of', 'GTiff',
                 '-co', 'COMPRESS=LZW', input_raster, output_raster])

        return output_raster

    def _polish_raster(self, input_raster):
        """gdal_fillnodata outputs a raster that it is larger than expected.
        Recompressing it solves the problem. Also need to change NA value."""
        output_raster = input_raster.replace(self.raster_ext, '_final.tif')
        sp.call([
            'gdal_calc.py', '-A', input_raster,
            '--calc=-32768*(A==-9999) + A*(A!=-9999)',
            '--NoDataValue=-32768',
            '--outfile={}'.format(output_raster),
            '--type=Int16', '--co=COMPRESS=LZW'])

        return output_raster

    def _generate_output_name(self, initial_name):
        """Rename raster to standard format, e.g. prec_4.tif.

        Args:
            initial_name (str): Raster file name from zip.

        Notes:
            Needs to extract the subvar_id, which is 1-12 for most (months)
            or 1-19 for bio. Does this by using regex to extract the number
            between the year and the file extension.

        """
        regex_result = re.search('{}(.*){}'.format(self.year, self.raster_ext),
                                 initial_name)
        try:
            subvar_id = regex_result.group(1)
        except:
            raise ValueError(
                'Unable to extract subvariable index from original filename.')

        output_file = '{}_{}.tif'.format(self.var, subvar_id)

        return output_file

    def process_subvar_raster(self, target_raster, cleanup=True):
        """Fully processes single variable (e.g. tmin_1)."""
        unzipped_r = self._unzip_raster(target_raster)
        prepped_r = self._prep_raster(unzipped_r)
        padded_r = self._pad_raster(prepped_r)
        final_r_badname = self._polish_raster(padded_r)

        # Rename file
        final_r_base = self._generate_output_name(os.path.basename(unzipped_r))
        final_r = '{}{}'.format(self.dest_dir, final_r_base)
        os.rename(final_r_badname, final_r)


        if self.gcs_dest_dir is None:
            delete_files = [unzipped_r, prepped_r, padded_r]
            output_path = final_r
        else:
            sp.call(['gsutil', 'cp', final_r, self.gcs_dest_dir])
            delete_files = [unzipped_r, prepped_r, padded_r, final_r]
            output_path = '{}{}'.format(self.gcs_dest_dir,
                                        os.path.basename(final_r))

        if cleanup:
            for del_f in delete_files:
                os.remove(del_f)

        return output_path

    def cleanup_all(self):
        delete_files = [self.zip_locations.values()]
        # Delete files
        for del_f in delete_files:
            os.remove(del_f)


def argparse_init():
    """Prepare ArgumentParser for inputs"""
    p = argparse.ArgumentParser(
        description='Download WorldClim files and run basic prep',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument(
        'year',
        help='WorldClim year (0, 50, or 70)',
        type=int)
    p.add_argument(
        'gcm',
        help=('2-letter GCM code, lower case. '
              'See: http://www.worldclim.org/cmip5_30s'),
        type=str)
    p.add_argument(
        'rcp',
        help='2-digit RCP code (26, 45, 60, or 85).',
        type=str)
    p.add_argument(
        'gcs_dest_dir',
        help='Google Cloud Storage destination directory',
        type=str)

    return p


def main():
    # Prep argparse
    parser = argparse_init()
    args = parser.parse_args()

    tmpdir = tempfile.mkdtemp()

    # Set up parallelization
    pool = mp.Pool(mp.cpu_count() - 1)

    for var in VAR_LIST:

        wcr = wc_prep.WorldClimRetrieval(
            year=args.year,
            cmip_gcm=args.gcm,
            rcp=args.rcp,
            var=var,
            dest_dir=tmpdir,
            gcs_dest_dir=args.gcs_dest_dir)

        # Download zip file
        wcr.download()
        wcr.get_zip_contents()

        for subvar in wcr.zip_contents:
            # Add processing function to queue
            pool.apply_async(
                wcr.process_subvar_raster,
                (subvar,))

    pool.close()
    pool.join()

    shutil.rmtree(tmpdir)

    return

if __name__ == '__main__':
    main()
