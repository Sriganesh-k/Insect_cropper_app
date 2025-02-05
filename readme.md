# Insect Image Cropper

A simple image cropping tool built with PyQt5 and OpenCV. This application allows you to:

- **Manually Crop an Image:**  
  Drag over the image to select a region of interest.
  
- **Auto-Detect ROI (Classical):**  
  Use classical image processing techniques (thresholding and contour detection) to automatically detect a region of interest.

- **Save the Cropped Image:**  
  Save the selected or automatically detected crop to a file.

## Features

- **Graphical User Interface:**  
  Built with PyQt5 for a clean and interactive UI.
  
- **Manual Cropping:**  
  Draw a cropping rectangle over the image with your mouse.
  
- **Automatic ROI Detection:**  
  Apply classical image processing (using OpenCV) to detect the largest contour in the image.
  
- **Easy-to-Use:**  
  Simple toolbar and button layout for quick access to actions.

## Requirements

- Python 3.x
- [PyQt5](https://pypi.org/project/PyQt5/)
- [OpenCV](https://pypi.org/project/opencv-python/)
- [NumPy](https://pypi.org/project/numpy/)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/insect-image-cropper.git
   cd insect-image-cropper

2. **Install Dependencies:**

    pip install PyQt5 opencv-python numpy

3.**Run the applciation**

    python3 insect_cropper.py
