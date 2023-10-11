# Description: find the closest points of a point cloud to a surface patch.
# Algorithm:
# 1. Load the surface patch and the point cloud.
# 2. Divide the patch to 32x32 smaller patches.
# 3. For each smaller patch, find the closest point in the point cloud.
# 4. Determine if the closest point is at either side of the patch.
# 5. Find the index of the closest points in the point cloud and correlate that to the index of the small patch.
# %% initilize
# load the patch and the point cloud
import vtk
import numpy as np

PLOT_PATCH = False
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

# divide the patch to 32x32 smaller patches
PATCH_SIZE = 32
n_patches = 32
patch_bounds = []

for i in range(n_patches):
    for j in range(n_patches):
        patch_bounds.append([bounds[0] + i * PATCH_SIZE, bounds[0] + (i + 1) * PATCH_SIZE,
                             bounds[2] + j * PATCH_SIZE, bounds[2] + (j + 1) * PATCH_SIZE,
                             bounds[4], bounds[4]])

# %% find the closest points in the point cloud to the smaller patches
# create a vtkCellLocator object
locator = vtk.vtkCellLocator()
locator.SetDataSet(polydata)
locator.BuildLocator()

# create a vtkPoints object to store the closest points
closest_points = vtk.vtkPoints()

# find the closest points
for i, patch_bound in enumerate(patch_bounds):
    # Compute the center of the bounding box
    center = [
        (patch_bound[0] + patch_bound[1]) / 2,
        (patch_bound[2] + patch_bound[3]) / 2,
        (patch_bound[4] + patch_bound[5]) / 2
    ]

    # find the closest point
    closest_point = [0, 0, 0]
    closest_point_id = vtk.mutable(0)
    sub_id = vtk.mutable(0)
    dist2 = vtk.mutable(0)
    locator.FindClosestPoint(center, closest_point, vtk.vtkGenericCell(), closest_point_id, sub_id, dist2)

    print(f"started with cell number {i}")
    # add the closest point to the vtkPoints object
    closest_points.InsertNextPoint(closest_point)
    print(f"done with cell number {i}")

# find the closest points
# for i, patch_bound in enumerate(patch_bounds):
#     # create a vtkCubeSource object
#     cube_source = vtk.vtkCubeSource()
#     cube_source.SetBounds(patch_bound)
#     cube_source.Update()

#     # get the output of the cube source
#     patch = cube_source.GetOutput()

#     # get the center of the patch
#     center = patch.GetCenter()

#     # convert patch to vtkGenericCell
#     patch_cell = vtk.vtkGenericCell()
#     patch_cell.SetPoints(patch.GetPoints())

#     # find the closest point
#     closest_point = [0, 0, 0]
#     closest_point_id = vtk.mutable(0)
#     sub_id = vtk.mutable(0)
#     dist2 = vtk.mutable(0)
#     locator.FindClosestPoint(center, closest_point, patch_cell, closest_point_id, sub_id, dist2)
#     print(f"started with cell number {i}")
#     # add the closest point to the vtkPoints object
#     closest_points.InsertNextPoint(closest_point)
#     print(f"done with cell number {i}")

# %%
