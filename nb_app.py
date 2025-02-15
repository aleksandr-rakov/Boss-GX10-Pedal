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
def update_state(upd, silent=False):
    with data_lock:
        STATE.update(upd)
        if not silent:
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
        state=get_state()
        last_ping_out=state['last_ping_out']
        last_ping_out+=1
        if last_ping_out>300:
            if state['last_ping_in']>0 and state['last_ping_in']+20<time.time():
                raise Exception('Ping lost')
            # print('ping out')
            ip_outport.send(lib_midi.ping_msg())
            last_ping_out=0
            
        update_state({'last_ping_out': last_ping_out},True)
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

    if message.is_cc(control=config.PING_CC):
        # print('ping in')
        update_state({'last_ping_in': time.time()},True)
        return

    print(message)
    print(outport.send(message))


if __name__ == "__main__":

    try:
        inport,outport=lib_midi.get_ports(config.NB_MIDI_DEVICE)
        ip_outport=lib_midi.get_ip_client_port(config.PEDAL_IP)
        ip_inport=lib_midi.get_ip_server_port()
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
