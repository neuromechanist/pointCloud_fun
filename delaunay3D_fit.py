# %% init
import vtk
import numpy as np

# %% Load the point cloud
point_cloud = np.loadtxt('jcFS_ss_no-orientation.dip')

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

# %% Create the surface renderer
surface_mapper = vtk.vtkPolyDataMapper()
surface_mapper.SetInputData(surface)

surface_actor = vtk.vtkActor()
surface_actor.SetMapper(surface_mapper)
surface_actor.GetProperty().SetOpacity(0.4)
renderer = vtk.vtkRenderer()
renderer.AddActor(surface_actor)
renderer.SetBackground(1, 1, 1)  # Set the background color to white

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create a VTK point cloud
vtk_points = vtk.vtkPoints()
for point in point_cloud:
    vtk_points.InsertNextPoint(point)

vtk_polydata = vtk.vtkPolyData()
vtk_polydata.SetPoints(vtk_points)

# Create a VTK glyph to visualize the points
glyph = vtk.vtkGlyph3D()
glyph.SetInputData(vtk_polydata)
glyph.Update()

# set the shape of the glyph
sphere_source = vtk.vtkSphereSource()
sphere_source.SetRadius(0.25)  # Set the radius of the sphere
glyph.SetSourceConnection(sphere_source.GetOutputPort())
glyph.Update()

# Increase the glyph size
# glyph.SetScaleFactor(2.0)  # Adjust the scale factor as desired

# Create a VTK mapper and actor
pc_mapper = vtk.vtkPolyDataMapper()
pc_mapper.SetInputConnection(glyph.GetOutputPort())

pc_actor = vtk.vtkActor()
pc_actor.SetMapper(pc_mapper)
pc_actor.GetProperty().SetColor(0, 0, 1)  # Set point color to blue

# Add the actor to the renderer
renderer.AddActor(pc_actor)

render_window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# %% Create thea renderer
interactor.Initialize()
render_window.Render()
interactor.Start()

# %% export the renderer to a VRML file
vrml_exporter = vtk.vtkVRMLExporter()
vrml_exporter.SetFileName('delaunay3D_overCortex.wrl')
vrml_exporter.SetRenderWindow(render_window)
vrml_exporter.Write()

# %% Write the surface to a file
ply_writer = vtk.vtkPLYWriter()
ply_writer.SetFileName('delaunay3D_overCortex.ply')
ply_writer.SetInputData(surface)
ply_writer.Write()
