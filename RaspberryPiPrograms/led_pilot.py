import gpiod

RED_LED_PIN = 17
BLUE_LED_PIN = 27
GREEN_LED_PIN = 22
BUTTON_PIN = 10

chip = gpiod.Chip('gpiochip4')

red_led_line = chip.get_line(RED_LED_PIN)
blue_led_line = chip.get_line(BLUE_LED_PIN)
green_led_line = chip.get_line(GREEN_LED_PIN)
button_line = chip.get_line(BUTTON_PIN)

red_led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
blue_led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
green_led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
button_line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

try:
	while True:
		button_state = button_line.get_value()
		red_led_line.set_value(1)
		if button_state == 1:
			green_led_line.set_value(1)
		else:
			green_led_line.set_value(0)
finally:
	green_led_line.set_value(0)
	red_led_line.set_value(0)
	blue_led_line.set_value(0)
	red_led_line.release()
	green_led_line.release()
	blue_led_line.release()
	button_line.release()
