from concurrent.futures import ThreadPoolExecutor
import time
from threading import Event, Lock
import traceback
import config
import lib_midi

event = Event()


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
def task_proxy_midi(inport, outport, dir):
    
    message = inport.receive(block=False)
    if not message:
        # time.sleep(0.015)
        return
    print(dir,message)

    # outport.send(message)



if __name__ == "__main__":

    try:
        dev_inport,dev_outport=lib_midi.get_ports('GX-10')
        prog_inport,prog_outport=lib_midi.get_virtual_ports()
    except:
        # time.sleep(3)
        raise

    with ThreadPoolExecutor(max_workers=4) as executor:
        future1 = executor.submit(task_proxy_midi,dev_inport,prog_outport,'dev->prog')
        future2 = executor.submit(task_proxy_midi,prog_inport,dev_outport,'prog->dev')
        
        try:
            result1 = future1.result()
            result2 = future2.result()
        except:
            print(traceback.format_exc())
            event.set()
            time.sleep(1)
