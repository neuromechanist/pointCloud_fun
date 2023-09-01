import vtk
import numpy as np
import matplotlib.pyplot as plt

# %% Load the point cloud
point_cloud = np.loadtxt('adjusted_jcFS_ss_no-orientation.dip')

# %% Fit a surface to the point cloud
points = vtk.vtkPoints()
for point in point_cloud:
    points.InsertNextPoint(point)

polydata = vtk.vtkPolyData()
polydata.SetPoints(points)

# %% Create a delaunay triangulation
delaunay = vtk.vtkDelaunay3D()
delaunay.SetInputData(polydata)
delaunay.SetAlpha(0.0)
delaunay.Update()

# %% Get the surface
output = delaunay.GetOutput()

# Convert vtkUnstructuredGrid to vtkPolyData
surface_filter = vtk.vtkDataSetSurfaceFilter()
surface_filter.SetInputData(output)
surface_filter.Update()

# Get the surface as vtkPolyData
surface = surface_filter.GetOutput()

# %% Visualize the surface
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

# %% Write the surface to a file
ply_writer = vtk.vtkPLYWriter()
ply_writer.SetFileName('delaunay3D_overCortex.ply')
ply_writer.SetInputData(surface)
ply_writer.Write()
