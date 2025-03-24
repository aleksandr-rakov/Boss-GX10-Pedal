import argparse
import time
import mido
from mido.sockets import PortServer, connect

PING_MSG=mido.Message.from_str(f'control_change control=99 value=0')

def check_midi_port(midi_port_name):
    available_ports=mido.get_input_names()
    if not midi_port_name in available_ports:
        raise Exception(f'MIDI port "{midi_port_name}" not found')

def get_midi_port(midi_port_name):
    try:
        midi_port=mido.open_ioport(midi_port_name)
    except:
        # available_ports=mido.get_input_names()
        # print('available_ports',available_ports)
        raise
    return midi_port

def get_virtual_midi_port(midi_port_name):
    midi_port=mido.open_ioport(midi_port_name,virtual=True)
    return midi_port

def trys(n,f,*args,**kwargs):
    n=0
    while 1:
        n+=1
        # print('try',n)
        try:
            res= f(*args,**kwargs)
        except:
            if n>=5:
                print(f'{f.__name__} failed after {n} trys')
                raise
            time.sleep(1)
            pass
        else:
            print(f'{f.__name__} ok on {n} try')
            break
    return res 

def get_ip_client_port(connect_to):
    ip_addr,ip_port=connect_to.split(':')
    external_port = connect(ip_addr,int(ip_port))
    print('connected')
    return external_port

def get_ip_server_port(bind_port):
    print(f'Listening on 0.0.0.0:{bind_port}')
    server = PortServer('0.0.0.0', int(bind_port))
    local_port = server.accept()
    print('connection accepted')
    return local_port

def route_midi_loop(local_port,remote_port,check_port=False):
    last_ping_in=last_ping_out=time.time()
    while 1:
        msgcount=0
        for msg in local_port.iter_pending():
            print('local to remote',msg)
            remote_port.send(msg)
            msgcount+=1
            break
        for msg in remote_port.iter_pending():
            if msg==PING_MSG:
                last_ping_in=time.time()
                continue
            
            print('remote to local',msg)
            local_port.send(msg)
            msgcount+=1
            break
        if not msgcount:
            time.sleep(0.01)
            t=time.time()

            if t-last_ping_in>30:
                print('Ping lost')
                raise Exception('Ping lost')
            
            if t-last_ping_out>5:
                if check_port:
                    check_midi_port(check_port)

                last_ping_out=time.time()
                remote_port.send(PING_MSG)

def run_proxy_loop(connect_to,bind_port,midi_port_name):
    check_port=None
    if connect_to:
        local_port=get_virtual_midi_port(midi_port_name)
        remote_port=trys(5,get_ip_client_port,connect_to)
    else:
        check_port=midi_port_name
        local_port=trys(5,get_midi_port,midi_port_name)
        remote_port=get_ip_server_port(bind_port)

    route_midi_loop(local_port,remote_port,check_port)

if __name__=='__main__':
    parser =argparse.ArgumentParser('midi_ip')
    parser.add_argument('--connect-to', help='ip:port to connect')
    parser.add_argument('--bind-port', help='TCP port')
    parser.add_argument('--midi-port-name', help='MIDI port name')
    parser.add_argument('--list-midi-ports', action='store_true', help='list MIDI ports and exit')
    args=parser.parse_args()
    # print(args)

    if args.list_midi_ports:
        # parser.print_usage()
        available_ports=mido.get_input_names()
        print(available_ports)
        exit(0)
    
    if args.connect_to and args.bind_port:
        parser.print_usage()
        print('Select only one of connect-to bind-port')
        exit(1)
    if not (args.connect_to or args.bind_port):
        parser.print_usage()
        print('Select one of connect-to bind-port')
        exit(1)
    if not args.midi_port_name:
        parser.print_usage()
        print('Seelct midi-port-name')
        exit(1)

    run_proxy_loop(args.connect_to,args.bind_port,args.midi_port_name)
