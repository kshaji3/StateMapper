#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd 
import geopandas as gpd
import os 
import sys 

# Stop getting the GDAL data files warning:
os.environ['GDAL_DATA'] = os.path.join(f'{os.sep}'.join(sys.executable.split(os.sep)[:-1]), 'Library', 'share', 'gdal')

# File dependencies
CURR_LIST_FILE = pd.read_excel('StateList.xlsx')
GIS_FOLDER = 'cb_2014_us_state_500k'
GIS_DATA = 'cb_2014_us_state_500k.shp'

# Categories:
CATS = ['Both People Went', 
        'Only Person 1 Went', 
        'Only Person 2 Went', 
        'Neither Person Went']
NUM_CLASSES = 4

# Non-States (will need to prune them out)
NON_STATES = ['Puerto Rico', 
              'American Samoa', 
              'Commonwealth of the Northern Mariana Islands',
              'District of Columbia',
              'United States Virgin Islands',
              'Guam']

person1 = CURR_LIST_FILE['Person 1']
person2 = CURR_LIST_FILE['Person 2']
states_list = CURR_LIST_FILE['State']
p1_bool = np.full((len(states_list), 1), False)
p2_bool = np.full((len(states_list), 1), False)

# Convert the sets of "yes" and "no" to a boolean mapping
# 4 Possible Options
state_cats = []
for i in range(len(states_list)):
    if (person1[i].lower() == 'y'):
        p1_bool[i] = True
    if (person2[i].lower() == 'y'):
        p2_bool[i] = True 
    
    # Now fill in the map of yesses and nos:
    if p1_bool[i]:
        if (p2_bool[i]):
            state_cats.append(CATS[0])
        else:
            state_cats.append(CATS[1])
    else:
        if p2_bool[i]:
            state_cats.append(CATS[2])
        else:
            state_cats.append(CATS[3])
            

# Load and process the GIS file path
gis_fp = os.path.join(GIS_FOLDER, GIS_DATA)
wgs_states = gpd.read_file(gis_fp)

# Convert to Mercator:
# EPSG:4326 = WGS84, EPSG:3395 = Mercator
# EPSG:32633 = UTM Zones (N), EPS:32733 = UTM Zones (S)
merc_states = wgs_states.to_crs("EPSG:3395")

# Sort in ascending order
merc_states = merc_states.sort_values(by=['NAME'])

# Remove the territories
merc_states = merc_states.loc[~merc_states["NAME"].isin(NON_STATES)]

fig1, ax1 = plt.subplots(figsize=(24,16))
merc_states['state_cats'] = state_cats
color_steps = plt.colormaps['tab20'].resampled(NUM_CLASSES)
merc_states.plot(column='state_cats', cmap = color_steps, 
                 legend=True, 
                            legend_kwds={'loc':'lower left', 
                        'bbox_to_anchor':(0, .2), 
                        'markerscale':1.29, 
                        'title_fontsize':'medium', 
                        'fontsize':'small'}, 
                        ax=ax1)
merc_states.boundary.plot(ax=ax1, color='black')
plt.xlim(-2.05E7, -0.65E7)
plt.show()
