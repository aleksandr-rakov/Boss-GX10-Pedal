import mido
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
        b1=f'U{k1:02d}-{k2}'
        b2=f'U{(k1+33):02d}-{k2}'
        b3=f'P{k1:02d}-{k2}'

        p=k1+k2-2+add
        pmap[0,p]=b1
        pmap[1,p]=b2
        pmap[2,p]=b3
        
        pl1.append((0,p))
        pl2.append((1,p))
        pl3.append((2,p))

    add+=2

plist=pl1+pl2+pl3
plist_len=len(plist)
pmap_rev={v:k for k,v in pmap.items()}

pmap2={}
b=p=1
c1=c2=c3=0
while 1:
    v=f'{b>66 and "P" or "U"}{b>66 and b-66 or b:02d}-{p}'
    k=('0',str(c1),str(c2),str(c3))
    # print(v,k)
    pmap2[k]=v

    p+=1
    if p>3:
        p=1
        b+=1
        if b>99:
            break
    c3+=1
    if c3>15:
        c3=0
        c2+=1
    if c2>15:
        c2=0
        c1+=1

    if (c1,c2,c3)==(0, 12, 6):
        c3=8


def get_bank_program(pname):
    return pmap_rev.get(pname,(0,0))

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

def get_device_names():
    names = mido.get_input_names()
    return names

def get_ports(portname):
    return mido.open_input(portname), mido.open_output(portname)


def change_preset(outport,bank,program,delta=1):

    print()
    print('cur',bank,program,get_name(bank,program))
    bank,program=shift_pos(bank,program,delta)
    print('next',bank,program,get_name(bank,program))
    print()

    set_preset(outport,bank,program)


def set_preset(outport,bank,program):

    print('send_midi_preset',bank,program)
    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control=0 value={bank}')
    print(msg)
    outport.send(msg)

    msg=mido.Message.from_str(f'program_change channel={config.midi_channel} program={program}')
    print(msg)
    outport.send(msg)

def send_cc(outport,cc):
    print('send_midi_cc',cc)
    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control={cc} value=0')
    print(msg)
    outport.send(msg)

    msg=mido.Message.from_str(f'control_change channel={config.midi_channel} control={cc} value=127')
    print(msg)
    outport.send(msg)

def request_preset_name(outport):
    msg=mido.Message('sysex', data= (65,16,0,0,0,0,11,17,16,0,0,0,0,0,0,16,96) )
    outport.send(msg)

def subscribe(outport):
    msg=mido.Message('sysex', data= (65,16,0,0,0,0,11,18,127,0,0,1,1,127) )
    outport.send(msg)

def get_current_pnum(outport):
    msg=mido.Message('sysex', data= (65,16,0,0,0,0,11,17,0,0,0,0,0,0,0,4,124) )
    outport.send(msg)

def parse_sysex(message):
    s=str(message)
    data=s.split('(')[1].split(')')[0].replace(' ','').split(',')
    header=data[:12]
    if header==  ['65','16','0','0','0','0','11','18','16','0','0','0']:
        mess=data[12:-1]
        return 'pname',''.join(chr(int(c)) for c in mess if c!='0')
    elif header==['65','16','0','0','0','0','11','18','0' ,'0','0','0']:
        mess=data[12:-1]
        # print(mess)
        return 'pnum',pmap2.get(tuple(mess))
    return None,None


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




    
    # U01-1 (0,0,0)
    # U01-2 (0,0,1)
    # U33-3 (0,6,2)

    # U34-1 (0,6,3)
    # U64-3 (0,11,15)
    # U65-1 (0,12,0)
    # U65-2 (0,12,1)
    # U65-3 (0,12,2)
    # U66-1 (0,12,3)
    # U66-2 (0,12,4)
    # U66-3 (0,12,5)

    # P01-1 (0,12,8)
    # P07-1 (0,13,10)
    # P13-2 (0,14,13)
    # P17-1 (0,15,8)
    # P33-2 (1,2,9)
    # P33-3 (1,2,10)

    print(pmap2[('0','0','0','0')])
    print(pmap2[('0','0','12','5')])
    print(pmap2[('0','1','2','10')])

    
    

    exit()


    def sp(bank,program,delta):
        new=shift_pos(bank,program,delta)
        print(bank,program,delta,new)
        
    sp(2,0,1)
    sp(2,0,-1)
    print()


    m1="sysex data=(65,16,0,0,0,0,11,18,16,0,0,0, 84,83,82,32,76,69,69,32,77,69,84,65,76,32,32,32,2,3,1,1,1,1,0,0,0,0,0,0,8,0,0,12,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,1,0,11,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,5,5,0,0,0,0,1,0,0,0,0,0,0,0,0,0,2,11,5,0,0,0, 64) time=0"
    m2="sysex data=(65,16,0,0,0,0,11,18,16,0,0,0, 50,84,83,82,32,76,69,69,32,77,69,84,65,76,32,32,2,3,1,1,1,1,0,0,0,0,0,0,8,0,0,12,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,1,0,11,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,5,5,0,0,0,0,1,0,0,0,0,0,0,0,0,0,2,11,5,0,0,0, 46) time=0"
    m3="sysex data=(65,16,0,0,0,0,11,18, 0,0,0,0, 0,0,12,3, 113) time=0"
    m4="sysex data=(65,16,0,0,0,0,11,18, 0,0,0,0, 0,0,12,4, 112) time=0"

    print(parse_sysex(m1))
    print("=========")
    print(parse_sysex(m2))
    print("=========")
    print(parse_sysex(m3))
    print("=========")
    print(parse_sysex(m4))
    print("=========")





    print(get_device_names())

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
