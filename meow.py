# Run this once in a separate file or terminal
import numpy as np
import cv2
import os

# Create data folder if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# Create a white HD image
white_image = np.ones((1080, 1920, 3), np.uint8) * 255
cv2.imwrite("data/white.jpg", white_image)
print("✅ Created data/white.jpg")