import sha1
import socket


def getMbit(text,m=5):
    hsh = sha1.sha1(text)
    m_bit=int(hsh,16)%(2**m)
    return int(m_bit)



def DoesServiceExist(host, port):
    captive_dns_addr = ""
    host_addr = ""

    try:
        captive_dns_addr = socket.gethostbyname("BlahThisDomaynDontExist22.com")
    except:
        pass

    try:
        host_addr = socket.gethostbyname(host)

        if (captive_dns_addr == host_addr):
            return False

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
    except:
        return False

    return True


#class Peer
#key : filename
files = defaultdict(list) # contains the hash of files
interfaces = dict()

# finger_table => ith entry : Peer

successor = None
predeseccor = None

def getMbit(text,m=5):
    hsh = sha1.sha1(text)
    m_bit=int(hsh,16)%(2**m)
    return int(m_bit)






def handle_socket(sock,addr):
    """

    :param sock: socket of the incoming connection
    :param addr:  address of the incoming connection
    :return: nothing
    This will handle request like
    1. find_successor
    2. closest_preceding_node
    3. join
    4. notify
    5. successor
    6. predecessor
    7. notify
    8. create
    9. stabilize
    10. fix_fingers
    11. check_predecessor
    'format of message'
    function_name,argument1,argument2....

    This function will return the appropriate value back to the contacting server
    """
    message = sock.recv(4096)
    print(message) # now message is a RPC for this network
    rpc = message.split(',')
    # now run cases for rpc
    if (rpc[0] == 'find_successor'): #1
        print ("finding_successor")
        pass
    elif (rpc[0] == 'closest_preceding_node'): #2
        pass
    elif (rpc[0] == 'join'): #3
        pass
    elif (rpc[0] == 'stabilize'): #9
        pass
    elif (rpc[0] == 'notify'): #7
        pass
    elif (rpc[0] == 'fix_fingers'): #10
        pass
    elif (rpc[0] == 'check_predecessor'): #11
        pass
    elif (rpc[0] == 'predecessor'): #6
        pass
    elif (rpc[0] == 'successor'): #5
        pass
    elif (rpc[0] == 'live'): #  to check if node is live or not
        pass
    else:
        print("Wrong request from {}",addr)
    print("closing connection")




def socket_server(main_socket):
    main_socket.listen(5)
    print("Socket is listening ... ")
    while True:
        c,addr = main_socket.accept()
        print("Got request from {}",format(addr))
        t = threading.Thread(target=handle_socket, args=(c,addr))
        t.start()
        sleep(0.1)


if __name__ == "__main__":
    p1 = Peer()  # first peer
    # p1.create() # start the network

    p2 = Peer(p1.key)

    """
    # this is the main program
    print("Initiating Server .....")
    s = socket.socket()
    port = int(sys.argv[1])
    # port = random.randint(10000,20000)
    s.bind(('',port))
    # need to get a key of the peer
    # KeyPeer = ;

    for ifaceName in netifaces.interfaces():
        addresses = [i['addr'] for i in netifaces.ifaddresses(ifaceName).setdefault(netifaces.AF_INET, [{'addr': 'No IP addr'}])]
        interfaces[ifaceName] = addresses
    ipPort = interfaces['wlp3s0'][0] + ":" + str(port)
    macPort = str(get_mac()) +":" + str(port)
    ipKeyPeer = getMbit(ipPort)
    macKeyPeer = getMbit(macPort)

    print ("The IP is  {}  and corresponding key is {}".format(ipPort, ipKeyPeer))
    print("The MAC is  {}  and corresponding key is {}".format(macPort, macKeyPeer))

    print("Connected the socket with config {}".format(s.getsockname()))

    print("Enabling listening")
    t = threading.Thread(target = socket_server,args=(s,))
    t.start()


    if len(sys.argv) > 2:
        # this is not the first peer and contains the IP address of other peers
        pass
    else: # the first peer connected

        # first get all the files in system and create a hash of them
        for file in os.listdir("./Files"):
            if file.endswith(".txt"):
                # now file is the file number
                key = getMbit(file)
                files[key].append(file)

"""
