from concurrent.futures import ThreadPoolExecutor
import time
from threading import Event, Lock
import traceback
import config
import lib_midi

data_lock = Lock()
event = Event()

STATE={
    'last_ping_in': 0,
    'last_ping_out': 0,
}
def update_state(upd):
    with data_lock:
        STATE.update(upd)
        print('STATE',STATE)
def get_state():
    with data_lock:
        res={}
        res.update(STATE)
        return res

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
def task_read_midi(inport, ip_outport):
    
    message = inport.receive(block=False)
    if not message:
        last_ping_out=get_state()['last_ping_out']
        last_ping_out+=1
        if last_ping_out>300:
            ip_outport.send(lib_midi.ping_msg())
            last_ping_out=0
            
        update_state({'last_ping_out': last_ping_out})
        time.sleep(0.015)
        return
    print(message)

    print(ip_outport.send(message))

@tf_dec
def task_write_midi(outport, ip_inport):
    
    message = ip_inport.receive(block=False)
    if not message:
        time.sleep(0.015)
        return
    print(message)

    if message.is_cc(control=config.PING_CC):
        update_state({'last_ping_in': time.time()})
        return

    print(outport.send(message))


if __name__ == "__main__":

    try:
        inport,outport=lib_midi.get_ports(config.NB_MIDI_DEVICE)
        ip_inport,ip_outport=lib_midi.get_ip_ports(config.PEDAL_IP)
    except:
        # time.sleep(3)
        raise

    with ThreadPoolExecutor(max_workers=4) as executor:
        future1 = executor.submit(task_read_midi,inport,ip_outport)
        future2 = executor.submit(task_write_midi,outport,ip_inport)
        
        try:
            result1 = future1.result()
            result2 = future2.result()
        except:
            print(traceback.format_exc())
            event.set()
            time.sleep(1)
