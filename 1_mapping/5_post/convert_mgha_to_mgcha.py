#!/usr/bin/env python3

bio = raster()
crb = np.copy(bio)
crb[crb > 0] = np.rint(np.true_divide(bio[bio > 0], 2)).astype(np.int16)
