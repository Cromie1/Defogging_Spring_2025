import gpiod
import subprocess, sys
import os
import logging
import cv2
from time import sleep
from datetime import datetime, timedelta
from picamera2 import Picamera2
import threading

from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

sleep(5)

log_file = '/home/amir/main_pilot.log'
logging.basicConfig(
	filename=log_file,
	level=logging.INFO,
	format='%(asctime) s - %(levelname)s - %(message) s'
)

def filter_log_file(file_path, max_age_hours=24):
    """Filter out log entries older than max_age_hours."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Calculate the cutoff time
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        filtered_lines = []

        for line in lines:
            try:
                # Extract the timestamp from the log line
                timestamp_str = line.split(' - ')[0]
                log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                # Keep the line if it is newer than the cutoff time
                if log_time > cutoff_time:
                    filtered_lines.append(line)
            except ValueError:
                # If timestamp parsing fails, keep the line (to avoid losing any unexpected format)
                filtered_lines.append(line)

        # Write the filtered lines back to the log file
        with open(file_path, 'w') as f:
            f.writelines(filtered_lines)

def sync():
	BLUE_LED_PIN = 27
	chip = gpiod.Chip('gpiochip4')
	blue_led_line = chip.get_line(BLUE_LED_PIN)
	blue_led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
	command = "rclone copy -v /home/amir/Pictures ClaraDrive2:claravisio_images"
	try: 
		result = subprocess.run(command, check=True, text=True, shell=True, capture_output=True)
		logging.info(result.stderr)
		blue_led_line.set_value(1)
		sleep(1)
		blue_led_line.set_value(0)
	except subprocess.CalledProcessError as cpe:
		logging.info(cpe.stderr)
	finally:
		blue_led_line.set_value(0)
		blue_led_line.release()
		

def run_periodically(interval, function):
    def wrapper():
        while True:
            function()
            threading.Event().wait(interval)
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()
    
def toggleFog(line):
	line.set_value(1)
	sleep(0.5)
	line.set_value(0)


def vidsplit(vidPath,OutputPath):
		# Read the video from specified path 
	cam = cv2.VideoCapture(vidPath) 

	if not cam.isOpened():
		logging.error(f"Error: Cannot open video file {vidPath}")
		return

	try: 
		# creating a folder named data 
		if not os.path.exists(OutputPath): 
			os.makedirs(OutputPath) 

	# if not created then raise error 
	except OSError: 
		logging.info('Error: Creating directory of data') 

	# frame 
	currentframe = 0

	last_variance = float('inf')
	every_x_variance = 5
	ret,first = cam.read()
	last_variance=cv2.Laplacian(first, cv2.CV_32F).var()
	while(True): 
		# reading from frame 
		ret,frame = cam.read()

		if ret: # if video is still left continue creating images 
			variance = cv2.Laplacian(frame, cv2.CV_32F).var()
			
			# record next variance:
			if variance < last_variance - every_x_variance:
				name =  OutputPath + '/frame' + str(currentframe) + 'var' + str(variance) + '.jpg'
				logging.info(f'Creating...' + name)
				
				stitched_image = cv2.hconcat([first, frame])

				# writing the extracted images
				cv2.imwrite(name, stitched_image) 
				success = cv2.imwrite(name, stitched_image)
				if not success:
					logging.error(f"Failed to save image: {name}")
				else:
					logging.info(f"Image saved: {name}")

				last_variance = variance    
				
			# increasing counter so that it will 
			# show how many frames are created 
			currentframe += 1
		else: 
			break

	# Release all space and windows once done 
	cam.release() 
	cv2.destroyAllWindows() 



def main():
	filter_log_file(log_file)
	logging.info('Pilot started')
	
	try:
		RED_LED_PIN = 17
		GREEN_LED_PIN = 22
		BUTTON_PIN = 10
		BLUE_LED_PIN = 27	# use "BLUE_LED_PIN" to trigger the IR remote

		picam0 = Picamera2()
		video_config = picam0.create_video_configuration(main={"size": (1920, 1080)})
		picam0.configure(video_config)
		picam0.start_preview()
		encoder = H264Encoder(bitrate=10000000)
		
		chip = gpiod.Chip('gpiochip4')

		red_led_line = chip.get_line(RED_LED_PIN)
		green_led_line = chip.get_line(GREEN_LED_PIN)
		button_line = chip.get_line(BUTTON_PIN)
		IR_remote = chip.get_line(BLUE_LED_PIN)

		red_led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
		green_led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
		button_line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
		IR_remote.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
		
		green_led_line.set_value(1)
		red_led_line.set_value(1)
		sleep(1)
		green_led_line.set_value(0)
		red_led_line.set_value(0)
		
		sleep(5)
		# run_periodically(5, sync)
		

		current_date = datetime.now().strftime('%Y-%m-%d')
		run_number = 1
		folder_name = f"/home/amir/young/videos/{current_date}_RUN{run_number}"

		while os.path.exists(folder_name):
			run_number += 1
			folder_name = f"/home/amir/young/videos/{current_date}_RUN{run_number}"

		os.makedirs(folder_name)
		# os.makedirs(f"{folder_name}/A")
		# os.makedirs(f"{folder_name}/B")
		logging.info(f"Folder created: {current_date}_RUN{run_number}")

		photo_number = 1
		recording = False

		while True:
			button_state = button_line.get_value()
			if button_state == 1:
				logging.info(f"{folder_name}/{current_date}_RUN{run_number}__{photo_number}.h264")
				output = FfmpegOutput(f"{folder_name}/{current_date}_RUN{run_number}__{photo_number}.mp4")

				#turn on fog
				toggleFog(IR_remote)
				
				#start recording
				picam0.start_recording(encoder, output)
				green_led_line.set_value(1)


				#waits 
				sleep(4)

				#stops fog
				toggleFog(IR_remote)
				
				#stops recording
				picam0.stop_recording()
				green_led_line.set_value(0)
				


				recording = not recording
				sleep(1)

				vidsplit(f"{folder_name}/{current_date}_RUN{run_number}__{photo_number}.mp4",folder_name)

				video_path = f"{folder_name}/{current_date}_RUN{run_number}__{photo_number}.mp4"  # Update with your actual video path

				if os.path.exists(video_path):
					os.remove(video_path)
					logging.info(f"Deleted video: {video_path}")
				else:
					logging.warning(f"File not found: {video_path}")

				photo_number += 1
				while os.path.exists(folder_name):
					run_number += 1
					folder_name = f"/home/amir/young/videos/{current_date}_RUN{run_number}"
				os.makedirs(folder_name)
				logging.info(f"Folder created: {current_date}_RUN{run_number}")


				
				

	except Exception as e:
		logging.error(f'An error occurred: {e}')
		red_led_line.set_value(1)
		sleep(10)
		
	finally:
		green_led_line.set_value(0)
		red_led_line.set_value(0)
		red_led_line.release()
		green_led_line.release()
		button_line.release()
		picam0.stop()
		picam0.stop_preview()
		logging.info('Program exited')

if __name__ == "__main__":
	main()
