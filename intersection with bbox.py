#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 18:02:33 2024

@author: snowden
"""

import geopandas as gpd
import pandas as pd
import time
import matplotlib.pyplot as plt

# Membaca file shp
def read_file(namafile):
    gdf = gpd.read_file(namafile)
    return gdf

# Menyiapkan data linestring
def create_linestring(gdf):
    data_linestring = []
    for index, row in gdf.iterrows():
        id_linestring = row['OBJECTID']
        koordinat = list(row['geometry'].coords)
        data_linestring.append([id_linestring, koordinat])
    return data_linestring

# Membuat bounding box dari suatu linestring
def calculate_bounding_box(line):
    x_coords, y_coords = zip(*line)
    min_x = min(x_coords)
    min_y = min(y_coords)
    max_x = max(x_coords)
    max_y = max(y_coords)
    return [(min_x, min_y), (max_x, max_y)]

# Fungsi untuk memeriksa overlap antara dua bounding box
def is_overlap(bbox1, bbox2):
    min_x1, min_y1 = bbox1[0]
    max_x1, max_y1 = bbox1[1]
    min_x2, min_y2 = bbox2[0]
    max_x2, max_y2 = bbox2[1]

    # Memeriksa apakah terjadi overlap antara dua bounding box
    return not (max_x1 < min_x2 or min_x1 > max_x2 or max_y1 < min_y2 or min_y1 > max_y2)

# Fungsi untuk menghitung titik-titik perpotongan antara dua garis (linestring)
def calculate_intersection_points(line1, line2):
    intersection_points = []

    for i in range(len(line1) - 1):
        for j in range(len(line2) - 1):
            x1, y1 = line1[i]
            x2, y2 = line1[i + 1]
            x3, y3 = line2[j]
            x4, y4 = line2[j + 1]

            # Hitung determinan
            det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

            if det != 0: #hindari pembagian dengan 0
                # Hitung titik perpotongan
                px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / det
                py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / det

                # Periksa apakah titik perpotongan berada pada segmen
                if min(x1, x2) <= px <= max(x1, x2) and min(x3, x4) <= px <= max(x3, x4) and min(y1, y2) <= py <= max(y1, y2) and min(y3, y4) <= py <= max(y3, y4):
                    intersection_points.append((px, py))

    return intersection_points

# Fungsi untuk menghitung waktu pemrosesan
def calculate_processing_time(start_time, end_time):
    processing_time = end_time - start_time
    return processing_time

# Fungsi untuk membuat visualisasi jumlah dan hasil perpotongan
def visualize_intersection_results(intersection_points, lines):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot linestrings
    for line_id, line_coords in lines:
        x_coords, y_coords = zip(*line_coords)
        ax.plot(x_coords, y_coords, label=f'Linestring {line_id}')
        ax.scatter(x_coords, y_coords, color='black')

    # Plot intersection points
    if intersection_points:
        x_int, y_int = zip(*intersection_points)
        ax.scatter(x_int, y_int, color='red', label='Intersection Points')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Linestrings and Intersection Points')
    plt.show()

# Panggil fungsi read file
pathfile = input("Masukkan path file:")
file = read_file(pathfile)

# Panggil fungsi create linestring
data_linestring = create_linestring(file)

# Membuat bounding box dan menampilkan linestring
bounding_boxes = []
fig, ax = plt.subplots(figsize=(10, 8))
for id_linestring, coordinates in data_linestring:
    bounding_box = calculate_bounding_box(coordinates)
    bounding_boxes.append([id_linestring, bounding_box])
    x_coords, y_coords = zip(*coordinates)
    ax.plot(x_coords, y_coords, label=f'Linestring {id_linestring}')
    ax.scatter(x_coords, y_coords, color='black')

# Mencari titik-titik perpotongan
start_time = time.time()  # Waktu awal pemrosesan
intersection_points = []

checked_bbox_pairs = set()  # Set untuk menyimpan pasangan bbox yang sudah diperiksa
for i in range(len(bounding_boxes)):
    for j in range(i + 1, len(bounding_boxes)):
        bbox1_id, bbox1 = bounding_boxes[i]
        bbox2_id, bbox2 = bounding_boxes[j]
        if bbox1_id != bbox2_id:  # Periksa apakah bbox memiliki ID yang berbeda
            bbox_pair = tuple(sorted((bbox1_id, bbox2_id)))  # Mengurutkan ID bbox agar urutannya tidak mempengaruhi
            if bbox_pair not in checked_bbox_pairs:  # Memeriksa apakah pasangan bbox sudah diperiksa sebelumnya
                bbox1 = bounding_boxes[i][1]
                bbox2 = bounding_boxes[j][1]
                if is_overlap(bbox1, bbox2):
                    line1 = data_linestring[i][1]
                    line2 = data_linestring[j][1]
                    intersection_points.extend(calculate_intersection_points(line1, line2))
                    print(f"Bounding box ID {bbox1_id} overlap with Bounding box ID {bbox2_id}, {len(intersection_points)} titik perpotongan telah terhitung")
                checked_bbox_pairs.add(bbox_pair)  # Menambah pasangan bbox yang sudah diperiksa ke dalam set
end_time = time.time()  # Waktu akhir pemrosesan
processing_time = calculate_processing_time(start_time, end_time)
print(f"Total waktu pemrosesan: {processing_time} detik")

# Simpan data titik perpotongan dalam file CSV
df_intersection_points = pd.DataFrame(intersection_points, columns=['Longitude', 'Latitude'])
df_intersection_points.to_csv('intersection_points.csv', index=False)

# Visualisasi jumlah dan hasil perpotongan
visualize_intersection_results(intersection_points,data_linestring )