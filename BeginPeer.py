"""Questions:
1. When is statabalized called in the peer class
2. When is the fixed finger clled in the peer cass1

"""

from __future__ import print_function
import threading
import socket
import os
import sys
import random
import sha1
from collections import defaultdict
import netifaces
from uuid import getnode as get_mac
from time import sleep

class Peer:
    def __init__(self,port=random.randint(10000,20000),next_node = None): # next node tells us the next node to communicate

        self.socket =None
        self.key =None
        self.ipaddress =None
        self.mac =None
        self.port =None
        self.successor =None# key
        self.predecessor =None# key
        self.files =defaultdict(list)# dict
        self.finger_table=dict() # dict
        # self.files =None# dict
        self.m = 5
        self.next = 0
        self.socket = socket.socket()
        # port = int(sys.argv[1])
        self.port = port
        # port = random.randint(10000,20000)
        self.socket.bind(('', port))
        # need to get a key of the peer
        # KeyPeer = ;
        self.interfaces = dict()
        for ifaceName in netifaces.interfaces():
            addresses = [i['addr'] for i in
                         netifaces.ifaddresses(ifaceName).setdefault(netifaces.AF_INET, [{'addr': 'No IP addr'}])]
            self.interfaces[ifaceName] = addresses
        # self.ipaddress = self.interfaces['l0'][0]
        self.ipaddress = "127.0.0.1" # set to the local IP # this needs to be fixed # error
        self.mac = get_mac()
        self.ipPort = self.ipaddress + ":" + str(self.port)
        self.macPort = str(get_mac()) + ":" + str(self.port)
        self.ipKeyPeer = self.getMbit(self.ipPort)
        self.macKeyPeer = self.getMbit(self.macPort)
        self.key = Key(self.macKeyPeer,self.ipaddress, self.port)
        if (next_node is None):
            self.create()
        else:
            self.log("Requesting to join")
            self.request_join(next_node)

    def start_server(self):
        self.t = threading.Thread(target=self.socket_server, args=(self.socket,))
        print("Enabling Listening ....")
        self.t.start()

    def log(self, string):
        print("[PEER] "+ str(string))
    def socket_server(self,main_socket):
        main_socket.listen(5)
        print("Socket is listening ... ")
        while True:
            c, addr = main_socket.accept()
            print("Got request from {}".format(addr))
            t = threading.Thread(target=self.handle_socket, args=(c, addr))
            t.start()
            sleep(0.1)

    def handle_socket(self,sock, addr):
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

        Thhis function will call the approprate function from the class recienve the data as
        key and cnvert that key to string and
        transmit it back

        """
        message = sock.recv(4096)
        print(message)  # now message is a RPC for this network
        rpc = message.split(',')
        # now run cases for rpc
        if (rpc[0] == 'find_successor'):  # 1 "one arg"
            print("finding_successor")
            arg = int(rpc[1])
            succ = self.find_successor(arg) # return s a key type
            # convert to string and transfer it back
            string = str(succ)
            sock.send(string.encode('ascii'))

        elif (rpc[0] == 'closest_preceding_node'):  # 2 # dont think required
            pass
        elif (rpc[0] == 'join'):  # 3
            pass
        elif (rpc[0] == 'stabilize'):  # 9
            pass
        elif (rpc[0] == 'notify'):  # 7
            key = Key(int(rpc[1]),rpc[2],int(rpc[3]))
            self.notify(key)
            sock.send("None".encode('ascii'))
            pass
        elif (rpc[0] == 'fix_fingers'):  # 10 # this will be automatic I suppose
            pass
        elif (rpc[0] == 'check_predecessor'):  # 11
            pass
        elif (rpc[0] == 'predecessor'):  # 6
            if self.predecessor is None:
                sock.send('None'.encode('ascii'))
            else:
                string = str(self.predecessor)
                sock.send(string.encode('ascii'))


        elif (rpc[0] == 'successor'):  # 5
            if self.successor is None:
                sock.send('None'.encode('ascii'))
            else:
                string = str(self.successor)
                sock.send(string.encode('ascii'))

        elif (rpc[0] == 'live'):  # to check if node is live or not
            pass
        elif( rpc[0] == 'send_files'):
            pass
        else:
            print("Wrong request from {}", addr)
            sock.send("None".encode("ascii"))
        print("closing connection")
        sock.close()


    # probabily lefgacy replaced by request_join
    def join(self,otherPeer): # assuming otherPeer is of Key type at the moment
        print("other Peer requesting to join id {}".format(otherPeer))
        self.predeseccor = None
        self.successor = otherPeer.request_find_successor(self.key.id)
        # self.successor = otherPeer.find_successor(self.key)
        if self.successor is not None:
            print ("Successfully joined ")
    def find_successor(self, id):
        """

        :param id:  id of the node whom we have to find successor to
        :return: returns a Key value type with id , ip, port
        """
        if self.inside(id,self.key.id, self.successor.id):
            return self.successor # returns the whole key
        else:
            node = self.closest_preceding_node(id) # confusing between this and implemetaion should it be self.key.id or just id
            # node is Key type
            return node.request_find_successor(id) # this function will first connect to node and then call find successor form there

    def inside(self,x,a,b,include=True):
        if include:
            if a<b:
                return (a <x and x<=b)
            else:
                return (a<x or x<=b)

        else:
            if a<b:
                return (a <x and x<b)
            else:
                return (a<x or x<b)

    def closest_preceding_node  (self, id):
        """
        :param id: the parameter id to find the closest preceding node to
        :return: return Key class type
        """
        for i in range(self.m-1,-1, -1) : #4,3,2,1,0
            # no need for i-1 as already i-1
            if self.inside(self.finger_table[i].id,self.key.id,id,False):
                return self.finger_table[i]
        return self.key

    def request_join(self,key):
        """
        This is a network function i.e. it recieved form the socket as string
        different from
        n'.join(n) where n' is the requesting node and n is the known node
        :param key:to be requested to join some network
        :return: assigns the predescessot and successor of the n' or id

        this function will send request to Key to join a network
        """
        self.predecessor = None
        self.successor = key.request_find_successor(self.key.id)

    def getMbit(self,text, m=5):
        hsh = sha1.sha1(text)
        m_bit = int(hsh, 16) % (2 ** m)
        return int(m_bit)

    def create(self):
        """
        Instattiares a chord network i.e. start hashing the files etc
        :return:
        """
        self.predecessor = None
        self.successor = self.key
        # create the initila hash for the files

        for file in os.listdir("./Files"):
            if file.endswith(".txt"):
                # now file is the file number
                key = self.getMbit(file)
                self.files[key].append(file)
        print("Chord Network Initiated")
    # creates the initail hash
    def request_create(self):
        self.predecessor = None
        self.successor = self.key

    def stabilize(self):
        """
        x is supposed to be the key type
        :return:
        """
        self.log(self.successor)
        x = self.successor.request_predecessor() # returns the key type
        # either x is just id or it is the whole key type
        if x is not None and self.inside(x.id,self.key.id, self.successor.id,False) :
            successor = x # x has to be a key type
        self.successor.request_notify(self.key)

    def notify(self,key):
        """

        :param key: n' thinks that it is our predecessor this is the whole key
        :return: The return doenst matter here
        """
        if self.predecessor is None or self.inside(key.id,self.predecessor.id, self.key.id):
            self.predecessor = key
        return None

    def check_predecessor(self):
        """
        Ping the predecessor and check if the node exists if not set as None
        :return:
        """
        if not self.predecessor.check_node():
            self.predecessor = None




    def fix_fingers(self):
        """
        Called periodically fixes the finger table
        :return: None
        """
        self.next += 1
        if (self.next > self.m-1):
            self.next = 0
        self.finger_table[self.next] = self.find_successor(self.key.id + 2**self.next)

    def fix_all_fingers(self):
        """
        Fixes all the fingers
        :return: None
        """
        for next in range(self.m):
            self.finger_table[next] = self.find_successor(self.key.id + 2**self.next)


#either we can make a key or a hash map for the id
class Key:
    """
    This class will be gateway to send commands and request to different nodes
    We will send request and rpc to the associated keys and their ip address
    """
    def __init__(self,id = -1,ipaddress = '0.0.0.0',port = 12345):
        self.id = id
        self.ipaddress = ipaddress # string
        self.port = port # integer
        # this will contains all the request commands

    def request_find_successor(self,id):
        """
        :param id: request for succcer of this id from the current ndoe
        :return: return the Key class to find_successor
        """
        request = "find_successor," + str(id)
        print("Sending the request : {}".format(request))
        reply = self.send_request(request)
        if (reply == 'HNE'):
            print("host not exists")
            return Key(id =-1, ipaddress = '0.0.0.0', port = 12345)
        # the reply will be of the format
        self.log(reply)
        if isinstance(reply, Key):
            return reply
        attrs = reply.split(',') # split the reply with ,
        retKey = Key(id = int(attrs[0]),ipaddress=attrs[1], port = int(attrs[2]) )
        return retKey # returns the Key class object for the successor

    def request_predecessor(self):
        """
        this returns the existing predescessor from the class
        :return:  return None if predesceet not exist else return the key class
        """
        request = "predecessor"
        reply = self.send_request(request)
        if (reply == 'HNE'):
            print("host not exists")
            return
        if reply == 'None':
            return None
        attrs = reply.split(',') # split the reply
        retKey = Key(id=int(attrs[0]), ipaddress=attrs[1], port=int(attrs[2]))
        return retKey  # returns the Key class object for the successor


    # currently I dont think it is required
    def request_join(self,key):
        """
        Curerntly I dont hthink it ise required
        Sends the join request to the intended client
        :return:
        """
        self.log('inside request join')
        # now we have to communicate to peer
        request = 'request_join,'  + str(object=key)
        self.log(request)
        reply = self.send_request(request)

    def log(self,string):
        print('[KEY] ' + string)

    def request_notify(self,key):
        """
`       Request the current Key that 'key' can be a predesccor to taht node
        :param key:request to notify the key attribute
        :return:
        Need to send the whole key
        """
        request = "notify," + str(key)
        print("Request message : {}".format(request))
        reply = self.send_request(request) # the reply will be irrelevant
        if(reply=='HNE'):
            print("host not exists")
            return
        print("Notified")


    def check_node(self):
        """
        To check if this node is live or not
        :return: True if node responds False if node doesnt responds
        """
        exists = self.DoesServiceExist(self.ipaddress,self.port)
        return exists # return true if host exists else glse

    def send_request(self,string):
        exists = self.DoesServiceExist(self.ipaddress, self.port)
        if not exists:
            return "HNE" # Host not exists
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ipaddress,self.port))
            print("Connected to the Host Key {}".format(self.id))
            s.send(string.encode('ascii')) # send the requested string
            reply = s.recv(4096) # recieve the reply
            print("Reply recieved from the server")
            s.close()
            return reply
    def DoesServiceExist(self,host, port):
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
    def request_file_transfer_from_successor(self,key):
        """
        :param key: is the key of the requesting node i.e. syntax will be succ.request_file_transfer_succ(self.key))

        :return:
        """
        request = "send_files," + str(key)


    def __repr__(self):
        return str(self.id) + "," + self.ipaddress + "," + str(self.port)



def run_peer(connection_peer):
    """

    :param connection_peer: Connection peer is the peer node connects to if entering a network
    :return:
    """
    if connection_peer == None:
        peer = Peer(next_node= None)
        print("Starting Server ....")
        peer.start_server()

        print("First Node established with :\nIP: {}\nPort: {}\nKey: {}\nFiles : {}".format(peer.ipaddress,peer.port,peer.key.id,peer.files.items()))
    else: # other node given
        peer = Peer(next_node = connection_peer)
        print("The Peer to connect is {}".format(connection_peer))
        print("Node established with :\nIP: {}\nPort: {}\nKey: {}\nFiles : {}".format(peer.ipaddress,peer.port,peer.key.id,peer.files.items()))
        peer.start_server()

    return peer


if __name__ == "__main__":
    if len(sys.argv) > 1:
        string = sys.argv[1]
        attr  = string.split(',')
        k = Key(id = int(attr[0]), ipaddress = attr[1], port = int(attr[2]))
        peer = run_peer(k)
        print("Successor is : {}".format(peer.successor))
    else:
        peer = run_peer(None)
    while True:
        peer.stabilize()
        print("Self : {}".format(peer.key))
        print("Successor is : {}".format(peer.successor))
        print("predecessor is : {}".format(peer.predecessor))
        sleep(5)
