# PyDebug

PyDebug is a Python script used for debugging and visualizing point cloud data
of parts accepted/rejected by various algorithms in PhotoneoLocalizationSDK
including and not limited to the model detail.

## Features

- Load point cloud data from .ply files
- Display point cloud data with various options (toggle visibility, bounding box, edges, etc.)
- Navigate through multiple point cloud data files
- Compute and log statistics of the accepted/rejected guesses
- Change background color of the visualization black/white
- Reset view to the center of the scene/point cloud

## Description

The script changes the working directory to the PhotoneoLocalizationSDK folder in the AppData directory. It then checks for the presence of a debug folder. If the debug folder is not found, an error is logged and a FileNotFoundError is raised.

The script reads point cloud data from two files: `scene_surface.ply` and `scene_boundary.ply` located in the debug folder. The point cloud data is then logged.

The script paints the scene point cloud grey and the boundary point cloud light blue.

Finally, the script creates an instance of the ItemViewer class with the scene and boundary point clouds as arguments. It then loads geometries from a directory selected by the user and runs the viewer.

## Dependencies

- Open3D for handling point cloud data
- numpy for numerical operations
- tkinter for the file dialog

## How to Run

To run the script, simply execute the `pydebug.py` file in your Python environment. Make sure all dependencies are installed.

## License

GNU/GPLv3