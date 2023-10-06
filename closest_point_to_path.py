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
    # create a vtkCubeSource object
    cube_source = vtk.vtkCubeSource()
    cube_source.SetBounds(patch_bound)
    cube_source.Update()

    # get the output of the cube source
    patch = cube_source.GetOutput()

    # get the center of the patch
    center = patch.GetCenter()

    # convert patch to vtkGenericCell
    patch_cell = vtk.vtkGenericCell()
    patch_cell.SetPoints(patch.GetPoints())

    # find the closest point
    closest_point = [0, 0, 0]
    closest_point_id = vtk.mutable(0)
    sub_id = vtk.mutable(0)
    dist2 = vtk.mutable(0)
    locator.FindClosestPoint(center, closest_point, patch_cell, closest_point_id, sub_id, dist2)
    print(f"started with cell number {i}")
    # add the closest point to the vtkPoints object
    closest_points.InsertNextPoint(closest_point)
    print(f"done with cell number {i}")
