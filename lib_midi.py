import mido
from mido.sockets import PortServer, connect
import config


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
        p=k1+k2-1+add
        b1=f'U{k1:02d}-{k2}'
        b2=f'U{(k1+33):02d}-{k2}'
        b3=f'P{k1:02d}-{k2}'
        
        # print(p,b1,b2,b3)

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

def get_ip_ports(ip):
    server = PortServer('0.0.0.0', config.IP_PORT)
    external_port = connect(ip, config.IP_PORT)
    local_port = server.accept()
    return external_port, local_port

def change_preset(outport,bank,program,delta=1):

    print()
    print('cur',bank,program,get_name(bank,program))
    bank,program=shift_pos(bank,program,delta)
    print('next',bank,program,get_name(bank,program))
    print()

    set_preset(outport,bank,program)


def set_preset(outport,bank,program):

    program-=1
    print('send_midi',bank,program)
    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control=0 value={bank}')
    print(msg)
    print(outport.send(msg))

    msg=mido.Message.from_str(f'program_change channel={config.midi_channel} program={program}')
    print(msg)
    print(outport.send(msg))

def ping_msg():
    return mido.Message.from_str(f'control_change channel={config.midi_channel} control={config.PING_CC} value=0')

def send_cc(outport,cc):
    print('send_cc',cc)
    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control={cc} value=0')
    print(msg)
    print(outport.send(msg))

    print('send_cc',cc)
    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control={cc} value=127')
    print(msg)
    print(outport.send(msg))

   

if __name__=='__main__':

    print(pmap)
    print(get_name(0,1))
    print(get_name(1,1))
    print(get_name(2,1))


    print_ports()

    inport,outport=get_ports(config.midi_device)

    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control=0 value=0')
    print(msg)
    print(outport.send(msg))

    msg=mido.Message.from_str(f'program_change channel={config.midi_channel} program=1')
    print(msg)
    print(outport.send(msg))

    
    print()
    with inport as inport:
        for message in inport:
            print(message)
