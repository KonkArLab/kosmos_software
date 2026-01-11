import cv2
import numpy as np
from picamera2 import Picamera2

PLOT_HEIGHT = 200
MAX_LINE_LENGTH = 300

camera_infos = Picamera2.global_camera_info()
num_cameras = len(camera_infos)

print("Caméras CSI détectées :")
for i, info in enumerate(camera_infos):
    print(f"{i}: {info}")

current_camera = 0
picam2 = None


def start_camera(cam_index):
    global picam2

    if picam2 is not None:
        picam2.stop()
        picam2.close()

    picam2 = Picamera2(camera_num=cam_index)
    config = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (1456, 1088)}
    )
    picam2.configure(config)
    picam2.start()


start_camera(current_camera)

cv2.namedWindow("Rpi Video", cv2.WINDOW_NORMAL)
cv2.namedWindow("Profil d'intensité", cv2.WINDOW_NORMAL)

plot_bgr = np.zeros((PLOT_HEIGHT, MAX_LINE_LENGTH, 3), dtype=np.uint8)

start_point = None
end_point = None
click_count = 0


def mouse_callback(event, x, y, flags, param):
    global start_point, end_point, click_count

    if event == cv2.EVENT_LBUTTONDOWN:
        if click_count % 2 == 0:
            start_point = np.array([x, y])
            end_point = None
            plot_bgr.fill(0)
        else:
            end_point = np.array([x, y])

        click_count += 1


def on_camera_change(val):
    global current_camera, start_point, end_point, click_count

    if val != current_camera:
        current_camera = val
        start_camera(current_camera)

        start_point = None
        end_point = None
        click_count = 0
        plot_bgr.fill(0)


cv2.setMouseCallback("Rpi Video", mouse_callback)

print(f"NUM CAMERAS : {num_cameras}")

if num_cameras > 1:
    cv2.createTrackbar(
        "Camera CSI",
        "Rpi Video",
        current_camera,
        max(0, num_cameras - 1),
        on_camera_change
    )

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Affichage nom caméra
    cam_name = camera_infos[current_camera]["Model"]
    cv2.putText(
        frame,
        f"Camera {current_camera}: {cam_name}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    if start_point is not None:
        cv2.circle(frame, tuple(start_point), 4, (0, 0, 255), -1)

    if end_point is not None:
        cv2.circle(frame, tuple(end_point), 4, (255, 0, 0), -1)

    if start_point is not None and end_point is not None:
        cv2.line(frame, tuple(start_point), tuple(end_point), (255, 255, 0), 1)

        direction = end_point - start_point
        length = np.linalg.norm(direction)

        if length > 0:
            num_points = int(length)
            xs = np.linspace(start_point[0], end_point[0], num_points).astype(int)
            ys = np.linspace(start_point[1], end_point[1], num_points).astype(int)

            valid = (
                (xs >= 0) & (xs < gray.shape[1]) &
                (ys >= 0) & (ys < gray.shape[0])
            )
            xs, ys = xs[valid], ys[valid]

            intensities = gray[ys, xs]

            plot_bgr.fill(0)
            x_plot = np.linspace(0, MAX_LINE_LENGTH - 1, len(intensities)).astype(int)
            y_plot = (intensities / 255.0 * (PLOT_HEIGHT - 1)).astype(int)

            for xi, yi in zip(x_plot, y_plot):
                cv2.line(
                    plot_bgr,
                    (xi, PLOT_HEIGHT - 1),
                    (xi, PLOT_HEIGHT - 1 - yi),
                    (255, 255, 255),
                    1
                )

    cv2.imshow("Rpi Video", frame)
    cv2.imshow("Profil d'intensité", plot_bgr)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
