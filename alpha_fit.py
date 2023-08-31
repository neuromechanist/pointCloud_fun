import vtk
import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# %% Load the point cloud
point_cloud = np.loadtxt('adjusted_jcFS_ss_no-orientation.dip')

# %% Fit a surface to the point cloud
points = vtk.vtkPoints()
for point in point_cloud:
    points.InsertNextPoint(point)

delaunay = vtk.vtkDelaunay3D()
delaunay.SetInputData(points)
delaunay.Update()

# %% Get the surface
surface = delaunay.GetOutput()

# %% Get the points on the surface
points = surface.GetPoints()

# %% Get the number of points
n_points = points.GetNumberOfPoints()

# %% Get the points as a numpy array
points_array = np.zeros((n_points, 3))

for i in range(n_points):
    points_array[i, :] = points.GetPoint(i)

# %% Plot the points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2])
plt.show()