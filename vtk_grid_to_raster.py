#python
# create a georeferenced image with colors of grid cell values along a surface
# v1.0 2023/07 paulo.ernesto
# Copyright 2023 Vale
# License: Apache 2.0
# https://github.com/pemn/vtk_grid_to_raster
'''
usage: $0 input_grid*vtk variable:input_grid lito_rgb*xlsx surface*vtk output*png,tif display@ geotif_epsg=3395,29191,29192,29193,31981,31982,31983
'''
import sys, os
import numpy as np
import pandas as pd
# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui

from pd_vtk import pv_read, vtk_Voxel, Raytracer

class AutoRGB(dict):
  _dc = np.ones(4)

  def from_colormap(self, s, name = 'plasma'):
    import matplotlib
    cmap = matplotlib.colormaps[name]
    u = np.unique(s)
    d = cmap(np.linspace(0,1, u.size)) * 255
    #z = list(zip(u.tolist(), d.tolist()))
    self.update(dict(zip(u, d)))
  
  def from_lookup(self, ds):
    self.update(dict([(k,ImageColor.getrgb(v) + (255,)) for k,v in ds.items()]))

  def __call__(self, key):
    #if isinstance(key, np.ndarray):
    #  return self.get(*key, self._dc)
    return self.get(key, self._dc)

def vtk_grid_to_geotif(input_grid, variable, lito_rgb, surface, output, display, epsg = None):
  data_axis = 0
  meshdist = 'meshdist'
  auto_rgb = AutoRGB()
  if lito_rgb:
    df_rgb = pd.read_excel(lito_rgb)
    if not df_rgb.empty:
      df_rgb = df_rgb.set_index(df_rgb.columns[0])
      if df_rgb.shape[1] > 0:
        auto_rgb.from_lookup(df_rgb[df_rgb.columns[0]])

  grid = vtk_Voxel.from_file_vtk(input_grid)
  mesh = pv_read(surface)
  rt = Raytracer(grid, True, np.PINF)
  rt.raytrace(mesh)
  grid.cell_data[meshdist] = rt.value
  i2d = np.argmin(grid.ijk_array(meshdist), data_axis)
  g2d = np.reshape(np.take_along_axis(grid.ijk_array(variable), np.reshape(i2d, (1, i2d.shape[0], i2d.shape[1])), data_axis), i2d.shape)


  if len(auto_rgb) == 0:
    auto_rgb.from_colormap(g2d)


  raster = np.ndarray((g2d.shape[0], g2d.shape[1], 4), dtype='uint8')
  for ri, rd in np.ndenumerate(g2d):
    raster[ri] = auto_rgb(rd)

  raster = np.flip(raster, 0)

  if not output:
    ...
  elif output.lower().endswith('csv'):
    s = np.concatenate((np.reshape(np.transpose(np.indices(g2d.shape), np.arange(g2d.ndim,-1,-1)), (g2d.size, g2d.ndim)), np.reshape(g2d, (g2d.size,1))), 1)
    np.savetxt(output, s, delimiter=',', header=f'i,j,{variable}',comments='')
  elif output.lower().endswith('png'):
    from PIL import Image, ImageColor
    img = Image.fromarray(raster)
    img.save(output)
  elif output.lower().endswith('f'):
    from vulcan_save_tri import gdal_save_geotiff
    bb = np.take(grid.bounds, [[0, 2, 4], [1, 2, 4], [1, 3, 4], [0, 3, 4]])
    gdal_save_geotiff(np.moveaxis(raster, 2, 0), bb, output, epsg)

  if int(display):
    import matplotlib.pyplot as plt
    plt.matshow(raster)
    plt.show()

main = vtk_grid_to_geotif

if __name__=="__main__":
  usage_gui(__doc__)
