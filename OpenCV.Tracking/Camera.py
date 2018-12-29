import cv2 as opencv
import Common as common


class CameraCapture:
    is_preview_active = False
    current_camera_frame = None

    def __init__(self):
        # grab camera no. 0
        self.camera_capture = opencv.VideoCapture(0)
        fps = self.camera_capture.get(opencv.CAP_PROP_FPS)
        self.ms_delay = int(1000 / fps)
        opencv.namedWindow(common.preview_window_name, opencv.WINDOW_FREERATIO)

    def start_preview(self):
        self.is_preview_active = True
        while self.is_preview_active:
            self.capture_and_display_frame()

    def stop_preview(self):
        self.is_preview_active = False

    def capture_and_display_frame(self):
        (capture_status, self.current_camera_frame) = self.camera_capture.read()
        if capture_status:
            opencv.imshow(common.preview_window_name, self.current_camera_frame)
            if opencv.waitKey(self.ms_delay) == common.quit_key:
                self.stop_preview()
        else:
            print(common.capture_failed)

    def release(self):
        self.stop_preview()
        self.camera_capture.release()
        opencv.destroyAllWindows()
