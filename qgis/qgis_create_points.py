def degrees_to_seconds(deg,min,sec):
    #convert degrees to a whole number to make it easier for addition  
    return (deg*60*60)+(min*60)+sec

def add_degrees(deg1,min1,sec1,deg2,min2,sec2):
    degree1 = degrees_to_seconds(deg1,min1,sec1)
    degree2 = degrees_to_seconds(deg2,min2,sec2)
    return(degree1+degree2)

def add_rome(deg,min,sec):
    #rome_lon_deg = 12
    #rome_lon_min = 27
    #rome_lon_sec = 7.1
    rome_lon_deg = 0
    rome_lon_min = 0
    rome_lon_sec = 0

    return add_degrees(deg,min,sec,rome_lon_deg,rome_lon_min,rome_lon_sec)

def convert_seconds_to_deg_dec(base60):
    sec = base60 % 60
    #print(sec)
    base60_working = base60 - sec
    min_working = (base60_working % (60*60))
    min = min_working/60
    #print(min)
    base60_working = base60_working - min_working
    deg = base60_working/(60*60)
    #print(deg)
    degree_fraction = (min*60+sec)/(60*60)
    return(deg+degree_fraction)

west_of_rome = True
map_lon_origin_dir = "east"
map_lon_origin_deg = 0
map_lon_origin_min = 0
map_lon_origin_sec = 0

#print(add_rome(0,0,0))
#d = add_rome(0,0,0)
#print(convert_seconds_to_deg_dec(d))

#print (degrees_to_seconds(rome_lon_deg,rome_lon_min,rome_lon_sec))

#12.335,41.833,772,-568
#12.335,41.750,779,-5318
#12.451,41.750,5859,-5335
#12.451,41.833,5852,-568

def calculate_points_on_line(lat_lon_static, inc_dec, west_of_meridian, origin_lat_deg, origin_lat_min, origin_lat_sec, origin_lon_deg, origin_lon_min, origin_lon_sec, mins, pixel_origin_x, pixel_origin_y, pixel_end_x, pixel_end_y):
    points_lines = ""
    

    if lat_lon_static == "lat":
        static_deg = origin_lat_deg
        static_min = origin_lat_min
        static_sec = origin_lat_sec
        static = convert_seconds_to_deg_dec(degrees_to_seconds(static_deg,static_min,static_sec))
        calc_origin_deg = origin_lon_deg
        calc_origin_min = origin_lon_min
        calc_origin_sec = origin_lon_sec
        calc_origin_seconds = add_rome(calc_origin_deg,calc_origin_min,calc_origin_sec)
                
    else:
        static_deg = origin_lon_deg
        static_min = origin_lon_min
        static_sec = origin_lon_sec
        static = convert_seconds_to_deg_dec(add_rome(static_deg,static_min,static_sec))

        calc_origin_deg = origin_lat_deg
        calc_origin_min = origin_lat_min
        calc_origin_sec = origin_lat_sec
        calc_origin_seconds = degrees_to_seconds(calc_origin_deg,calc_origin_min,calc_origin_sec)
                
    
    pixel_inc_x = (pixel_end_x - pixel_origin_x)/mins
    pixel_inc_y = (pixel_end_y - pixel_origin_y)/mins
    min_step = 1
    east_of_meridian = False
    min_seconds = degrees_to_seconds(0,1,0)
    if inc_dec == "dec":
        min_step = -1
    min_west_dec = 1
    if west_of_meridian == True:
        min_west_dec = -1  
        


    for mins in range(0, mins+1):
        point_line = ""
        calc_seconds = calc_origin_seconds + (mins*min_seconds*min_step*min_west_dec)
        calc_deg_dec = convert_seconds_to_deg_dec(calc_seconds)
        calc_pixel_x = pixel_origin_x + (mins*pixel_inc_x)
        calc_pixel_y = pixel_origin_y + (mins*pixel_inc_y)
        if lat_lon_static == "lat":
            # mapX,mapY,pixelX,pixelY,enable,dX,dY,residual 12.3353055555555553,41.8333333333333357,772.85005482455812853,-568.71381578947671187,1,3.39804119407631333,0.05842193834280351,3.3985433761420949
            point_line = str(calc_deg_dec)+","+str(static)+","+str(calc_pixel_x)+","+str(calc_pixel_y*-1)+",1,0,0\n"
        else:
            point_line = str(static)+","+str(calc_deg_dec)+","+str(calc_pixel_x)+","+str(calc_pixel_y*-1)+",1,0,0\n"
        points_lines = points_lines + point_line
    return(points_lines) 

map_name = "ta-map-150-iii-so"
point_lines = ""
point_lines = calculate_points_on_line("lat", "inc", False, 41, 45, 0, 0, 0, 0, 7, 538.629, 474.412, 5372.37, 479.767)
point_lines = point_lines + calculate_points_on_line("lat", "inc", False, 41, 40, 0, 0, 0, 0, 7, 517.213, 5013.67, 5355.24, 5037.23)
point_lines = point_lines + calculate_points_on_line("lon", "dec", False, 41, 45, 0, 0, 0, 0, 5, 538.629, 474.412, 517.213, 5013.67)
# Let's not put points not on the border of the map

print(point_lines)

map_points_path = os.path.join(os.path.join('E:\\a_new_orgs\\carleton\\bsr\\',(map_name+"\\")),(map_name+".points"))



import os
with open(map_points_path, 'w') as f:
    f.write("mapX,mapY,pixelX,pixelY,enable,dX,dY,residual\n")  
    f.write(point_lines)
#12.335,41.833,772,-568
#12.335,41.750,779,-5318
#12.451,41.750,5859,-5335
#12.451,41.833,5852,-568