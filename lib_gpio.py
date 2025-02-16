import config
from gpiozero import LED, Button
import time
from functools import wraps

# button_1 = Button(pin=config.button_gpio_1)
button_2 = Button(pin=config.button_gpio_2)
button_3 = Button(pin=config.button_gpio_3)
button_4 = Button(pin=config.button_gpio_4)
button_5 = Button(pin=config.button_gpio_5)
button_6 = Button(pin=config.button_gpio_6)
button_7 = Button(pin=config.button_gpio_7,hold_time=2)
button_8 = Button(pin=config.button_gpio_8)


led_pwr = LED(pin=config.pwr_led_gpio)
led_p1 = LED(pin=config.p1_led_gpio)
led_p2 = LED(pin=config.p2_led_gpio)
led_p3 = LED(pin=config.p3_led_gpio)


button_throttle=0.20
def throttle(throttle_seconds=0):
    def throttle_decorator(fn):
        time_of_last_call = 0
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if throttle_seconds==0:
                return fn(*args, **kwargs)
            else:
                now = time.time()
                nonlocal time_of_last_call
                if now - time_of_last_call > throttle_seconds:
                    time_of_last_call = now
                    return fn(*args, **kwargs)
        return wrapper
    return throttle_decorator

def set_pled(p):
    if p==0:
        led_p1.on()
    else:
        led_p1.off()
    if p==1:
        led_p2.on()
    else:
        led_p2.off()
    if p==2:
        led_p3.on()
    else:
        led_p3.off()

def shutdown(q):
    q.put_nowait('shutdown')
    led_pwr.on()

def setup(q):
    led_pwr.off()
    led_p1.on()
    led_p2.on()
    led_p3.on()

    # button_1.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('up'))
    # button_2.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('down'))
    button_2.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('cc2'))

    button_7.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('bdown'))
    button_8.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('bup'))

    button_4.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('p1'))
    button_5.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('p2'))
    button_6.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('p3'))

    button_3.when_pressed=throttle(button_throttle)(lambda: q.put_nowait('cc1'))

    # button_7.when_held = lambda: shutdown(q)
    button_2.when_held = lambda: shutdown(q)
    button_2.when_held = lambda: shutdown(q)


if __name__=='__main__':

    # button_1.when_pressed=throttle(button_throttle)(lambda: print('up'))
    button_2.when_pressed=throttle(button_throttle)(lambda: print('down'))

    time.sleep(10)