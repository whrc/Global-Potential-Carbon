# Example of how to summarize results in Table 1 (Walker et al. 2022) from primary zonal stats table.

library(dplyr)
library(tidyr)

df <- read.csv('Global_Carbon_Summary_Table.csv')

# baseline climate, unconstrained
df %>%
	select(agb_cur_mgc,agb_pot_mgc,agb_unr_mgc,bgb_cur_mgc,bgb_pot_mgc,bgb_unr_mgc,bio_cur_mgc,bio_pot_mgc,bio_unr_mgc,soc_cur_mgc,soc_pot_mgc,soc_unr_mgc,tot_cur_mgc,tot_pot_mgc,tot_unr_mgc) %>%
	summarize_all(sum) %>%
	mutate_all(.funs = function(x){round(x/1e9, 1)}) %>%
	pivot_longer(everything(), names_to = c('.value','type'), names_pattern = '(.+)_(.+)_mgc') %>%
	as.data.frame()

# baseline climate, constrained
df %>%
	filter(is.na(cons_code)) %>%
	select(agb_unr_mgc,bgb_unr_mgc,bio_unr_mgc,soc_unr_mgc,tot_unr_mgc) %>%
	summarize_all(sum) %>%
	mutate_all(.funs = function(x){round(x/1e9, 1)}) %>%
	pivot_longer(everything(), names_to = c('.value','type'), names_pattern = '(.+)_(.+)_mgc') %>%
	as.data.frame()

# future climate, unconstrained
df %>%
	select(contains('_fc_')) %>%
	summarize_all(sum) %>%
	mutate_all(.funs = function(x){x/1e9}) %>%
	pivot_longer(everything(), names_to = c('.value','type','.value'), names_pattern = '(.+)_(.+)_fc_(.+)_mgc') %>%
	rowwise() %>%
	mutate(agb_min = min(agbbc,agbcc,agbgs,agbhd,agbhe,agbip,agbmc,agbmg,agbmi,agbmr,agbno),
		   agb_max = max(agbbc,agbcc,agbgs,agbhd,agbhe,agbip,agbmc,agbmg,agbmi,agbmr,agbno),
		   bgb_min = min(bgbbc,bgbcc,bgbgs,bgbhd,bgbhe,bgbip,bgbmc,bgbmg,bgbmi,bgbmr,bgbno),
		   bgb_max = max(bgbbc,bgbcc,bgbgs,bgbhd,bgbhe,bgbip,bgbmc,bgbmg,bgbmi,bgbmr,bgbno),
		   biomean = agbmean + bgbmean,
		   bio_min = agb_min + bgb_min,
		   bio_max = agb_max + bgb_max,
		   agb = paste0(round(agbmean, 1), ' (', round(agb_min), '-', round(agb_max), ')'),
		   bgb = paste0(round(bgbmean, 1), ' (', round(bgb_min), '-', round(bgb_max), ')'),
		   bio = paste0(round(biomean, 1), ' (', round(bio_min), '-', round(bio_max), ')')) %>%
	select(type, agb, bgb, bio) %>%
	as.data.frame()

# future climate, constrained
df %>%
	filter(is.na(cons_code)) %>%
	select(contains('_unr_fc_')) %>%
	summarize_all(sum) %>%
	mutate_all(.funs = function(x){x/1e9}) %>%
	pivot_longer(everything(), names_to = c('.value','type','.value'), names_pattern = '(.+)_(.+)_fc_(.+)_mgc') %>%
	rowwise() %>%
	mutate(agb_min = min(agbbc,agbcc,agbgs,agbhd,agbhe,agbip,agbmc,agbmg,agbmi,agbmr,agbno),
		   agb_max = max(agbbc,agbcc,agbgs,agbhd,agbhe,agbip,agbmc,agbmg,agbmi,agbmr,agbno),
		   bgb_min = min(bgbbc,bgbcc,bgbgs,bgbhd,bgbhe,bgbip,bgbmc,bgbmg,bgbmi,bgbmr,bgbno),
		   bgb_max = max(bgbbc,bgbcc,bgbgs,bgbhd,bgbhe,bgbip,bgbmc,bgbmg,bgbmi,bgbmr,bgbno),
		   biomean = agbmean + bgbmean,
		   bio_min = agb_min + bgb_min,
		   bio_max = agb_max + bgb_max,
		   agb = paste0(round(agbmean, 1), ' (', round(agb_min), '-', round(agb_max), ')'),
		   bgb = paste0(round(bgbmean, 1), ' (', round(bgb_min), '-', round(bgb_max), ')'),
		   bio = paste0(round(biomean, 1), ' (', round(bio_min), '-', round(bio_max), ')')) %>%
	select(type, agb, bgb, bio) %>%
	as.data.frame()

