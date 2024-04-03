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
bounds_range = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]

# divide the patch to 32x32 smaller patches
NUM_PATCHES = 32  # number of patches in each direction
PATCH_SIZE = (np.array(bounds_range) / NUM_PATCHES).tolist()
patch_bounds = []
patch_centers = []

for i in range(NUM_PATCHES):
    for j in range(NUM_PATCHES):
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

num_patches = len(patch_centers)
NUMBER_OF_CLOSEST_POINTS = 10
closest_points_index = np.zeros((num_patches, NUMBER_OF_CLOSEST_POINTS))
closest_points_to_patch = np.zeros((num_patches, NUMBER_OF_CLOSEST_POINTS, 3))
distance_of_closest_points = np.zeros((num_patches, NUMBER_OF_CLOSEST_POINTS))

for i, c in enumerate(patch_centers):
    # find the closest point to the center of the patch
    distance, index = tree.query(c, NUMBER_OF_CLOSEST_POINTS)

    # get the closest points
    closest_points_index[i, :] = index
    closest_points_to_patch[i, :, :] = point_cloud[index, :]
    distance_of_closest_points[i, :] = distance

# %% Give weight to the closest points based on the squared distance
# The closest points are weighted based on the squared distance to the patch center.
# The weight is calculated as the inverse of the squared distance.
# The weight is normalized to sum to 1.
# The weight is used to calculate the projected activity of the patch to the point cloud.

# calculate the weight of the closest points
weight_of_closest_points = 1 / distance_of_closest_points**2
weight_of_closest_points = weight_of_closest_points / np.sum(weight_of_closest_points, axis=1)[:, np.newaxis]

# %% choose unique points for each patch
# Each smaller path should only correspond to one point in the point cloud.
# For each patch, if use the next closest point if the closest point is already used for the previous patches.
# If the next closest point is also used, use the next closest point.

# initialize the index of the closest points
unique_closest_point_index = np.zeros(num_patches, dtype=int)
unique_closest_point_to_patch = np.zeros((num_patches, 3))
unique_distance_of_closest_point = np.zeros(num_patches)

# initialize the used points
used_points_index = np.zeros(NUM_PATCHES**2)

for i in range(num_patches):
    # find if the closest points are used before
    used_flag = [True if index in used_points_index else False for index in closest_points_index[i, :]]
    # find the index of the closest point that is not used before
    if not all(used_flag):
        unique_closest_point_index[i] = closest_points_index[i, np.where(np.logical_not(used_flag))[0][0]]
        unique_closest_point_to_patch[i, :] = closest_points_to_patch[i, np.where(np.logical_not(used_flag))[0][0], :]
        unique_distance_of_closest_point[i] = distance_of_closest_points[i, np.where(np.logical_not(used_flag))[0][0]]
        used_points_index[i] = unique_closest_point_index[i]

# %% for the (non-unique) closest points above, find the patches that they belong to.
# It turns out that many of the closest points are used for multiple patches.
# Therefore, the `unique_closest_point_index` is often empty for many patches.
# So, we need to solve the problem in an inverse way. For each point in the point cloud, 
# find the patches that they belong to. Also, include the distance of the point to the patches.
# We can use `closest_points_index` and `distance_of_closest_points` for this purpose.
# The algorithm is as follows:
        # 1. Find the points that are closest to the patches from the `closest_points_index`.
        # 2. Create a dictionary with the point index as the key and the patch index and the distance as the value.
        # 3. For each point, find the patches that they belong to and the distance to the patches.
        # * It is possible that a patch is close to multiple points. The patch can be present for multiple points.

# create a dictionary with the point index as the key and the patch index and the distance as the value
point_to_patch = {}
point_to_patch_weight = {}
for i, c in enumerate(patch_centers):
    for j in range(NUMBER_OF_CLOSEST_POINTS):
        if closest_points_index[i, j] in point_to_patch:
            point_to_patch[closest_points_index[i, j]].append((i, distance_of_closest_points[i, j]))
            point_to_patch_weight[closest_points_index[i, j]].append((i, weight_of_closest_points[i, j]))
        else:
            point_to_patch[closest_points_index[i, j]] = [(i, distance_of_closest_points[i, j])]
            point_to_patch_weight[closest_points_index[i, j]] = [(i, weight_of_closest_points[i, j])]

# %% save the point_to_patch and point_to_patch_weight
import pickle
with open('point_to_patch.pkl', 'wb') as f:
    pickle.dump(point_to_patch, f)
with open('point_to_patch_weight.pkl', 'wb') as f:
    pickle.dump(point_to_patch_weight, f)
