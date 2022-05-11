#!/usr/bin/env Rscript

row.list <- list(
	list(variable = 'bioclim', zonal = 1, file = 'gez_2010_sin500m_LW.tif', description = 'Bioclimate zones', pixel_values = 'codes', code_file = 'bioclims.csv', code_col = 'gez_code', name_col = 'gez_name'),
	list(variable = 'gadm', zonal = 1, file = 'gadm36_0_sin500m.tif', description = 'Countries', pixel_values = 'codes', code_file = 'gadm36.csv', code_col = 'gadm_code', name_col = 'gadm_name'),
	list(variable = 'ncs', zonal = 1, file = 'global_500m_ncs_zones.tif', description = 'NCS activity categories', pixel_values = 'codes', code_file = 'ncs_opp_space.csv', code_col = 'ncs_code', name_col = 'ncs_name'),
	list(variable = 'cons', zonal = 1, file = 'global_constraints_500m.tif', description = 'Constraints', pixel_values = 'codes', code_file = 'constraints.csv', code_col = 'cons_code', name_col = 'cons_name'),

	list(variable = 'agc_cur', zonal = 0, file = 'global_actual_biomass_2016_v6_blend_a95_f03_w75_clp.tif', description = 'current aboveground biomass', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot', zonal = 0, file = 'global_potential_biomass_v6_blend_ndm_clp_adj.tif', description = 'potential aboveground biomass', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr', zonal = 0, file = 'global_unrealized_2016_AGB_Mgha_adj.tif', description = 'unrealized potential aboveground biomass', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),

	list(variable = 'agc_pot_fc_bc', zonal = 0, file = 'future_potential_bc_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 bc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_cc', zonal = 0, file = 'future_potential_cc_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 cc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_gs', zonal = 0, file = 'future_potential_gs_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 gs)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_hd', zonal = 0, file = 'future_potential_hd_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 hd)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_he', zonal = 0, file = 'future_potential_he_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 he)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_ip', zonal = 0, file = 'future_potential_ip_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 ip)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_mc', zonal = 0, file = 'future_potential_mc_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 mc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_mg', zonal = 0, file = 'future_potential_mg_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 mg)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_mi', zonal = 0, file = 'future_potential_mi_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 mi)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_mr', zonal = 0, file = 'future_potential_mr_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 mr)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_no', zonal = 0, file = 'future_potential_no_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 no)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_avg', zonal = 0, file = 'future_potential_mean_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 mean)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_pot_fc_med', zonal = 0, file = 'future_potential_median_rcp85_y50_global_blend_pp_adj.tif', description = 'potential aboveground biomass (rcp8.5 median)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),

	list(variable = 'agc_unr_fc_bc', zonal = 0, file = 'global_unrealized_AGB_fc_bc_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 bc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_cc', zonal = 0, file = 'global_unrealized_AGB_fc_cc_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 cc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_gs', zonal = 0, file = 'global_unrealized_AGB_fc_gs_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 gs)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_hd', zonal = 0, file = 'global_unrealized_AGB_fc_hd_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 hd)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_he', zonal = 0, file = 'global_unrealized_AGB_fc_he_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 he)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_ip', zonal = 0, file = 'global_unrealized_AGB_fc_ip_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 ip)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_mc', zonal = 0, file = 'global_unrealized_AGB_fc_mc_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 mc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_mg', zonal = 0, file = 'global_unrealized_AGB_fc_mg_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 mg)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_mi', zonal = 0, file = 'global_unrealized_AGB_fc_mi_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 mi)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_mr', zonal = 0, file = 'global_unrealized_AGB_fc_mr_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 mr)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_no', zonal = 0, file = 'global_unrealized_AGB_fc_no_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 no)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_avg', zonal = 0, file = 'global_unrealized_AGB_fc_mean_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 mean)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'agc_unr_fc_med', zonal = 0, file = 'global_unrealized_AGB_fc_median_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential aboveground biomass (rcp8.5 median)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),

	list(variable = 'bgc_cur', zonal = 0, file = 'global_actual_2016_BGB_Mgha.tif', description = 'current belowground biomass', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot', zonal = 0, file = 'global_potential_BGB_Mgha_adj.tif', description = 'potential belowground biomass', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr', zonal = 0, file = 'global_unrealized_2016_BGB_Mgha_adj.tif', description = 'unrealized potential belowground biomass', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),

	list(variable = 'bgc_pot_fc_bc', zonal = 0, file = 'global_potential_BGB_fc_bc_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 bc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_cc', zonal = 0, file = 'global_potential_BGB_fc_cc_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 cc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_gs', zonal = 0, file = 'global_potential_BGB_fc_gs_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 gs)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_hd', zonal = 0, file = 'global_potential_BGB_fc_hd_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 hd)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_he', zonal = 0, file = 'global_potential_BGB_fc_he_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 he)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_ip', zonal = 0, file = 'global_potential_BGB_fc_ip_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 ip)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_mc', zonal = 0, file = 'global_potential_BGB_fc_mc_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 mc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_mg', zonal = 0, file = 'global_potential_BGB_fc_mg_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 mg)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_mi', zonal = 0, file = 'global_potential_BGB_fc_mi_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 mi)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_mr', zonal = 0, file = 'global_potential_BGB_fc_mr_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 mr)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_no', zonal = 0, file = 'global_potential_BGB_fc_no_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 no)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_avg', zonal = 0, file = 'global_potential_BGB_fc_mean_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 mean)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_pot_fc_med', zonal = 0, file = 'global_potential_BGB_fc_median_rcp85_y50_Mgha_adj.tif', description = 'potential belowground biomass (rcp8.5 median)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),

	list(variable = 'bgc_unr_fc_bc', zonal = 0, file = 'global_unrealized_BGB_fc_bc_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 bc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_cc', zonal = 0, file = 'global_unrealized_BGB_fc_cc_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 cc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_gs', zonal = 0, file = 'global_unrealized_BGB_fc_gs_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 gs)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_hd', zonal = 0, file = 'global_unrealized_BGB_fc_hd_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 hd)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_he', zonal = 0, file = 'global_unrealized_BGB_fc_he_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 he)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_ip', zonal = 0, file = 'global_unrealized_BGB_fc_ip_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 ip)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_mc', zonal = 0, file = 'global_unrealized_BGB_fc_mc_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 mc)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_mg', zonal = 0, file = 'global_unrealized_BGB_fc_mg_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 mg)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_mi', zonal = 0, file = 'global_unrealized_BGB_fc_mi_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 mi)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_mr', zonal = 0, file = 'global_unrealized_BGB_fc_mr_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 mr)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_no', zonal = 0, file = 'global_unrealized_BGB_fc_no_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 no)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_avg', zonal = 0, file = 'global_unrealized_BGB_fc_mean_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 mean)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'bgc_unr_fc_med', zonal = 0, file = 'global_unrealized_BGB_fc_median_rcp85_y50_Mgha_adj.tif', description = 'unrealized potential belowground biomass (rcp8.5 median)', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),

	list(variable = 'soc_cur', zonal = 0, file = 'SOCS_0_200cm_year_2010AD_500m_Mgha_wm.tif', description = 'current soil organic carbon matter', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'soc_pot', zonal = 0, file = 'SOCS_0_200cm_year_NoLU_500m_Mgha_wm_adj.tif', description = 'potential soil organic carbon matter', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA),
	list(variable = 'soc_unr', zonal = 0, file = 'SOCS_0_200cm_unrealized_500m_Mgha_wm_adj.tif', description = 'unrealized potential soil organic carbon matter', pixel_values = 'MgC/ha', code_file = NA, code_col = NA, name_col = NA)
)

df <- do.call(rbind, lapply(row.list, as.data.frame))

write.csv(df, 'inputs.csv', row.names = F)
