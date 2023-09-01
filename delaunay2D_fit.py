import vtk
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# %% Load the point cloud
point_cloud = np.loadtxt('adjusted_jcFS_ss_no-orientation.dip')

# %% Create vtkPoints object
points = vtk.vtkPoints()
for point in point_cloud:
    points.InsertNextPoint(point[0], point[1], point[2])

# Create vtkPolyData object
polydata = vtk.vtkPolyData()
polydata.SetPoints(points)

# %% Create vtkDelaunay2D object
delaunay = vtk.vtkDelaunay2D()
delaunay.SetInputData(polydata)
delaunay.SetAlpha(0)
delaunay.Update()

# %% Get the output of the Delaunay triangulation
output = delaunay.GetOutput()

# %% plot the surface
# Convert vtkUnstructuredGrid to vtkPolyData
surface_filter = vtk.vtkDataSetSurfaceFilter()
surface_filter.SetInputData(output)
surface_filter.Update()

# Get the surface as vtkPolyData
surface = surface_filter.GetOutput()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(surface)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

interactor.Initialize()
render_window.Render()
interactor.Start()

# Get the points on the surface
points = output.GetPoints()

# Get the number of points
n_points = points.GetNumberOfPoints()

# Get the points as a numpy array
points_array = np.zeros((n_points, 3))
for i in range(n_points):
    points_array[i, :] = points.GetPoint(i)

# %% Plot the points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2])

plt.show()