from Camera import CameraCapture

if __name__ == "__main__":
    camera_capture = CameraCapture()
    camera_capture.start_preview()

    camera_capture.release()
