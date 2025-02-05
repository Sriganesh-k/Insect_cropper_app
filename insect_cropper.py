import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QToolBar, QAction, QStatusBar
)
from PyQt5.QtGui import QPixmap, QImage, QPen, QColor, QIcon
from PyQt5.QtCore import Qt, QRectF

class CropGraphicsView(QGraphicsView):
    """
    Custom QGraphicsView to handle mouse events for drawing a cropping rectangle.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.origin = None
        self.cropRect = None
        self.currentRectItem = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Map the mouse press position to scene coordinates
            self.origin = self.mapToScene(event.pos())
            # Remove any existing rectangle item
            if self.currentRectItem is not None:
                self.scene().removeItem(self.currentRectItem)
                self.currentRectItem = None
            # Create a new rectangle item with a dashed red outline
            self.currentRectItem = self.scene().addRect(
                QRectF(self.origin, self.origin),
                QPen(QColor("red"), 2, Qt.DashLine)
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.origin is not None and self.currentRectItem is not None:
            # Update the rectangle as the mouse moves
            currentPos = self.mapToScene(event.pos())
            rect = QRectF(self.origin, currentPos).normalized()
            self.currentRectItem.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.origin is not None and self.currentRectItem is not None:
            # Finalize the crop rectangle
            currentPos = self.mapToScene(event.pos())
            rect = QRectF(self.origin, currentPos).normalized()
            self.cropRect = rect
            self.origin = None
        super().mouseReleaseEvent(event)

class ImageCropper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insect Image Cropper")
        self.resize(1000, 700)
        self.initUI()

    def initUI(self):
        # Create a central widget with a vertical layout
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)

        # Toolbar for quick access actions
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        # Open action
        openAction = QAction(QIcon(), "Open Image", self)
        openAction.triggered.connect(self.load_image)
        self.toolbar.addAction(openAction)

        # Save action
        saveAction = QAction(QIcon(), "Save Cropped Image", self)
        saveAction.triggered.connect(self.save_cropped_image)
        self.toolbar.addAction(saveAction)

        # Auto detect ROI using classical image processing
        autoClassicalAction = QAction(QIcon(), "Auto ROI (Classical)", self)
        autoClassicalAction.triggered.connect(self.detect_roi_classical)
        self.toolbar.addAction(autoClassicalAction)

        # Status bar for messages
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Instruction/info label
        self.infoLabel = QLabel("Load an image to start cropping or use auto detection (classical).")
        self.infoLabel.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.infoLabel)

        # Create the QGraphicsView and scene to display the image
        self.scene = QGraphicsScene(self)
        self.view = CropGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setStyleSheet("background-color: #f0f0f0;")
        mainLayout.addWidget(self.view)

        # Button layout at the bottom (in addition to the toolbar)
        buttonLayout = QHBoxLayout()
        self.loadButton = QPushButton("Load Image")
        self.loadButton.clicked.connect(self.load_image)
        buttonLayout.addWidget(self.loadButton)

        self.saveButton = QPushButton("Save Cropped Image")
        self.saveButton.clicked.connect(self.save_cropped_image)
        self.saveButton.setEnabled(False)
        buttonLayout.addWidget(self.saveButton)

        self.autoClassicalButton = QPushButton("Auto ROI (Classical)")
        self.autoClassicalButton.clicked.connect(self.detect_roi_classical)
        buttonLayout.addWidget(self.autoClassicalButton)

        mainLayout.addLayout(buttonLayout)

    def load_image(self):
        # Open a file dialog to load an image
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "",
            "Image Files (*.png *.jpg *.jpeg);;All Files (*)", options=options
        )
        if filePath:
            self.imagePath = filePath  # Store file path for further processing
            self.image = QPixmap(filePath)
            self.scene.clear()
            self.pixmapItem = QGraphicsPixmapItem(self.image)
            self.scene.addItem(self.pixmapItem)
            self.infoLabel.setText("Image loaded. Drag over the image to select a crop area or use auto detection.")
            self.saveButton.setEnabled(True)
            self.statusBar.showMessage("Image loaded.", 3000)
            # Adjust view to fit the image
            self.view.fitInView(self.pixmapItem, Qt.KeepAspectRatio)

    def save_cropped_image(self):
        # Save the manually selected crop if it exists
        if hasattr(self.view, 'cropRect') and self.view.cropRect is not None:
            cropRectF = self.view.cropRect
            cropRect = cropRectF.toRect()
            imageRect = self.pixmapItem.boundingRect().toRect()
            cropRect = cropRect.intersected(imageRect)
            if cropRect.isEmpty():
                self.statusBar.showMessage("Invalid crop area. Please select a valid region.", 3000)
                return
            croppedImage = self.image.copy(cropRect)
            options = QFileDialog.Options()
            savePath, _ = QFileDialog.getSaveFileName(
                self, "Save Cropped Image", "",
                "Image Files (*.png *.jpg *.jpeg);;All Files (*)", options=options
            )
            if savePath:
                if croppedImage.save(savePath):
                    self.statusBar.showMessage("Image saved successfully.", 3000)
                else:
                    self.statusBar.showMessage("Failed to save image.", 3000)
        else:
            self.statusBar.showMessage("No crop area selected.", 3000)

    def detect_roi_classical(self):
        """
        Use classical image processing (thresholding & contour detection)
        to auto-detect a region of interest.
        """
        if not hasattr(self, 'imagePath'):
            self.statusBar.showMessage("No image loaded.", 3000)
            return

        # Load image using OpenCV
        image_cv = cv2.imread(self.imagePath)
        if image_cv is None:
            self.statusBar.showMessage("Failed to load image with OpenCV.", 3000)
            return

        # Convert to grayscale and blur the image
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Apply thresholding to obtain a binary image
        ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Find contours from the thresholded image
        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Choose the largest contour (by area) as the ROI
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            crop_cv = image_cv[y:y+h, x:x+w]
            # Convert the cropped image from BGR to RGB
            crop_cv_rgb = cv2.cvtColor(crop_cv, cv2.COLOR_BGR2RGB)
            h_c, w_c, ch = crop_cv_rgb.shape
            bytesPerLine = ch * w_c
            qimg = QImage(crop_cv_rgb.data, w_c, h_c, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            # Update the scene with the cropped image
            self.scene.clear()
            self.pixmapItem = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmapItem)
            self.view.fitInView(self.pixmapItem, Qt.KeepAspectRatio)
            self.statusBar.showMessage("ROI detected using classical image processing.", 3000)
        else:
            self.statusBar.showMessage("No contours detected.", 3000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageCropper()
    window.show()
    sys.exit(app.exec_())
