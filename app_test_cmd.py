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

# @tf_dec
def task_send_midi(outport):
    import mido

#     message=mido.Message('sysex', data= (65,16,0,0,0,0,11,17,16,0,0,0,0,0,0,16,96) )


#     # message=mido.Message('sysex', data= (65,16,0,0,0,0,11,18,0,0,0,0,0,0,12,4,112) )

# # prog->dev sysex data=(65,16,0,0,0,0,11,18,0,0,0,0,0,0,12,4,112) time=0
# # # prog->dev sysex data=(65,16,0,0,0,0,11,17,16,0,0,0,0,0,0,16,96) time=0
# # prog->dev sysex data=(65,16,0,0,0,0,11,17,0,0,0,0,0,0,0,4,124) time=0
# # prog->dev sysex data=(65,16,0,0,0,0,11,17,16,0,0,0,0,0,0,16,96) time=0

# # prog->dev sysex data=(65,16,0,0,0,0,11,17,16,0,0,105,0,0,0,20,115) time=0
# # prog->dev sysex data=(126,127,6,1) time=0
#     # message= mido.Message.from_str('control_change channel=0 control=32 value=0 time=0')

#     outport.send(message)


    msg=mido.Message.from_str(f'control_change control=0 value=0')
    print(msg)
    outport.send(msg)

    msg=mido.Message.from_str(f'program_change program=0')
    print(msg)
    outport.send(msg)


    time.sleep(3)

@tf_dec
def task_read_midi(inport):
    
    message = inport.receive(block=False)
    if not message:
        # time.sleep(0.015)
        return
    print('received',message)
    try:
        print('p',lib_midi.parse_sysex(str(message)))
    except:
        print('print failed')



if __name__ == "__main__":

    try:
        dev_inport,dev_outport=lib_midi.get_ports('GX-10')
    except:
        # time.sleep(3)
        raise

    with ThreadPoolExecutor(max_workers=4) as executor:
        future1 = executor.submit(task_send_midi,dev_outport)
        future2 = executor.submit(task_read_midi,dev_inport)
        
        try:
            result1 = future1.result()
            result2 = future2.result()
        except:
            print(traceback.format_exc())
            event.set()
            time.sleep(1)
