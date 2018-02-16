# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 23:09:17 2018

@author: Nir
"""

from geopy.distance import vincenty
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import glob
import csv

time_format = "%Y-%m-%d %H:%M:%S"
dir_path = "D:/Nir/Downloads/Chrome/T-drive Taxi Trajectories/release/taxi_log_2008_by_id/test/"

def main():
    
    # Retrive all text file names from the directory
    filenames = glob.glob(dir_path + "*.txt")

    lst_data = list()
    for filename in filenames[1:]:
        with open(filename, 'r') as f:
            reader = list()
            [reader.append(row) for row in csv.reader(f) if not reader.count(row)]
            
            time_segments = divide_to_time_segments(reader, 20)
            
            source_dest_comb = list(itertools.combinations(reader, 2))
            
            for comb in source_dest_comb:
                row_features = extract_features(comb[0], comb[1])
                lst_data.append(row_features)
        break
    
    df_data = pd.DataFrame(lst_data, columns=["source_location_lon",
                                            "source_location_lat",
                                            "dest_location_lon",
                                            "dest_location_lat",
                                            "distance",
                                            "duration"])                
                
def divide_to_time_segments(data, maximum_mins):
    segments = list()
    curr_segment = list()
    
    # Divide the data into segments that in each segment, the time between two consecutive rows is less the maximum_mins
    for index, row in enumerate(data[:-1]):
        
        # Hold the current row and the next one to calculate the time between them
        curr_row = row
        next_row = data[index + 1]
        
        # Add the current row to the current segment (it will be a new segment if the previous row was too far from the current row)
        curr_segment.append(curr_row)
        
        # Extract only the duration (in seconds) feature from the two rows
        duration = extract_features(curr_row, next_row, names=["duration"])[0]
        
        # Check if the duration (in minuts) meets the requirements of the maximum_mins.
        # If it does'nt, start a new segment
        if duration / 60.0 > maximum_mins:
            segments.append(curr_segment)
            curr_segment.clear()
        
def extract_features(source, dest, names=None):
    row_features = list()
    
    # Extract source and destination longitude and latitude
    source_location = (source[2], source[3])
    dest_location = (dest[2], dest[3])
    
    # Show the source location only if asked
    if names == None or "source_location" in names:
        row_features.append(source_location[0])
        row_features.append(source_location[1])
    
    # Show the destination location only if asked
    if names == None or "dest_location" in names:
        row_features.append(dest_location[0])
        row_features.append(dest_location[1])
    
    # Show the distance between source and destination only if asked
    if names == None or "distance" in names:
        distance = vincenty(source_location, dest_location).km
        row_features.append(distance)
    
    # Show the duration time in seconds to get from source to destination only if asked
    if names == None or "duration" in names:
        source_time = datetime.strptime(source[1], time_format)
        dest_time = datetime.strptime(dest[1], time_format)
        duration = (dest_time - source_time).total_seconds()
        row_features.append(duration)
    
    return row_features # Add day of week, day of month, month, hour of day
            
if "__main__" == __name__:
    main()            

#geolocator = GoogleV3()
#location = geolocator.reverse(latlon, exactly_one=True, language="en-US")
#print(location.raw)