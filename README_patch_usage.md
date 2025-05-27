# Patch Fitting and EEG Visualization Tool

This updated `fit_patch.py` script provides enhanced functionality for working with cortical surface patches and EEG sensor visualization.

## Features

1. **Interactive or Load Mode**: Create new patches interactively or load existing ones
2. **EEG Sensor Visualization**: Display EEG electrode locations on the cortex and patch
3. **Enhanced Controls**: Better visualization controls and user interface

## Configuration

Edit the configuration flags at the top of `fit_patch.py`:

```python
# Configuration flags
CREATE_NEW_PATCH = True   # Set to False to load existing patch
SHOW_EEG_SENSORS = True   # Set to True to display EEG sensor locations
```

## Usage Modes

### 1. Create New Patch (Interactive Mode)
Set `CREATE_NEW_PATCH = True`

- Run the script
- Click on the cortical surface to select patch location
- Press 'q' to proceed with patch creation
- The patch will be projected onto the surface and saved as `projected_patch.ply`

### 2. Load Existing Patch
Set `CREATE_NEW_PATCH = False`

- Requires `projected_patch.ply` to exist in the same directory
- The script will load and display the existing patch
- No interactive selection needed

## EEG Sensor Visualization

When `SHOW_EEG_SENSORS = True`:

- The script will load electrode locations from `jc_s1.sensors` (MATLAB file)
- Yellow spheres will represent each EEG sensor location
- Sensors are displayed over both the cortical surface and patch

## Required Files

- `delaunay3D_overCortex.ply`: The cortical surface mesh
- `jc_s1.sensors`: MATLAB file containing EEG electrode locations (optional)
- `projected_patch.ply`: Saved patch file (created or loaded)

## Controls

### Interactive Patch Creation:
- **Left Click**: Select patch location
- **Mouse**: Rotate, zoom, pan
- **Q**: Quit and proceed to patch creation

### Final Visualization:
- **Mouse**: Rotate, zoom, pan the view
- **Q**: Quit the visualization
- **R**: Reset camera view

## Dependencies

- `vtk`: For 3D visualization and mesh processing
- `scipy`: For loading MATLAB files
- `numpy`: For numerical operations

## File Structure

The script expects these files in the same directory:
```
pointCloud_fun/
├── fit_patch.py
├── delaunay3D_overCortex.ply
├── jc_s1.sensors (optional)
└── projected_patch.ply (created/loaded)
```

## Output

- **projected_patch.ply**: The projected patch mesh (when creating new patches)
- **Console output**: Information about loaded sensors and processing steps
- **3D visualization**: Interactive display of cortex, patch, and EEG sensors 