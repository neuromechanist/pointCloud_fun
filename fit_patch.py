# %% init
import vtk
import os
import scipy.io
import numpy as np
import csv

# Configuration flags
CREATE_NEW_PATCH = False  # Set to False to load existing patch
SHOW_EEG_SENSORS = True  # Set to True to display EEG sensor locations

# %% load the surface
# Create a vtkPLYReader object
ply_reader = vtk.vtkPLYReader()
ply_reader.SetFileName('delaunay3D_overCortex.ply')
ply_reader.Update()

# Get the output of the PLY reader
surface = ply_reader.GetOutput()

# %% Load EEG sensor locations if requested
eeg_sensors = None
if SHOW_EEG_SENSORS and os.path.exists('jc_s1.sensors'):
    try:
        mat_data = scipy.io.loadmat('jc_s1.sensors')
        print("Available keys in .mat file:", list(mat_data.keys()))
        
        # Look for 'pnt' field which should contain 208x3 array of coordinates
        if 'pnt' in mat_data:
            pnts_data = mat_data['pnt']
            print("Found electrode coordinates in 'pnt' field")
            print(f"Data shape: {pnts_data.shape}")
            
            eeg_sensors = []
            for i in range(pnts_data.shape[0]):
                try:
                    # Extract coordinates directly from the array
                    x = float(pnts_data[i, 0])
                    y = float(pnts_data[i, 1]) 
                    z = float(pnts_data[i, 2])
                    label = f"Ch{i + 1}"
                    
                    eeg_sensors.append({'x': x, 'y': y, 'z': z, 'label': label})
                except Exception as e:
                    print(f"Warning: Could not process electrode {i}: {e}")
                    continue
                    
            print(f"Successfully loaded {len(eeg_sensors)} EEG sensor locations")
            if eeg_sensors:
                print(f"Sample sensor: {eeg_sensors[0]}")
        else:
            print("Could not find 'pnt' field in .mat file")
            
    except Exception as e:
        print(f"Warning: Could not load EEG sensors: {e}")
        eeg_sensors = None

# %% get the anchor point location or load existing patch
projected_patch = None

if CREATE_NEW_PATCH:
    print("Interactive mode: Click on the surface to select patch location, then press 'q' to continue")
    
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
else:
    # Load existing patch
    if os.path.exists('projected_patch.ply'):
        print("Loading existing patch from projected_patch.ply")
        patch_reader = vtk.vtkPLYReader()
        patch_reader.SetFileName('projected_patch.ply')
        patch_reader.Update()
        projected_patch = patch_reader.GetOutput()
    else:
        print("Error: projected_patch.ply not found. Set CREATE_NEW_PATCH=True to create a new patch.")
        exit(1)

# %% Fit a patch (only when creating new patch)
if CREATE_NEW_PATCH:
    PATCH_SIZE = 32
    left_corner = point_picker.GetPickPosition()

    bounds = surface.GetBounds()

    # Calculate the patch bounds
    patch_bounds = [
        left_corner[0], left_corner[0] + PATCH_SIZE, 
        left_corner[1], left_corner[1] + PATCH_SIZE, 
        bounds[5], bounds[5]
    ]

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


# %% Function to create EEG sensor markers
def create_eeg_sensor_actors(eeg_sensors, renderer):
    """Create VTK actors for EEG sensor locations"""
    sensor_actors = []
    if eeg_sensors:
        for i, sensor in enumerate(eeg_sensors):
            # Create a sphere for each sensor
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(sensor['x'], sensor['y'], sensor['z'])
            sphere.SetRadius(5)  # Large size for visibility
            sphere.SetPhiResolution(8)
            sphere.SetThetaResolution(8)

            # Create mapper and actor
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            
            # Color the first 3 sensors (fiducial points) light green, others yellow
            if i < 3:
                actor.GetProperty().SetColor(0.5, 1, 0.5)  # Light green for fiducial points
            else:
                actor.GetProperty().SetColor(1, 1, 0)  # Yellow color for EEG sensors
                
            actor.GetProperty().SetSpecular(0.3)
            actor.GetProperty().SetSpecularPower(60)

            renderer.AddActor(actor)
            sensor_actors.append(actor)
            
            # Optionally add text labels (commented out to avoid clutter)
            # text_source = vtk.vtkVectorText()
            # text_source.SetText(sensor['label'])
            # text_mapper = vtk.vtkPolyDataMapper()
            # text_mapper.SetInputConnection(text_source.GetOutputPort())
            # text_actor = vtk.vtkActor()
            # text_actor.SetMapper(text_mapper)
            # text_actor.SetPosition(sensor['x'], sensor['y'], sensor['z'] + 1)
            # text_actor.SetScale(0.5, 0.5, 0.5)
            # renderer.AddActor(text_actor)
            
    return sensor_actors


def calculate_patch_center(projected_patch):
    """Calculate the center (centroid) of the projected patch"""
    if not projected_patch:
        return None
    
    points = projected_patch.GetPoints()
    num_points = points.GetNumberOfPoints()
    
    if num_points == 0:
        return None
    
    # Calculate centroid
    center = [0.0, 0.0, 0.0]
    for i in range(num_points):
        point = points.GetPoint(i)
        center[0] += point[0]
        center[1] += point[1]
        center[2] += point[2]
    
    center[0] /= num_points
    center[1] /= num_points
    center[2] /= num_points
    
    return center


def calculate_distances_to_sensors(patch_center, eeg_sensors):
    """Calculate Euclidean distances from patch center to each EEG sensor"""
    if not patch_center or not eeg_sensors:
        return []
    
    distances = []
    for i, sensor in enumerate(eeg_sensors):
        # Calculate Euclidean distance (L2 norm)
        dx = sensor['x'] - patch_center[0]
        dy = sensor['y'] - patch_center[1]
        dz = sensor['z'] - patch_center[2]
        
        distance = np.sqrt(dx*dx + dy * dy + dz * dz)  
        
        sensor_type = "Fiducial" if i < 3 else "EEG"
        distances.append({
            'sensor_index': i,
            'sensor_label': sensor['label'],
            'sensor_type': sensor_type,
            'distance': distance,
            'coordinates': (sensor['x'], sensor['y'], sensor['z'])
        })
    
    return distances


def save_distances_to_file(distances, patch_center, filename='patch_sensor_distances.csv'):
    """Save distance measurements to CSV file"""
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['sensor_index', 'sensor_label', 'sensor_type', 
                         'distance', 'sensor_x', 'sensor_y', 'sensor_z',
                         'patch_center_x', 'patch_center_y', 'patch_center_z']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for dist_info in distances:
                writer.writerow({
                    'sensor_index': dist_info['sensor_index'],
                    'sensor_label': dist_info['sensor_label'],
                    'sensor_type': dist_info['sensor_type'],
                    'distance': f"{dist_info['distance']:.3f}",
                    'sensor_x': f"{dist_info['coordinates'][0]:.3f}",
                    'sensor_y': f"{dist_info['coordinates'][1]:.3f}",
                    'sensor_z': f"{dist_info['coordinates'][2]:.3f}",
                    'patch_center_x': f"{patch_center[0]:.3f}",
                    'patch_center_y': f"{patch_center[1]:.3f}",
                    'patch_center_z': f"{patch_center[2]:.3f}"
                })
        print(f"Distance data saved to '{filename}'")
        return True
    except Exception as e:
        print(f"Error saving distance data: {e}")
        return False


# # Perform surface reconstruction using Poisson algorithm
# poisson = vtk.vtkPoissonReconstruction()  # vtk.vtkPoissonReconstruction is not compiled yet
# poisson.SetDepth(10)  # Set the depth parameter for the reconstruction
# poisson.SetInputData(projected_patch)
# poisson.Update()

# # Get the output of the Poisson reconstruction
# smooth_surface = poisson.GetOutput()

# %% Create final visualization
print("Creating final visualization...")

renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)  # Set the background color to white

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(1200, 800)

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
surface_actor.GetProperty().SetColor(0.8, 0.8, 0.9)  # Light blue-gray
renderer.AddActor(surface_actor)

# Add the projected patch to the renderer (if available)
if projected_patch:
    projected_patch_mapper = vtk.vtkPolyDataMapper()
    projected_patch_mapper.SetInputData(projected_patch)
    projected_patch_actor = vtk.vtkActor()
    projected_patch_actor.SetMapper(projected_patch_mapper)
    projected_patch_actor.GetProperty().SetColor(1, 0, 0)  # Bright red color
    projected_patch_actor.GetProperty().SetOpacity(0.8)
    renderer.AddActor(projected_patch_actor)
    print("Added projected patch to visualization")

# Add EEG sensors if available
if SHOW_EEG_SENSORS and eeg_sensors:
    sensor_actors = create_eeg_sensor_actors(eeg_sensors, renderer)
    print(f"Added {len(sensor_actors)} EEG sensors to visualization")

# Calculate distances between patch center and EEG sensors
if projected_patch and eeg_sensors:
    print("\n" + "="*60)
    print("DISTANCE ANALYSIS: Patch Center to EEG Sensors")
    print("="*60)
    
    # Calculate patch center
    patch_center = calculate_patch_center(projected_patch)
    if patch_center:
        print(f"Patch center coordinates: ({patch_center[0]:.3f}, {patch_center[1]:.3f}, {patch_center[2]:.3f})")
        
        # Calculate distances to all sensors
        distances = calculate_distances_to_sensors(patch_center, eeg_sensors)
        
        if distances:
            # Separate fiducials and EEG sensors for analysis
            fiducials = [d for d in distances if d['sensor_type'] == 'Fiducial']
            eeg_only = [d for d in distances if d['sensor_type'] == 'EEG']
            
            print(f"\nFiducial points (first 3 sensors):")
            for fid in fiducials:
                print(f"  {fid['sensor_label']}: {fid['distance']:.3f} units")
            
            print(f"\nEEG Sensor Distance Statistics:")
            if eeg_only:
                eeg_distances = [d['distance'] for d in eeg_only]
                print(f"  Number of EEG sensors: {len(eeg_only)}")
                print(f"  Minimum distance: {min(eeg_distances):.3f} units")
                print(f"  Maximum distance: {max(eeg_distances):.3f} units")
                print(f"  Mean distance: {np.mean(eeg_distances):.3f} units")
                print(f"  Standard deviation: {np.std(eeg_distances):.3f} units")
                
                # Find closest and farthest EEG sensors
                closest = min(eeg_only, key=lambda x: x['distance'])
                farthest = max(eeg_only, key=lambda x: x['distance'])
                print(f"  Closest EEG sensor: {closest['sensor_label']} ({closest['distance']:.3f} units)")
                print(f"  Farthest EEG sensor: {farthest['sensor_label']} ({farthest['distance']:.3f} units)")
            
            # Save distances to CSV file
            save_distances_to_file(distances, patch_center)
            
            # Add visual marker for patch center
            center_sphere = vtk.vtkSphereSource()
            center_sphere.SetCenter(patch_center[0], patch_center[1], patch_center[2])
            center_sphere.SetRadius(8)  # Slightly larger than EEG sensors
            center_sphere.SetPhiResolution(12)
            center_sphere.SetThetaResolution(12)
            
            center_mapper = vtk.vtkPolyDataMapper()
            center_mapper.SetInputConnection(center_sphere.GetOutputPort())
            
            center_actor = vtk.vtkActor()
            center_actor.SetMapper(center_mapper)
            center_actor.GetProperty().SetColor(1, 0, 1)  # Magenta color for patch center
            center_actor.GetProperty().SetSpecular(0.5)
            center_actor.GetProperty().SetSpecularPower(80)
            
            renderer.AddActor(center_actor)
            print("Added patch center marker (magenta sphere) to visualization")
            
            print(f"\nFor correlation analysis, use the 'distance' column from the CSV file")
            print("to correlate with EEG signal amplitudes or other measures.")
        else:
            print("No distance calculations could be performed.")
    else:
        print("Could not calculate patch center.")
    print("="*60)

# Add keyboard instructions
print("\nVisualization Controls:")
print("- Mouse: Rotate, zoom, pan the view")
print("- 'q' or 'Q': Quit the visualization")
print("- 'r' or 'R': Reset camera view")

# Create a callback function for the key press event


def key_press_final(obj, event):
    key = interactor.GetKeySym()
    if key == "q" or key == "Q":
        interactor.GetRenderWindow().Finalize()
        interactor.TerminateApp()
    elif key == "r" or key == "R":
        renderer.ResetCamera()
        render_window.Render()


# Add the callback function to the key press event
interactor.AddObserver("KeyPressEvent", key_press_final)

# Reset camera to show the entire scene
renderer.ResetCamera()

# Render the scene
render_window.Render()

# Start the interactor
interactor.Initialize()
interactor.Start()

# %% Save the projected patch (only when creating new patch)
if CREATE_NEW_PATCH and projected_patch:
    # Create a vtkPLYWriter object
    ply_writer = vtk.vtkPLYWriter()
    ply_writer.SetFileName('projected_patch.ply')
    ply_writer.SetInputData(projected_patch)
    ply_writer.Write()
    print("Projected patch saved to 'projected_patch.ply'")
