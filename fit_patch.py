import vtk

# %% load the surface
# Create a vtkPLYReader object
ply_reader = vtk.vtkPLYReader()
ply_reader.SetFileName('delaunay3D_overCortex.ply')
ply_reader.Update()

# Get the output of the PLY reader
surface = ply_reader.GetOutput()

# %% get the anchor point location
# Create a renderer
renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)  # Set the background color to white

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Set the interactor style to trackball camera
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
interactor.SetInteractorStyle(interactor_style)

# Add the surface to the renderer
surface_mapper = vtk.vtkPolyDataMapper()
surface_mapper.SetInputData(surface)
surface_actor = vtk.vtkActor()
surface_actor.SetMapper(surface_mapper)
renderer.AddActor(surface_actor)

# Create a point picker
point_picker = vtk.vtkPointPicker()

# Set the point picker for the interactor
interactor.SetPicker(point_picker)


# Create a callback function for the left button press event
def left_button_press(obj, event):
    click_position = interactor.GetEventPosition()
    picker = interactor.GetPicker()
    picker.Pick(click_position[0], click_position[1], 0, renderer)
    picked_point = picker.GetPickPosition()
    print("Selected point:", picked_point)

    # Create a marker at the selected point
    marker = vtk.vtkSphereSource()
    marker.SetCenter(picked_point)
    marker.SetRadius(0.01)  # Adjust the size of the marker as needed

    marker_mapper = vtk.vtkPolyDataMapper()
    marker_mapper.SetInputConnection(marker.GetOutputPort())

    marker_actor = vtk.vtkActor()
    marker_actor.SetMapper(marker_mapper)
    marker_actor.GetProperty().SetColor(1, 0, 0)  # Set the marker to red

    renderer.AddActor(marker_actor)
    render_window.Render()


# Add the callback function to the left button press event
interactor.AddObserver("LeftButtonPressEvent", left_button_press)


# Create a callback function for the key press event
def key_press(obj, event):
    key = interactor.GetKeySym()
    if key == "q" or key == "Q":
        interactor.GetRenderWindow().Finalize()
        interactor.TerminateApp()


# Add the callback function to the key press event
interactor.AddObserver("KeyPressEvent", key_press)

# Start the interactor
interactor.Initialize()
render_window.Render()
interactor.Start()

# %% Fit a patch
PATCH_SIZE = 32
left_corner = point_picker.GetPickPosition()

bounds = surface.GetBounds()

# Calculate the patch bounds
patch_bounds = [left_corner[0], left_corner[0] + PATCH_SIZE, left_corner[1], left_corner[1] + PATCH_SIZE, bounds[5], bounds[5]]

# Create a vtkCubeSource object
cube_source = vtk.vtkCubeSource()
cube_source.SetBounds(patch_bounds)
cube_source.Update()

# Get the output of the cube source
patch = cube_source.GetOutput()

# Project the patch onto the surface
implicit_distance = vtk.vtkImplicitPolyDataDistance()
implicit_distance.SetInput(surface)
projected_patch = vtk.vtkPolyData()
projected_patch.SetPoints(patch.GetPoints())
projected_patch.Allocate(patch.GetNumberOfCells(), 1)
for i in range(patch.GetNumberOfCells()):
    cell = patch.GetCell(i)
    projected_patch.InsertNextCell(cell.GetCellType(), cell.GetPointIds())

for i in range(patch.GetNumberOfPoints()):
    point = patch.GetPoint(i)
    distance = implicit_distance.EvaluateFunction(point)
    projected_point = [point[j] - distance * implicit_distance.FunctionGradient(point)[j] for j in range(3)]
    projected_patch.GetPoints().SetPoint(i, projected_point)


# # Perform surface reconstruction using Poisson algorithm
# poisson = vtk.vtkPoissonReconstruction()  # vtk.vtkPoissonReconstruction is not compiled yet
# poisson.SetDepth(10)  # Set the depth parameter for the reconstruction
# poisson.SetInputData(projected_patch)
# poisson.Update()

# # Get the output of the Poisson reconstruction
# smooth_surface = poisson.GetOutput()

# %% Create a renderer
renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)  # Set the background color to white

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Set the interactor style to trackball camera
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
interactor.SetInteractorStyle(interactor_style)

# Add the surface to the renderer
surface_mapper = vtk.vtkPolyDataMapper()
surface_mapper.SetInputData(surface)
surface_actor = vtk.vtkActor()
surface_actor.SetMapper(surface_mapper)
surface_actor.GetProperty().SetOpacity(0.7)
renderer.AddActor(surface_actor)

# Add the projected patch to the renderer
projected_patch_mapper = vtk.vtkPolyDataMapper()
projected_patch_mapper.SetInputData(projected_patch)
projected_patch_actor = vtk.vtkActor()
projected_patch_actor.SetMapper(projected_patch_mapper)
projected_patch_actor.GetProperty().SetColor(0, 1, 0)  # Set the color to green
renderer.AddActor(projected_patch_actor)

# # Add the smooth surface to the renderer
# smooth_surface_mapper = vtk.vtkPolyDataMapper()
# smooth_surface_mapper.SetInputData(smooth_surface)
# smooth_surface_actor = vtk.vtkActor()
# smooth_surface_actor.SetMapper(smooth_surface_mapper)
# smooth_surface_actor.GetProperty().SetColor(0, 1, 0)  # Set the color to green
# renderer.AddActor(smooth_surface_actor)

# Render the scene
render_window.Render()

# Start the interactor
interactor.Initialize()
interactor.Start()

# %% Save the projected patch
# Create a vtkPLYWriter object
ply_writer = vtk.vtkPLYWriter()
ply_writer.SetFileName('projected_patch.ply')
ply_writer.SetInputData(projected_patch)
ply_writer.Write()
