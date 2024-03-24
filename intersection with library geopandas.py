#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 18:04:04 2024

@author: snowden
"""


import matplotlib.pyplot as plt
import time
import pandas as pd
import geopandas as gpd


gdf = gpd.read_file('dk/singlepart.shp')
gdf.head()


# Calculate center coordinates
gdf['center_coords'] = gdf['geometry'].centroid

# Plot the GeoDataFrame without annotations
ax = gdf.plot()

# Show the plot
plt.show()

# Pertama, kita perlu DataFrame untuk menyimpan hasil
# Kita akan membuat GeoDataFrame nanti
# Mulai menghitung waktu
start_time = time.time()
intersections_gdf = pd.DataFrame()

# Selanjutnya, kita akan melakukan iterasi melalui setiap baris di `gdf` dan mencari tahu apakah dan di mana garis tersebut berpotongan dengan garis lain.
for index, row in gdf.iterrows():
    # Dapatkan GeoSeries dari potongan baris dengan semua baris
    row_intersections = gdf.intersection(row['geometry'])
    # Kecualikan baris yang bukan geometri Titik
    row_intersection_points = row_intersections[row_intersections.geom_type == 'Point']
    # Buat DataFrame dari titik potongan baris
    row_intersections_df = pd.DataFrame(row_intersection_points)
    # Buat kolom untuk nama (atau nilai identifikasi lainnya) dari baris
    row_intersections_df['name_2'] = str(row['OBJECTID'])
    # Gabungkan gdf masukan dengan gdf potongan baris. Secara default, ini adalah gabungan kiri pada indeks.
    # Karena gdf baris adalah turunan dari gdf, indeks setiap baris yang berpotongan sama dengan di gdf
    row_intersections_df = row_intersections_df.join(gdf['OBJECTID'])
    # Gabungkan gdf potongan baris ke dalam gdf hasil
    intersections_gdf = pd.concat([row_intersections_df, intersections_gdf])
    
# Buang kolom geometri. Karena kita bergabung langsung dengan gdf masukan, kolom geometri adalah Garis untuk fitur pada indeks baris yang bergabung
# intersections_gdf = intersections_gdf.drop('geometry', axis = 1)
# Ganti nama dan tetapkan kolom titik sebagai kolom geometri
intersections_gdf = intersections_gdf.rename(columns={0: 'geometry'})
# Ada dua titik untuk setiap potongan. Kita hanya ingin satu. Kita akan membuat kolom baru untuk menyimpan nama potongan berdasarkan daftar yang diurutkan dari nama dua garis yang berpotongan
intersections_gdf['intersection'] = intersections_gdf.apply(lambda row: '-'.join(sorted([row['name_2'], str(row['OBJECTID'])])), axis = 1)
# Kita akan mengelompokkan potongan berdasarkan namanya, mengembalikan hanya hasil pertama untuk setiap nilai unik
intersections_gdf = intersections_gdf.groupby('intersection').first()
# Indeks sekarang adalah kolom potongan. Kita tidak menginginkannya, jadi kita akan mengatur ulang indeksnya
intersections_gdf = intersections_gdf.reset_index()
# Akhirnya, kita akan mengubah DataFrame kembali menjadi GeoDataFrame dan tetapkan CRS
intersections_gdf = gpd.GeoDataFrame(intersections_gdf, geometry = 'geometry')
intersections_gdf.crs = 'epsg:4326'

# Berhenti menghitung waktu
end_time = time.time()

intersections_gdf
waktu = end_time - start_time
print(f"Waktu yang diperlukan: {waktu} detik")
intersections_gdf

print(intersections_gdf.crs)
type(intersections_gdf)
ax = intersections_gdf.plot(marker='o', color='red', markersize=10)

# Plot the original lines from gdf on top of the intersections
gdf.plot(ax=ax)

# Add title and legend
plt.title('Intersections between Lines')
plt.legend(['Original Lines', 'Intersections'])

# Show the plot
plt.show()