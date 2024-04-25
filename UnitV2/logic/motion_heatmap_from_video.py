import numpy as np
import cv2
import copy
from .make_video_from_images import make_video
from progress.bar import Bar

# This code is an adaptation of the [Intel Motion Heatmap](https://github.com/intel-iot-devkit/python-cv-samples/tree/master/examples/motion-heatmap)

def motion_heatmap(video_location, video_name):
    capture = cv2.VideoCapture(video_location)
    background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
    length = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    bar = Bar('Processing Frames', max=length)

    first_iteration_indicator = 1
    for i in range(0, length):

        ret, frame = capture.read()

        # If first frame
        if first_iteration_indicator == 1:

            first_frame = copy.deepcopy(frame)
            height, width = frame.shape[:2]
            accum_image = np.zeros((height, width), np.uint8)
            first_iteration_indicator = 0
        else:

            filter = background_subtractor.apply(frame)  # remove the background
            cv2.imwrite('./resources/frame.jpg', frame)
            cv2.imwrite('./resources/diff-bkgnd-frame.jpg', filter)

            threshold = 2
            maxValue = 4
            ret, th1 = cv2.threshold(filter, threshold, maxValue, cv2.THRESH_BINARY)

            # add to the accumulated image
            accum_image = cv2.add(accum_image, th1)
            cv2.imwrite('./resources/mask.jpg', accum_image)

            color_image_video = cv2.applyColorMap(accum_image, cv2.COLORMAP_HOT)

            video_frame = cv2.addWeighted(frame, 0.7, color_image_video, 0.5, 0)
            # video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)

            name = "./resources/frames/frame%d.jpg" % i
            cv2.imwrite(name, video_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        bar.next()

    bar.finish()

    make_video('./resources/frames/', f'./resources/videos/heatmap_{video_name}')

    color_image = cv2.applyColorMap(accum_image, cv2.COLORMAP_HOT)
    result_overlay = cv2.addWeighted(first_frame, 0.7, color_image, 0.7, 0)

    # save the final heatmap
    cv2.imwrite('resources/diff-overlay.jpg', result_overlay)

    # cleanup
    capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    motion_heatmap()
