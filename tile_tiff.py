import rasterio
import rasterio.plot
import gdal
import osr
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np
import gdalnumeric
import cv2
import os

class Tiletiff:

    # class attribute
    tiff_to_tile_path = "" # the source tiff to be split into tiles
    tt_tile_path = "/content/" # the path to where the tiles are saved   

    # varables for gdal    
    tt_gdal_dataset = ""
    tt_srs = ""
    tt_cols = 0
    tt_rows = 0

    # varables for rasterio
    tt_raterio_dataset = 0
    tt_crs = 0
    tt_crs_int = 0
    tt_left_min_x = 0
    tt_bottom_min_y = 0
    tt_right_max_x = 0
    tt_top_max_y = 0
    tt_coords = 0
    tt_pixel_size_x = 0
    tt_pixel_size_y = 0

    # set this for tile size
    tt_tile_pixel_width = 1000
    tt_tile_pixel_height = 1000

    # set this for overlap
    tt_tile_pixel_width_overlap = 0 # 200
    tt_tile_pixel_height_overlap = 0 # 100

    tt_tile_matrix = []
    # gdal
    tt_gdal_driver = ""
    tt_gdal_dataset = ""
    tt_gdal_dataset_band = ""
    tt_gdal_transform = ""
    tt_gdal_data = ""

    def create_tile_matrix(self):
        self.tt_tile_matrix = []
        number_tiles_wide = int(self.tt_cols/(self.tt_tile_pixel_width - self.tt_tile_pixel_width_overlap))+1
        number_tiles_high = int(self.tt_rows/(self.tt_tile_pixel_height - self.tt_tile_pixel_height_overlap))+1
        print("create_tile_matrix", number_tiles_wide,number_tiles_high)    
        # rows
        for tif_rows in range(0, number_tiles_high):
            # columns
            for tif_cols in range(0, number_tiles_wide):
                # If the bottom row, tile from bottom back
                if tif_rows == number_tiles_high - 1:
                    lry = self.tt_rows - self.tt_tile_pixel_height
                    uly = self.tt_rows
                else:
                    lry = 0 + ((self.tt_tile_pixel_height - self.tt_tile_pixel_height_overlap) * tif_rows)  # self.tt_bottom_min_y
                    uly = lry + self.tt_tile_pixel_height                    

                # If the end column, tile from right back
                if tif_cols == number_tiles_wide - 1:
                    lrx = self.tt_cols - self.tt_tile_pixel_width
                    ulx = self.tt_cols
                else:
                    lrx = 0 + ((self.tt_tile_pixel_width - self.tt_tile_pixel_width_overlap) * tif_cols)  # self.tt_left_min_x
                    ulx = lrx + self.tt_tile_pixel_width

                if(lrx>self.tt_cols):
                    lrx=self.tt_cols
                
                if(lry>self.tt_rows):
                    lry=self.tt_rows
                
                if(ulx>self.tt_cols):
                    ulx=self.tt_cols
                
                if(uly>self.tt_rows):
                    uly=self.tt_rows
                
                self.tt_tile_matrix.append([[lrx, lry], [ulx, uly], [tif_cols,tif_rows]])

        return(self.tt_tile_matrix)
    
    def create_tile_files(self):
        self.tt_boundary_polys = gpd.GeoDataFrame()
        self.tt_boundary_polys['geometry'] = None
        self.tt_boundary_polys.crs = ("EPSG:" + str(self.tt_crs_int))
        self.tt_boundary_polys.geometry = self.tt_boundary_polys.geometry.to_crs(crs=self.tt_crs_int)
        self.tt_boundary_polys.to_crs(crs=self.tt_crs_int)
        self.tt_boundary_polys = self.tt_boundary_polys.to_crs(epsg=self.tt_crs_int)
        for tile in self.tt_tile_matrix:
            minx = tile[0][0]
            maxx = tile[1][0]
            miny = tile[0][1]
            maxy = tile[1][1]

            tilex = "00"+str(tile[2][0])
            tilex = tilex[-2:]
            tiley = "00"+str(tile[2][1])
            tiley = tiley[-2:]

            self.tt_gdal_data = self.tt_gdal_dataset_band.ReadAsArray(minx, miny, maxx-minx, maxy-miny)

            output_file_name_base = "r" + tiley + "c" + tilex 
            output_file_name_tiff = output_file_name_base + ".tif"
            output_file_path = os.path.join(self.tt_tile_path,output_file_name_tiff)
            print(output_file_path)
            print(self.tt_gdal_dataset)

            self.tile_dst_ds = gdal.Translate(output_file_path, self.tt_gdal_dataset, srcWin = [minx, miny, maxx-minx, maxy-miny])
            print(self.tile_dst_ds)
            this_tile_x_min = self.tt_left_min_x + (minx*self.tt_pixel_size_x)
            this_tile_y_min = self.tt_top_max_y - (miny*self.tt_pixel_size_y)
            this_tile_x_max = self.tt_left_min_x + (maxx*self.tt_pixel_size_x)
            this_tile_y_max = self.tt_top_max_y - (maxy*self.tt_pixel_size_y)
            print("this_tile_transform",this_tile_x_min, self.tt_gdal_transform[1], self.tt_gdal_transform[2], this_tile_y_min, self.tt_gdal_transform[4], self.tt_gdal_transform[5])
            this_tile_transform = (this_tile_x_min, self.tt_gdal_transform[1], self.tt_gdal_transform[2], this_tile_y_min, self.tt_gdal_transform[4], self.tt_gdal_transform[5])
            print("this_tile_transform2",this_tile_transform)
            ## COLOR
            self.tile_dst_ds.GetRasterBand(1).SetRasterColorTable(self.tt_gdal_dataset_band.GetRasterColorTable())
            self.tile_dst_ds.GetRasterBand(1).SetRasterColorInterpretation(self.tt_gdal_dataset_band.GetRasterColorInterpretation())

            # Write metadata
            self.tile_dst_ds.SetGeoTransform(this_tile_transform)
            self.tile_dst_ds.SetProjection(self.tt_gdal_dataset.GetProjection())
            
            self.tile_dst_ds.GetRasterBand(1).WriteArray(self.tt_gdal_data)
            self.tile_dst_ds = None

            coords = [(this_tile_x_min, this_tile_y_min), (this_tile_x_max, this_tile_y_min), (this_tile_x_max, this_tile_y_max), (this_tile_x_min, this_tile_y_max)]
            poly = Polygon(coords)
            new_tp_row = {'id':output_file_name_base, 'geometry':poly}
            self.tt_boundary_polys = self.tt_boundary_polys.append(new_tp_row, ignore_index=True)     

        self.tt_boundary_polys.to_file(os.path.join(self.tt_tile_path,'tile_polys.shp'))

    def __init__(self,tiff_to_tile_path, tt_tile_path = "/content/"):
        self.tiff_to_tile_path = tiff_to_tile_path
        self.tt_tile_path = tt_tile_path

        self.tt_raterio_dataset = rasterio.open(self.tiff_to_tile_path)
        self.tt_rows,self.tt_cols = self.tt_raterio_dataset.shape
        self.tt_crs =  self.tt_raterio_dataset.crs
        if(self.tt_crs.is_valid):
            
            self.tt_crs_int = int(str(self.tt_crs)[5:])
        else:
            self.tt_crs_int = 3857
        self.tt_srs = osr.SpatialReference()

        self.tt_srs.ImportFromEPSG(int(str(self.tt_crs_int)))

        self.tt_left_min_x = self.tt_raterio_dataset.bounds[0]
        self.tt_bottom_min_y = self.tt_raterio_dataset.bounds[1]
        self.tt_right_max_x = self.tt_raterio_dataset.bounds[2]
        self.tt_top_max_y = self.tt_raterio_dataset.bounds[3]
        self.tt_coords = [(self.tt_left_min_x, self.tt_bottom_min_y), (self.tt_right_max_x, self.tt_bottom_min_y), (self.tt_right_max_x, self.tt_top_max_y), (self.tt_left_min_x, self.tt_top_max_y)]
    
        self.tt_pixel_size_x, self.tt_pixel_size_y = self.tt_raterio_dataset.res

        self.tt_gdal_driver = gdal.GetDriverByName('GTiff')
        self.tt_gdal_dataset = gdal.Open(tiff_to_tile_path)
        self.tt_gdal_dataset_band = self.tt_gdal_dataset.GetRasterBand(1)
        self.tt_gdal_transform = self.tt_gdal_dataset.GetGeoTransform()
    
    def plot_tif_and_poly(self):
        poly_df=gpd.read_file(os.path.join(self.tt_tile_path,'tile_polys.shp'))
        ax = poly_df.plot(figsize=(20, 20), alpha=0.5, edgecolor='k')
        rasterio.plot.show(self.tt_raterio_dataset, ax=ax)
        poly_df.boundary.plot(ax=ax,color="red",alpha=0.5)
        ax = poly_df.plot(figsize=(20, 20), alpha=0.5, edgecolor='k')

        tiles = []
        for tf in tiles:
            tif_file = rasterio.open(tf)
            rasterio.plot.show(tif_file, ax=ax)

        poly_df.boundary.plot(ax=ax,color="red",alpha=0.5)
    def plot_tif_and_poly_map_overlap(self, tiles):
        poly_df=gpd.read_file(os.path.join(self.tt_tile_path,'tile_polys.shp'))
        ax = poly_df.plot(figsize=(20, 20), alpha=0.5, edgecolor='k')
        rasterio.plot.show(self.tt_raterio_dataset, ax=ax)
        poly_df.boundary.plot(ax=ax,color="red",alpha=0.5)
        ax = poly_df.plot(figsize=(20, 20), alpha=0.5, edgecolor='k')

        for tf in tiles:
            tif_file = rasterio.open(tf)
            rasterio.plot.show(tif_file, ax=ax)

        poly_df.boundary.plot(ax=ax,color="red",alpha=0.5)

    def plot_tif_and_poly_map5_overlap(self, tiles):
        poly_df=gpd.read_file(os.path.join(self.tt_tile_path,'tile_polys.shp'))
        ax = poly_df.plot(figsize=(20, 20), alpha=0.5, edgecolor='k')
        rasterio.plot.show(self.tt_raterio_dataset, ax=ax)
        poly_df.boundary.plot(ax=ax,color="red",alpha=0.5)
        ax = poly_df.plot(figsize=(20, 20), alpha=0.5, edgecolor='k')

        for tf in tiles:
            tif_file = rasterio.open(tf)
            rasterio.plot.show(tif_file, ax=ax)

        poly_df.boundary.plot(ax=ax,color="red",alpha=0.5)
        poly_df['coords'] = poly_df['geometry'].apply(lambda x: x.representative_point().coords[:])
        poly_df['coords'] = [coords[0] for coords in poly_df['coords']]

        for idx, row in poly_df.iterrows():
            ax.annotate(s=row['id'], xy=row['coords'], horizontalalignment='center')

    def plot_tif_and_poly_map_no_overlap(self, tiles):
        poly_df=gpd.read_file(os.path.join(self.tt_tile_path,'tile_polys.shp'))
        ax = poly_df.plot(figsize=(20, 20), alpha=0.5, edgecolor='k')
        rasterio.plot.show(self.tt_raterio_dataset, ax=ax)
        poly_df.boundary.plot(ax=ax,color="red",alpha=0.5)
        ax = poly_df.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')

        for tf in tiles:
            tif_file = rasterio.open(tf)
            rasterio.plot.show(tif_file, ax=ax)

        poly_df.boundary.plot(ax=ax,color="red",alpha=0.5)
        poly_df['coords'] = poly_df['geometry'].apply(lambda x: x.representative_point().coords[:])
        poly_df['coords'] = [coords[0] for coords in poly_df['coords']]

        for idx, row in poly_df.iterrows():
            plt.annotate(s=row['id'], xy=row['coords'], horizontalalignment='center')

    def get_attributes(self):
        return {
            "cols": str(self.tt_cols), 
            "rows": str(self.tt_rows),
            "crs": str(self.tt_crs),
            "left_min_x": str(self.tt_left_min_x),
            "bottom_min_y": str(self.tt_bottom_min_y),
            "right_max_x": str(self.tt_right_max_x),
            "top_max_y": str(self.tt_top_max_y),
            "coords": str(self.tt_coords),
            "pixel_size_x": str(self.tt_pixel_size_x),
            "pixel_size_y": str(self.tt_pixel_size_y)
            }
