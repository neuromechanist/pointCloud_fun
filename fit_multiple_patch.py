import vtk

# Load the surface
ply_reader = vtk.vtkPLYReader()
ply_reader.SetFileName('delaunay3D_overCortex.ply')
ply_reader.Update()
surface = ply_reader.GetOutput()

# Initialize visualization
renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)  # White background
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
interactor.SetInteractorStyle(interactor_style)

# Add the cortex surface to the renderer
surface_mapper = vtk.vtkPolyDataMapper()
surface_mapper.SetInputData(surface)
surface_actor = vtk.vtkActor()
surface_actor.SetMapper(surface_mapper)
surface_actor.GetProperty().SetOpacity(0.7)
renderer.AddActor(surface_actor)

# Initialize patch counter
patch_count = 0


def create_patch(left_corner):
    PATCH_SIZE = 32
    patch_bounds = [
        left_corner[0], left_corner[0] + PATCH_SIZE,
        left_corner[1], left_corner[1] + PATCH_SIZE,
        left_corner[2], left_corner[2]
    ]
    cube_source = vtk.vtkCubeSource()
    cube_source.SetBounds(patch_bounds)
    cube_source.Update()
    return cube_source.GetOutput()


def project_patch_to_surface(patch, surface):
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

    return projected_patch


def visualize_patch(projected_patch):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(projected_patch)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0, 1, 0)  # Green color
    return actor


def place_patch(obj, event):
    global patch_count
    click_position = interactor.GetEventPosition()
    picker = interactor.GetPicker()
    picker.Pick(click_position[0], click_position[1], 0, renderer)
    picked_point = picker.GetPickPosition()

    # Create and project the patch
    patch = create_patch(picked_point)
    projected_patch = project_patch_to_surface(patch, surface)

    # Visualize the patch
    patch_actor = visualize_patch(projected_patch)
    renderer.AddActor(patch_actor)

    patch_count += 1
    print(f"Patch {patch_count} placed at: {picked_point}")

    render_window.Render()


def key_press(obj, event):
    key = interactor.GetKeySym()
    if key == "q" or key == "Q":
        print(f"Total patches placed: {patch_count}")
        interactor.GetRenderWindow().Finalize()
        interactor.TerminateApp()


# Custom interactor style
class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("RightButtonPressEvent", self.right_button_press)
        self.AddObserver("KeyPressEvent", self.key_press)

    def right_button_press(self, obj, event):
        place_patch(obj, event)

    def key_press(self, obj, event):
        key_press(obj, event)


# Set up the picker
point_picker = vtk.vtkPointPicker()
interactor.SetPicker(point_picker)

# Set up the custom interaction style
custom_style = CustomInteractorStyle()
interactor.SetInteractorStyle(custom_style)

# Start the interaction
interactor.Initialize()
render_window.Render()
print("Right-click to place ECoG patches. Left-click and drag to rotate. Press 'Q' to quit.")
interactor.Start()
