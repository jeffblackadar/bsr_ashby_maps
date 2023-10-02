# bsr_ashby_maps

The meridians are based on the meridian of Rome, which is 12 degrees, 27 minutes and 7.1 seconds east of Greenwich
per https://digitalarchive.mcmaster.ca/islandora/object/macrepo%3A66660?page=15
Each bar is one minute

degree alt+0176

## Procedures

### Georectification

Open Python
Load qgis_create_points.py
in line 103 set map_name = "ta_map_149_ii_se-1"

Open QGIS
Open georeferencer
Check target SRS is EPSG:4806
Change output file name to -4806
Open Python
Mark outer points


File | Load GCP Points... AU DGA_00_template.points
Move 6 points to correct place on image
Start georefererncing
Check results in QGIS




## Particular maps
TA[MAP]-149.II.NE

Eastern limit starts at 0°0' (12°27'7.1" Greenwich)
Western limit starts at 0°7'X"  12 20 7.1
Northern 41°50'
Southern 41°45'

°
TA[MAP]-149.II.NE_modified.tif.points

mapX,mapY,pixelX,pixelY,enable,dX,dY,residual
12.3353055555555553,41.8333333333333357,772.85005482455812853,-568.71381578947671187,1,3.39804119407631333,0.05842193834280351,3.3985433761420949
12.3353055555555553,41.75,779.65509718216208057,-5318.47694364336075523,1,-3.40700116352763871,8.70991424989551888,9.35255383137737972
12.45197222222222067,41.75,5859.64268279860152688,-5335.86500015021010768,1,-3.33937703571609745,-8.67814225695383357,9.29847256373840203
12.45197222222222067,41.8333333333333357,5852.95496875750905019,-568.86243165705934643,1,3.34833700537637924,-0.09019392923983105,3.34955155900675461
