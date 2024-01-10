# Description: find the closest points of a point cloud to a surface patch.
# Algorithm:
# 1. Load the surface patch and the point cloud.
# 2. Divide the patch to 32x32 smaller patches.
# 3. For each smaller patch, find the closest point in the point cloud.
# 4. Determine if the closest point is at either side of the patch.
# 5. Find the index of the closest points in the point cloud and correlate that to the index of the small patch.
# %% initialize
# load the patch and the point cloud
import vtk
import numpy as np
from scipy.spatial import cKDTree

PLOT_PATCH = True
# load the patch
# Create a vtkPLYReader object
ply_reader = vtk.vtkPLYReader()
ply_reader.SetFileName('projected_patch.ply')
ply_reader.Update()

# Get the output of the PLY reader
patch = ply_reader.GetOutput()

# Load the point cloud
point_cloud = np.loadtxt('jcFS_ss_no-orientation.dip')

# make a polydata object from the point cloud
points = vtk.vtkPoints()
for point in point_cloud:
    points.InsertNextPoint(point)

polydata = vtk.vtkPolyData()
polydata.SetPoints(points)

# %% plot the patch and the point cloud
# patch mapper and actor
if PLOT_PATCH:
    patch_mapper = vtk.vtkPolyDataMapper()
    patch_mapper.SetInputData(patch)
    patch_actor = vtk.vtkActor()
    patch_actor.SetMapper(patch_mapper)

    # point cloud mapper and actor
    # Create a VTK glyph to visualize the points
    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(polydata)
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

    # create a renderer
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.5, 0.5, 0.5)  # Set the background color to white
    renderer.AddActor(patch_actor)
    renderer.AddActor(pc_actor)

    # create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # create an interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # initialize the interactor
    interactor.Initialize()
    render_window.Render()
    interactor.Start()

# %% divide the patch to smaller patches
# get the bounds of the patch
bounds = patch.GetBounds()
bounds_range = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]

# divide the patch to 32x32 smaller patches
n_patches = 32  # number of patches in each direction
PATCH_SIZE = (np.array(bounds_range) / n_patches).tolist()
patch_bounds = []
patch_centers = []

for i in range(n_patches):
    for j in range(n_patches):
        patch_bounds.append([bounds[0] + i * PATCH_SIZE[0], bounds[0] + (i + 1) * PATCH_SIZE[0],
                             bounds[2] + j * PATCH_SIZE[1], bounds[2] + (j + 1) * PATCH_SIZE[1],
                             bounds[4], bounds[5]])
        patch_centers.append([(bounds[0] + i * PATCH_SIZE[0] + bounds[0] + (i + 1) * PATCH_SIZE[0]) / 2,
                              (bounds[2] + j * PATCH_SIZE[1] + bounds[2] + (j + 1) * PATCH_SIZE[1]) / 2,
                              bounds[4]])

# %% plot the smaller patch centers on the point cloud
# Create a VTK glyph to visualize the points
if PLOT_PATCH:
    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(polydata)
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

    # Add the patch centers to the point cloud
    patch_centers_points = vtk.vtkPoints()
    for point in patch_centers:
        patch_centers_points.InsertNextPoint(point)

    patch_centers_polydata = vtk.vtkPolyData()
    patch_centers_polydata.SetPoints(patch_centers_points)

    # Create a VTK glyph to visualize the points
    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(patch_centers_polydata)
    glyph.Update()

    # set the shape of the glyph
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(0.25)  # Set the radius of the sphere
    glyph.SetSourceConnection(sphere_source.GetOutputPort())
    glyph.Update()

    # Increase the glyph size
    # glyph.SetScaleFactor(2.0)  # Adjust the scale factor as desired

    # Create a VTK mapper and actor
    centerpoint_mapper = vtk.vtkPolyDataMapper()
    centerpoint_mapper.SetInputConnection(glyph.GetOutputPort())

    centerpoint_actor = vtk.vtkActor()
    centerpoint_actor.SetMapper(centerpoint_mapper)
    centerpoint_actor.GetProperty().SetColor(1, 0, 0)  # Set point color to red


    # create a renderer
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.5, 0.5, 0.5)  # Set the background color to white
    renderer.AddActor(pc_actor)
    renderer.AddActor(centerpoint_actor)

    # create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # create an interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # initialize the interactor
    interactor.Initialize()
    render_window.Render()
    interactor.Start()

# %% find the closest points in the point cloud to the smaller patches
# Build a KD-Tree from the point cloud
tree = cKDTree(point_cloud)

closest_points_to_patch = []
distance_of_closest_points = []
for c in patch_centers:
    # find the closest point to the center of the patch
    distance, index = tree.query(c)

    closest_point = point_cloud[index]
    closest_points_to_patch.append(closest_point)
    distance_of_closest_points.append(distance)
