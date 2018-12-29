import cv2 as opencv
import Common as common
from Tracking import TemplateMatching

class CameraCapture:
    is_preview_active = False
    current_camera_frame = None
    mouse_start_pos = None
    user_rectangle = None
    template_matching = TemplateMatching()

    def __init__(self):
        # grab camera no. 0
        self.camera_capture = opencv.VideoCapture(0)
        fps = self.camera_capture.get(opencv.CAP_PROP_FPS)
        self.ms_delay = int(1000 / fps)
        opencv.namedWindow(common.preview_window_name, opencv.WINDOW_FREERATIO)
        opencv.setMouseCallback(common.preview_window_name, self.on_mouse_move)

    def on_mouse_move(self, event, x, y, flags, user_data):
        if event == opencv.EVENT_LBUTTONDOWN:
            self.template_matching.clear_template()
            self.mouse_start_pos = (x, y)
        elif flags & opencv.EVENT_FLAG_LBUTTON:
            if self.mouse_start_pos is not None:
                min_pos = min(self.mouse_start_pos[0], x), min(self.mouse_start_pos[1], y)
                max_pos = max(self.mouse_start_pos[0], x), max(self.mouse_start_pos[1], y)
                self.user_rectangle = (min_pos[0], min_pos[1], max_pos[0], max_pos[1])
        elif event == opencv.EVENT_LBUTTONUP:
            self.mouse_start_pos = None
            self.template_matching.set_template(self.current_camera_frame, self.user_rectangle)
        elif event == opencv.EVENT_RBUTTONDOWN:
            self.template_matching.clear_template()
            self.user_rectangle = None

    def start_preview(self):
        self.is_preview_active = True
        while self.is_preview_active:
            self.capture_and_display_frame()

    def stop_preview(self):
        self.is_preview_active = False

    def capture_and_display_frame(self):
        (capture_status, self.current_camera_frame) = self.camera_capture.read()
        if capture_status:
            if self.template_matching.has_template():
                self.current_camera_frame = self.template_matching.match(self.current_camera_frame)
            else:
                self.draw_user_rectangle()
            opencv.imshow(common.preview_window_name, self.current_camera_frame)
            if opencv.waitKey(self.ms_delay) == common.quit_key:
                self.stop_preview()
        else:
            print(common.capture_failed)

    def draw_user_rectangle(self):
        if self.user_rectangle is not None:
            top_left_corner = (self.user_rectangle[0], self.user_rectangle[1])
            bottom_right_corner = (self.user_rectangle[2], self.user_rectangle[3])
            opencv.rectangle(self.current_camera_frame, top_left_corner, bottom_right_corner, common.yellow, common.rectangle_thickness)

    def release(self):
        self.stop_preview()
        self.camera_capture.release()
        opencv.destroyAllWindows()
