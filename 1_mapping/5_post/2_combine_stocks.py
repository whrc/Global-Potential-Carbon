#!/usr/bin/env python3

# combines biomass (AGB+BGB) and all (AGB+BGB+SOC) rasters

import sys, os
from rasters import *

def compute_biomass_total(agb_tif, bgb_tif):
	agb_img = r2n(agb_tif)
	bgb_img = r2n(bgb_tif)
	agb_nd = get_nodata(agb_tif)
	bgb_nd = get_nodata(bgb_tif)
	agb_img[agb_img == agb_nd] = 0
	bgb_img[bgb_img == bgb_nd] = 0
	bio_img = agb_img + bgb_img
	del agb_img
	del bgb_img
	return bio_img

def compute_total(agb_tif, bgb_tif, soc_tif):
	agb_img = r2n(agb_tif)
	bgb_img = r2n(bgb_tif)
	soc_img = r2n(soc_tif)
	agb_nd = get_nodata(agb_tif)
	bgb_nd = get_nodata(bgb_tif)
	soc_nd = get_nodata(soc_tif)
	agb_img[agb_img == agb_nd] = 0
	bgb_img[bgb_img == bgb_nd] = 0
	soc_img[soc_img == soc_nd] = 0
	tot_img = agb_img + bgb_img + soc_img
	del agb_img
	del bgb_img
	del soc_img
	return tot_img

def main():

	# - - - - -
	# inputs
	# - - - - -

	agb_cur = 'global_actual_biomass_2016_v6_blend_a95_f03_w75_clp.tif'
	agb_pot = 'global_potential_biomass_v6_blend_ndm_clp_adj.tif'
	agb_unr = 'global_unrealized_2016_AGB_Mgha_adj.tif'

	bgb_cur = 'global_actual_2016_BGB_Mgha.tif'
	bgb_pot = 'global_potential_BGB_Mgha_adj.tif'
	bgb_unr = 'global_unrealized_2016_BGB_Mgha_adj.tif'

	soc_cur = 'SOCS_0_200cm_year_2010AD_500m_Mgha_wm.tif'
	soc_pot = 'SOCS_0_200cm_year_NoLU_500m_Mgha_wm_adj.tif'
	soc_unr = 'SOCS_0_200cm_unrealized_500m_Mgha_wm_adj.tif'

	gt, sr = get_gt_sr(agb_cur)

	# - - - - -
	# outputs
	# - - - - -

	bio_cur = 'Current_AGC_BGC_mgha_500m.tif'
	bio_pot = 'Potential_AGC_BGC_mgha_500m.tif'
	bio_unr = 'Unrealized_AGC_BGC_mgha_500m.tif'

	tot_cur = 'Current_AGC_BGC_SOC_mgha_500m.tif'
	tot_pot = 'Potential_AGC_BGC_SOC_mgha_500m.tif'
	tot_unr = 'Unrealized_AGC_BGC_SOC_mgha_500m.tif'

	# - - - - - - - - - - - - - - - - - - - - - - - - - -
	# combine AGB and BGB
	# - - - - - - - - - - - - - - - - - - - - - - - - - -

	cur_bio_tifs = [agb_cur, bgb_cur, bio_cur]
	pot_bio_tifs = [agb_pot, bgb_pot, bio_pot]
	unr_bio_tifs = [agb_unr, bgb_unr, bio_unr]
	bio_input_tifs = [cur_bio_tifs, pot_bio_tifs, unr_bio_tifs]

	for i in range(len(bio_input_tifs)):
		agb_tif, bgb_tif, bio_tif = bio_input_tifs[i]
		bio_img = compute_biomass_total(agb_tif, bgb_tif)
		write_gtiff(bio_img, bio_tif, dtype = 'Int16', gt = gt, sr = sr, nodata = 0)

	# - - - - - - - - - - - - - - - - - - - - - - - - - -
	# combine AGB, BGB, and SOC
	# - - - - - - - - - - - - - - - - - - - - - - - - - -

	cur_tot_tifs = [agb_cur, bgb_cur, soc_cur, tot_cur]
	pot_tot_tifs = [agb_pot, bgb_pot, soc_pot, tot_pot]
	unr_tot_tifs = [agb_unr, bgb_unr, soc_unr, tot_unr]
	tot_input_tifs = [cur_tot_tifs, pot_tot_tifs, unr_tot_tifs]

	for i in range(len(tot_input_tifs)):
		agb_tif, bgb_tif, soc_tif, tot_tif = tot_input_tifs[i]
		tot_img = compute_total(agb_tif, bgb_tif, soc_tif)
		write_gtiff(tot_img, tot_tif, dtype = 'Int16', gt = gt, sr = sr, nodata = 0)

if __name__ == "__main__":
	main()

