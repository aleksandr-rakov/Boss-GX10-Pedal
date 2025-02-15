from concurrent.futures import ThreadPoolExecutor
import time
from threading import Event, Lock
import traceback
import queue
import os
import config
import lib_gpio
import lib_midi
import lib_oled

data_lock = Lock()
event = Event()
buttonsq = queue.Queue()
screenq = queue.Queue()
ledq = queue.Queue()

STATE={
    'bank': 0,
    'program': 0,
    'shutdown': False,
}
def update_state(upd):
    with data_lock:
        STATE.update(upd)
        print('STATE',STATE)
        screenq.put_nowait(1)
        ledq.put_nowait(1)
def get_state():
    with data_lock:
        res={}
        res.update(STATE)
        return res

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds

def empty_queue(q):
    try:
        while True:
            q.get(False)
            q.task_done()
    except queue.Empty:
        pass

def tf_dec(f):
    def wrp(*args):
        try:
            while 1:
                if event.is_set():
                    return
                f(*args)
        except:
            event.set()
            print(traceback.format_exc())
            raise
    return wrp

@tf_dec
def task_read_midi(inport):
    #read midi
    
    message = inport.receive(block=False)
    if not message:
        #правильней перенести в отрисовку ?
        time.sleep(0.015)
        return
    print(message)

    if message.is_cc(control=0) and 0<=message.value<=2:
        update_state({'bank': message.value})

    elif message.type=='program_change':
        update_state({'program': message.program+1})

@tf_dec
def task_write_midi(outport):
    #write midi
     
    m=None
    try:
        m=buttonsq.get(timeout=1)
    except queue.Empty:
        pass
    else:
        buttonsq.task_done()

        state=get_state()
        print('button',m)
        if m=='up':
            lib_midi.change_preset(outport,state['bank'],state['program'],1)
        elif m=='down':
            lib_midi.change_preset(outport,state['bank'],state['program'],-1)
        
        elif m=='bup':
            lib_midi.change_preset(outport,state['bank'],state['program'],3)
        elif m=='bdown':
            lib_midi.change_preset(outport,state['bank'],state['program'],-3)

        elif m=='cc1':
            lib_midi.send_cc(outport,1)
        
        elif m=='cc2':
            lib_midi.send_cc(outport,2)

        elif m in ('p1','p2','p3'):
            t=int(m.split('p')[1])
            state_txt=lib_midi.get_name(state['bank'],state['program'])
            if '-' in state_txt:
                p=state_txt.split('-')[1]
                p=int(p)

                delta=t-p
                if delta:
                    lib_midi.set_preset(outport,state['bank'],state['program']+delta)
        
        elif m=='shutdown':
            update_state({'shutdown': True})
            os.system('/usr/sbin/poweroff')

        else:
            print(f'Ignore button {m}')

@tf_dec
def task_update_display(oled):
    #update display
 
    try:
        screenq.get(timeout=1)
    except queue.Empty:
        pass
    else:
        screenq.task_done()
        empty_queue(screenq)
        
        state=get_state()
        if state['shutdown']:
            oled.display_status('Shutdown...')
            event.set()
        else:
            state_txt=lib_midi.get_name(state['bank'],state['program'])
            oled.show_selected_preset(state_txt)
        
@tf_dec
def task_update_leds():
    #update leds
 
    try:
        ledq.get(timeout=1)
    except queue.Empty:
        pass
    else:
        ledq.task_done()
        empty_queue(ledq)
        
        state=get_state()
        state_txt=lib_midi.get_name(state['bank'],state['program'])
        if '-' in state_txt:
            p=state_txt.split('-')[1]
            lib_gpio.set_pled(int(p))
        


if __name__ == "__main__":

    oled=lib_oled.SSD1306_Display()
    oled.display_status('Init...')

    try:
        inport,outport=lib_midi.get_ports(config.midi_device)
    except:
        oled.display_status('Init WiFi...')
        try:
            outport,inport=lib_midi.get_ip_ports(config.NB_IP)
            # запустить проверку пинга
        except:
            oled.display_status('Not connected...')
            time.sleep(3)
            raise

    lib_gpio.setup(buttonsq)

    uptime=get_uptime()
    if uptime<300:
        buttonsq.put('up')
        buttonsq.put('down')

    with ThreadPoolExecutor(max_workers=4) as executor:
        future1 = executor.submit(task_read_midi,inport)
        future2 = executor.submit(task_write_midi,outport)
        future3 = executor.submit(task_update_display,oled)
        future4 = executor.submit(task_update_leds)
        
        try:
            result1 = future1.result()
            result2 = future2.result()
            result3 = future3.result()
            result4 = future4.result()
        except:
            print(traceback.format_exc())
            event.set()
            oled.display_status('Connection lost...')
            time.sleep(1)
