//
// Purpose:
//  Create a global mosaic of the GFSAD30 regions downsampled to the 500m sinusoidal projection
//
// Notes:
//  1. Intended to be run in Google Earth Engine Code Editor
//  2. GFSAD30 regions were downloaded from https://croplands.org/downloadLPDAAC and ingested into GEE.
//     The only modification made to the original GeoTIFFs was to remove the NoData value (256) before
//     uplodaing them to GEE assets.
//

var usr = 'SOMEUSER';

// create global cropland mosaic using max value (cropland) from each overlapping region:
//  0 = water
//  1 = non-cropland land
//  2 = cropland
var crop_mosaic_30m = ee.ImageCollection([
  ee.Image('users/'+usr+'/GFSAD30/GFSAD30_AFCE'),
  ee.Image('users/'+usr+'/GFSAD30/GFSAD30_AUNZCNMOCE'),
  ee.Image('users/'+usr+'/GFSAD30/GFSAD30_EUCEARUMECE'),
  ee.Image('users/'+usr+'/GFSAD30/GFSAD30_NACE'),
  ee.Image('users/'+usr+'/GFSAD30/GFSAD30_SAAFGIRCE'),
  ee.Image('users/'+usr+'/GFSAD30/GFSAD30_SACE'),
  ee.Image('users/'+usr+'/GFSAD30/GFSAD30_SEACE')
]).max().unmask(0);

// convert mosaic to mask so that:
//  0 = non-cropland (land or water)
//  1 = cropland
var crop_mask_30m = crop_mosaic_30m.eq(2);

// aggregate pixels from 30m to 500m sinusoidal
var crop_mask_500m = crop_mask_30m
  .unmask(0)
  .reproject({
    crs: 'SR-ORG:6974',
    scale: 27.829872698318393
  })
  .reduceResolution({
    reducer: ee.Reducer.mode(),
    bestEffort: false,
    maxPixels: 300
  })
  .reproject({
    crs: 'SR-ORG:6974',
    scale: 463.3127165275
  })
  .round().uint8();

// mask out all non-cropland pixels
crop_mask_500m = crop_mask_500m
  .updateMask(crop_mask_500m)
  .rename('cropland_mask');

// export, matching AGB dimensions and projection
Export.image.toCloudStorage({
  image: crop_mask_500m,
  bucket: 'SOMEBUCKET',
  fileNamePrefix: 'GFSAD_crop_mask_500m',
  crs: 'SR-ORG:6974',
  crsTransform: [463.31271653, 0, -20015109.354096, 0, -463.31271653, 10007554.677048],
  dimensions: '86400x36000',
  maxPixels: 86400*36000,
});
