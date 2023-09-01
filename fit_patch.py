import vtk
import numpy as np

# %% Load the point cloud
point_cloud = np.loadtxt('jcFS_ss_no-orientation.dip')
# %% load the surface
# Create a vtkPLYReader object
ply_reader = vtk.vtkPLYReader()
ply_reader.SetFileName('surface.ply')
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

# # %% Fit a patch
# PATCH_SIZE = 32
