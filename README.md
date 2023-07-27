## 📌 Description
create a georeferenced image with colors of grid cell values over a surface
## 📸 Screenshot
![screenshot1](https://github.com/pemn/assets/blob/main/vtk_grid_to_raster1.png?raw=true)
## 📝 Parameters
name|optional|description
---|---|------
input_grid|❎|grid in vtk format
variable|❎|cell field in grid to use a value
lito_rgb|☑️|lookup table assign a rgb color to each unique value of variable 
surface|❎|surface that will be used as the 2d reference for selecting grid cells
output|☑️|path to save the result in one of the supported formats:
||tif|geotif raster
||png|unreferenced png image
||csv|unreferenced csv ascii
display||show the result in a image display window

## 📓 Notes
### lito rgb file format example
lito|rgb
---|---
if|#0000FF
hf|#FF0000
cg|#00FF00
## 📚 Examples
### raster as a png image
![screenshot2](https://github.com/pemn/assets/blob/main/vtk_grid_to_raster2.png?raw=true)
### raster as texture in 3d scene
![screenshot3](https://github.com/pemn/assets/blob/main/vtk_grid_to_raster3.png?raw=true)
## 🧩 Compatibility
distribution|status
---|---
![winpython_icon](https://github.com/pemn/assets/blob/main/winpython_icon.png?raw=true)|✔
![vulcan_icon](https://github.com/pemn/assets/blob/main/vulcan_icon.png?raw=true)|❌
![anaconda_icon](https://github.com/pemn/assets/blob/main/anaconda_icon.png?raw=true)|❌
## 🙋 Support
Any question or problem contact:
 - paulo.ernesto
## 💎 License
Apache 2.0  
Copyright ![vale_logo_only](https://github.com/pemn/assets/blob/main/vale_logo_only_r.svg?raw=true) Vale 2023
