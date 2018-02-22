# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 23:09:17 2018

@author: Nir
"""
from sklearn.metrics import mean_squared_error, r2_score, explained_variance_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR
from geopy.distance import vincenty
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import glob
import csv

time_format = "%Y-%m-%d %H:%M:%S"
dir_path = "C:/Users/Nir/Downloads/release/taxi_log_2008_by_id/"
feature_names = ["source_location_lon",
                "source_location_lat",
                "dest_location_lon",
                "dest_location_lat",
                "distance",
                "real_distance",
                "month",
                "day_of_month",
                "day_of_week",
                "hour_of_day",
                "duration"]

def main():
    features = get_data()
    scaler = MinMaxScaler()
    norm_features = scaler.fit_transform(features[feature_names[:-1]])
    norm_label = scaler.fit_transform(features[feature_names[-1]].values.reshape(-1, 1))
    X = norm_features
    y = norm_label
    
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_lin = SVR(kernel='linear', C=1e3)
    svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    
    
    y_rbf = svr_rbf.fit(X, y.reshape(-1)).predict(X)
    y_lin = svr_lin.fit(X, y.reshape(-1)).predict(X)
    y_poly = svr_poly.fit(X, y.reshape(-1)).predict(X)
    
    print("RBF - mse:", mean_squared_error(y, y_rbf), "r2:", r2_score(y, y_rbf), "evs:", explained_variance_score(y, y_rbf))
    print("LINEAR - mse:", mean_squared_error(y, y_lin), "r2:", r2_score(y, y_lin), "evs:", explained_variance_score(y, y_lin))
    print("POLY - mse:", mean_squared_error(y, y_poly), "r2:", r2_score(y, y_poly), "evs:", explained_variance_score(y, y_poly))
    
    #plt.scatter(range(len(y)), y.reshape(-1), color="blue")
    #plt.scatter(range(len(y_rbf)), y_rbf.reshape(-1), color="red")

def get_data():
    
    # Retrive all text filenames from the directory
    filenames = glob.glob(dir_path + "*.txt")

    lst_data = list()
    
    # Read each text file (specific taxi readings) and extract the features
    for filename in filenames[0:5]:
        with open(filename, 'r') as f:
            
            # Read the taxi readings
            reader = list(csv.reader(f))
            
            # Divide the data into segments of close taxi readings (no more then 15 mins between two readings)
            segments = divide_to_segments(reader, 15)
            
            # Combine the data into source-destination combinations
            source_dest_combs = get_source_dest_comb(segments)
            
            # Go through all the source-destination combinations and extract all the features from each one
            for comb in source_dest_combs:
                
                # Extract all features from this source-destination combination
                row_features = extract_features(comb[0], comb[1])
                lst_data.append(row_features)
    
    # Convert the list into a dataframe of features
    features = pd.DataFrame(lst_data, columns=feature_names)
    
    return features
    
def get_source_dest_comb(segments):
    final_combinations = list()
    
    for segment in segments:
        source_dest_combs = list(itertools.combinations(segment, 2))
        final_combinations.append(source_dest_combs)
        
    return list(itertools.chain.from_iterable(final_combinations))
    
#def get_source_dest_comb(data, maximum_mins):
#    source_dest_comb = list()
#    
#    # Combine the data into source-destination combinations that in each combination,
#    # the time between two consecutive rows is less the maximum_mins and not zero (duplicate rows)
#    for index, row in enumerate(data[:-1]):
#        
#        # Hold the current row and the next one to calculate the time between them
#        curr_row = row
#        next_row = data[index + 1]
#        
#        # Extract only the duration (in seconds) feature from the two rows
#        duration = extract_features(curr_row, next_row, names=["duration"])[0]
#        
#        # Check if the duration (in minuts) meets the requirements of the maximum_mins and not zero (duplicate rows)
#        if duration != 0 and duration / 60.0 < maximum_mins:
#            
#            # Add the current row as a source and the next row as a destination
#            source_dest_comb.append((curr_row, next_row))
#    
#    return source_dest_comb

def divide_to_segments(data, maximum_mins):
    segments = list()
    curr_segment = list()
    
    # Divide the data into segments that each segment contains close readings by time
    # the time between two consecutive rows is less the maximum_mins and not zero (duplicate rows)
    for index, row in enumerate(data[:-1]):
        
        # Hold the current row and the next one to calculate the time between them
        curr_row = row
        next_row = data[index + 1]
        
        # Extract only the duration (in seconds) feature from the two rows
        duration = extract_features(curr_row, next_row, names=["duration"])[0]
        
        # Skip duplicate rows
        if duration == 0:
            continue
        
        # The row is added to the current segment.
        # The segment will be empty (new segment) if the previous row was far back in time
        curr_segment.append(curr_row)
        
        # Check if the duration (in minuts) does not meets the requirements of the maximum_mins
        if duration / 60.0 >= maximum_mins:
            
            # Save the current segment if he is big enough
            if len(curr_segment) > 1:
                segments.append(curr_segment)
                
            # Start a new segment  
            curr_segment = list()
    
    return segments
        
def extract_features(source, dest, names=None):
    row_features = list()
    
    # Extract source and destination longitude and latitude
    source_location = (source[2], source[3])
    dest_location = (dest[2], dest[3])
    
    # Show the source location only if asked
    if None == names or "source_location" in names:
        row_features.append(source_location[0])
        row_features.append(source_location[1])
    
    # Show the destination location only if asked
    if None == names or "dest_location" in names:
        row_features.append(dest_location[0])
        row_features.append(dest_location[1])
    
    # Show the distance between source and destination only if asked
    if None == names or "distance" in names:
        distance = vincenty(source_location, dest_location).km
        row_features.append(distance)
        
    # Show the month of the reading only if asked
    if None == names or "month" in names:
        month = datetime.strptime(source[1], time_format).month
        row_features.append(month)
        
    # Show the day of the month of the reading only if asked
    if None == names or "day_of_month" in names:
        day_of_month = datetime.strptime(source[1], time_format).day
        row_features.append(day_of_month)
        
    # Show the day of the week of the reading only if asked
    if None == names or "day_of_week" in names:
        day_of_week = datetime.strptime(source[1], time_format).weekday()
        row_features.append(day_of_week)
        
    # Show the hour of the day of the reading only if asked
    if None == names or "hour_of_day" in names:
        hour_of_day = datetime.strptime(source[1], time_format).hour
        row_features.append(hour_of_day)
    
    # Show the duration time in seconds to get from source to destination only if asked
    if None == names or "duration" in names:
        source_time = datetime.strptime(source[1], time_format)
        dest_time = datetime.strptime(dest[1], time_format)
        duration = (dest_time - source_time).total_seconds()
        row_features.append(duration)
    
    return row_features
            
if "__main__" == __name__:
    main()            

#geolocator = GoogleV3()
#location = geolocator.reverse(latlon, exactly_one=True, language="en-US")
#print(location.raw)