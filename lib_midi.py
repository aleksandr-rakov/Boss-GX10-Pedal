import mido
from mido.sockets import PortServer, connect
import config
import time
import timeout_decorator

"""
p   bank1 bank2 bank3

pc1 u01-1 u34-1 p01-1
...

pc99 u33-3 u66-3 p33-3
"""
pmap={}
pl1=[]
pl2=[]
pl3=[]
add=0
for k1 in range(1,34):
    for k2 in range(1,4):
        b1=f'U{k1:02d}-{k2}'
        b2=f'U{(k1+33):02d}-{k2}'
        b3=f'P{k1:02d}-{k2}'

        p=k1+k2-1+add
        pmap[0,p]=b1
        pmap[1,p]=b2
        pmap[2,p]=b3
        
        pl1.append((0,p))
        pl2.append((1,p))
        pl3.append((2,p))

    add+=2

plist=pl1+pl2+pl3
plist_len=len(plist)

def shift_pos(bank,program,delta=1):
    try:
        cur=plist.index((bank,program))
    except ValueError:
        cur=0

    new_pos=cur+delta
    if new_pos<0:
        return plist[plist_len+new_pos]
    elif new_pos>=plist_len:
        return plist[-plist_len+new_pos]
    else:
        return plist[new_pos]

def get_name(bank,program):
    return pmap.get((bank,program),f'{bank}:{program}')

def print_ports():
    names = mido.get_input_names()
    print(names)

def get_ports(portname):

    return mido.open_input(portname), mido.open_output(portname)

def get_virtual_ports():
    outport=mido.open_output('GX-10', virtual=True)
    inport=mido.open_input('GX-10')
    # inport=mido.open_input('GX-10 (DAW)',virtual=True)
    return inport,outport

@timeout_decorator.timeout(10)
def get_ip_server_port():
    server = PortServer('0.0.0.0', config.IP_PORT)
    local_port = server.accept()
    print('connection accepted')
    return local_port

def get_ip_client_port(ip):
    n=0
    while 1:
        n+=1
        print('try',n)
        try:
            external_port = connect(ip, config.IP_PORT)
        except:
            if n>5:
                raise
            time.sleep(1)
            pass
        else:
            print('connected')
            break
    return external_port

def change_preset(outport,bank,program,delta=1):

    print()
    print('cur',bank,program,get_name(bank,program))
    bank,program=shift_pos(bank,program,delta)
    print('next',bank,program,get_name(bank,program))
    print()

    set_preset(outport,bank,program)


def set_preset(outport,bank,program):

    program-=1
    print('send_midi_preset',bank,program)
    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control=0 value={bank}')
    print(msg)
    outport.send(msg)

    msg=mido.Message.from_str(f'program_change channel={config.midi_channel} program={program}')
    print(msg)
    outport.send(msg)

def ping_msg():
    return mido.Message.from_str(f'control_change channel={config.midi_channel} control={config.PING_CC} value=0')

def send_cc(outport,cc):
    print('send_midi_cc',cc)
    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control={cc} value=0')
    print(msg)
    outport.send(msg)

    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control={cc} value=127')
    print(msg)
    outport.send(msg)

   

if __name__=='__main__':

    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    print(pmap)
    print()

    for c in chunker(plist,3):
        print(c)
    print()


    for c in chunker(plist,3):
        print([pmap[x] for x in c])
    print()



    print(get_name(0,0))
    print(get_name(1,0))
    print(get_name(2,0))
    print()


    def sp(bank,program,delta):
        new=shift_pos(bank,program,delta)
        print(bank,program,delta,new)
        
    sp(2,0,1)
    sp(2,0,-1)
    print()




    print_ports()

    inport,outport=get_ports(config.midi_device)

    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control=0 value=0')
    print(msg)
    outport.send(msg)

    msg=mido.Message.from_str(f'program_change channel={config.midi_channel} program=1')
    print(msg)
    outport.send(msg)

    
    print()
    with inport as inport:
        for message in inport:
            print(message)
