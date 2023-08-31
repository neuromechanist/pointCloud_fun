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

# %% Create a VTK renderer and window
renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)  # Set background color to white

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create a VTK interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create a VTK point cloud
vtk_points = vtk.vtkPoints()
for point in point_cloud:
    vtk_points.InsertNextPoint(point)

vtk_polydata = vtk.vtkPolyData()
vtk_polydata.SetPoints(vtk_points)

# Create a VTK glyph to visualize the points
glyph = vtk.vtkVertexGlyphFilter()
glyph.SetInputData(vtk_polydata)
glyph.Update()

# Create a VTK mapper and actor
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(glyph.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(0, 0, 1)  # Set point color to blue

# Add the actor to the renderer
renderer.AddActor(actor)

# Start the interactor
interactor.Initialize()
render_window.Render()
interactor.Start()

# %%
