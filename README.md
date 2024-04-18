# PointCloud_fun, correlate ECoG activity to Leadfield matrix (LFM)

This repository contains scripts to correlate ECoG activity to Leadfield matrix (LFM) in order to estimate the spatial distribution of the ECoG activity as EEG activity. The hypothesis is that mapping ECoG activity to EEG will help us to understand the ground-truth dynamics of EEG data and help us determine the extent of the ECoG (and cortical) activity that can be captured by EEG.

## Workflow
Here is the general workflow of the scripts:

```mermaid
graph TD
    AA{{Start, get the LFM nodes from Headmodel}} --> A[delaunay3D_fit.py]
    A -->|delaunay3D_overCortex.ply| B[fit_patch.py \n select the nodes over the cortex that represents the ECoG]
    B -->|projected_patch.ply| C[closest_point_to_patch.py \n get the closest LFM nodes to the ECoG patches]
    C -->|point_to_patch_weight.pkl \n patch_centers.pkl| D[project_activity.py \n project the ECoG activity to the LFM nodes]
    
    D -->|point_activation.pkl| E{{End, use LFM transformation to get EEG activations}}
```
