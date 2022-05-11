// -----------------------------------------------------------------------------------------------
//
// Purpose:
//  Create a global mosaic of the GFSAD30 regions downsampled to the 500m sinusoidal projection.
//
// Notes:
//  1. This script is intended to be run in Google Earth Engine, i.e.:
//     https://code.earthengine.google.com/503c213063ee52fa286d28f7942b5c97
//  2. The GFSAD30 GEE image assets that are loaded into this script were originally downloaded
//     from https://croplands.org/downloadLPDAAC and ingested into GEE by Seth Gorelik. The only
//     modification made to the original GeoTIFFs was to remove the NoData value (256) before
//     uplodaing them to GEE.
//  3. In GEE, Parts 1 and 2 of this script are intended to be run separately.
//
// -----------------------------------------------------------------------------------------------
// Part 1: Create a global 30m mosaic of cropland, saved to a GEE image asset
// -----------------------------------------------------------------------------------------------

var basemap = require('users/sgorelik/modules:visualization/basemaps');
Map.setOptions('Dark', {'Dark': basemap.BASE_DARK});

// create global cropland mosaic using max value (cropland) from each overlapping region:
//  0 = water
//  1 = non-cropland land
//  2 = cropland
var crop_mosaic_30m = ee.ImageCollection([
  ee.Image("users/sgorelik/GFSAD30/GFSAD30_AFCE"),
  ee.Image("users/sgorelik/GFSAD30/GFSAD30_AUNZCNMOCE"),
  ee.Image("users/sgorelik/GFSAD30/GFSAD30_EUCEARUMECE"),
  ee.Image("users/sgorelik/GFSAD30/GFSAD30_NACE"),
  ee.Image("users/sgorelik/GFSAD30/GFSAD30_SAAFGIRCE"),
  ee.Image("users/sgorelik/GFSAD30/GFSAD30_SACE"),
  ee.Image("users/sgorelik/GFSAD30/GFSAD30_SEACE")
]).max().unmask(0);

Map.addLayer(crop_mosaic_30m, {min: 0, max: 2, palette: ['grey','black','green']}, 'GFSAD30 mosaic', false);

// convert mosaic to mask so that:
//  0 = non-cropland (land or water)
//  1 = cropland
var crop_mask_30m = crop_mosaic_30m.eq(2);

// mask out all non-cropland pixels
crop_mask_30m = crop_mask_30m
  .updateMask(crop_mask_30m)
  .rename('cropland_mask');

Map.addLayer(crop_mask_30m, {min: 0, max: 1, palette: ['black','green']}, 'Cropland mask 30m', true);

// create export region geometry (see: https://groups.google.com/d/msg/google-earth-engine-developers/xc7f10FOM0k/ze2OTS2bCQAJ)
var geom = ee.Geometry.Polygon([-180, 88, 0, 88, 180, 88, 180, -88, 0, -88, -180, -88], null, false);

// export the 30m cropland mosaic to an Earth Engine image asset
Export.image.toAsset({
  image: crop_mask_30m,
  description: 'GFSAD30_global_cropland_mask',
  assetId: 'GFSAD30/GFSAD30_global_cropland_mask',
  region: geom,
  scale: 30,
  pyramidingPolicy: {'cropland_mask': 'mode'},
  crs: "EPSG:4326",
  maxPixels: 1e13
});


// -----------------------------------------------------------------------------------------------
// Part 2: Create a global 500m mosaic of cropland, exported to cloud storage
// -----------------------------------------------------------------------------------------------

// import 30m asset for aggregation step, rather than aggregating to 500m from the "virtual" 30m mosaic
var crop_mask_30m_asset = ee.Image("users/sgorelik/GFSAD30/GFSAD30_global_cropland_mask");

// aggregate pixels from 30m to 500m
var crop_mask_500m = crop_mask_30m_asset
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

Map.addLayer(crop_mask_500m, {min: 0, max: 1, palette: ['black','blue']}, 'Cropland mask 500m', true);

// force 500m export to match WHRC biomass image dimensions
Export.image.toAsset({
  image: crop_mask_500m,
  description: 'Asset-GFSAD500_global_cropland_mask',
  assetId: 'GFSAD30/GFSAD500_global_cropland_mask',
  pyramidingPolicy: {'cropland_mask': 'mode'},
  crs: 'SR-ORG:6974',
  crsTransform: [463.3127165275, 0, -20015109.354096, 0, -463.3127165275, 10007554.677048],
  dimensions: '86400x36000',
  maxPixels: 86400*36000
});

Export.image.toCloudStorage({
  image: crop_mask_500m,
  description: 'GSB-GFSAD500_global_cropland_mask',
  bucket: 'sgwhrc',
  fileNamePrefix: 'GFSAD30/GFSAD500_global_cropland_mask',
  crs: 'SR-ORG:6974',
  crsTransform: [463.31271653, 0, -20015109.354096, 0, -463.31271653, 10007554.677048],
  dimensions: '86400x36000',
  maxPixels: 86400*36000,
});


/* */