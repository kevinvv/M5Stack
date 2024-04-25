import os
from datetime import datetime

from moviepy.editor import VideoFileClip

from logic.make_video_from_images import make_video
from logic.motion_heatmap_from_video import motion_heatmap


def main():

    os.chdir('UnitV2/')
    storage = './resources/'
    device_storage = storage + "devices/"

    devices = os.listdir(device_storage)
    devices.remove(".gitignore")
    devices.remove(".DS_Store")

    i = 0
    for device in devices:

        print(f'[{i}]: {device}')
        i += 1
    
    user_input = input(f'Choose the prefix number of the device from the list (between 0 and {len(devices) - 1}): ')
    
    chosen_device = devices[int(user_input)]
    image_location = device_storage + chosen_device
    images = os.listdir(image_location)
    
    
    total_images = len(images)
    first_image = images[0].split('-')[0]
    last_image = images[total_images - 1].split('-')[0]
    
    first_datetime = datetime.strptime(first_image, '%Y_%m_%d_%H_%M_%S')
    last_datetime = datetime.strptime(last_image, '%Y_%m_%d_%H_%M_%S')
    difference_datetime = last_datetime - first_datetime

    print(f'Device {chosen_device} has {total_images} photos taken in a timespan of {difference_datetime}')
    print('Generating Motion Heatmap')

    video_name = f'{chosen_device}_{str(datetime.now())}.avi'
    video_location = f'./{storage}videos/{video_name}'
    make_video(image_location, video_name=video_location)
    motion_heatmap(video_location, video_name)

    print("\n Generating Motion Heatmap Gif")
    videoClip = VideoFileClip(f'./{storage}videos/heatmap_{video_name}')
    videoClip.write_gif(f'./{storage}gifs/heatmap_{video_name}.gif', fps=60,program='imageio') 
    
if __name__ == '__main__':
    main()