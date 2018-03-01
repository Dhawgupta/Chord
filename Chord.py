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
from Keys import Key

class Peer:
    def __init__(self,port=random.randint(10000,20000),next_node = None): # next node tells us the next node to communicate

        self.socket =None
        self.key =None
        self.ipaddress =None
        self.mac =None
        self.port =None
        self.successor =Key() # key is the node type Key() # simiular to finger_table[1]
        self.files =defaultdict(list)# dict
        self.finger_table=dict() # dict I - > Key() types
        self.finger_start = dict()

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
        # key is a interface between 2 nodes
        self.key = Key(self.macKeyPeer,self.ipaddress, self.port) # key to self node
        # key has been decided
        for i in range(self.m):
            self.finger_start[i] = (self.key.id + 2**(i))/(2**self.m)
        self.join(next_node)

        # if (next_node is None):
        #     self.create()
        # else:
        #     self.log("Requesting to join")
        #     self.request_join(next_node)

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
        elif (rpc[0] == 'find_predecessor'):  # 1 "one arg"
            print("finding_predecessor")
            arg = int(rpc[1])
            pred = self.find_predecessor(arg) # return s a key type
            # convert to string and transfer it back
            string = str(pred)
            sock.send(string.encode('ascii'))

        elif (rpc[0] == 'closest_preceding_node'):  # @1/3/18
            id = int(rpc[1])
            key = self.closest_preceding_node(id)
            string = str(key)
            sock.send(string.encode('ascii'))


        elif (rpc[0] == 'join'):  # 3
            pass
        elif (rpc[0] == 'stabilize'):  # 9
            pass
        elif (rpc[0] == 'notify'):  # 7
            key = Key(int(rpc[1]),rpc[2],int(rpc[3]))
            self.notify(key)
            sock.send("None".encode('ascii'))

        elif (rpc[0] == 'fix_fingers'):  # 10 # this will be automatic I suppose
            pass
        elif (rpc[0] == 'check_predecessor'):  # 11
            pass
        elif (rpc[0] == 'update_finger_table'):
            key = Key(int(rpc[1]), rpc[2], int(rpc[3]))
            id = int(rpc[4])
            # @1/3/18
            self.update_finger_table(key, id)
            sock.send("DOne".encode('ascii'))

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



    # @1/3/18 not using this join going to use request_join
    # probabily lefgacy replaced by request_join
    def joinOld(self,otherPeer): # assuming otherPeer is of Key type at the moment
        print("other Peer requesting to join id {}".format(otherPeer))
        self.predeseccor = None
        self.successor = otherPeer.request_find_successor(self.key.id)
        # self.successor = otherPeer.find_successor(self.key)
        if self.successor is not None:
            print ("Successfully joined ")
    def find_successorOld(self, id):
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

    # fixme check the correctness
    def find_successor(self,id):
        # id int() whose successor is to be found
        key = self.find_predecessor(id)
        succ = key.request_successor()
        return succ

        # fixme check the correctness of the function
    def find_predecessor(self, id):
            """
            :param id: THe id whose predecessor has to be found
            :return:  return the Key() of the predescoot
            """
            key = self.key
            while (not self.inside(id,key.id,key.request_successor().id, False, True)):
                key = key.request_closest_preceding_finger(id)
            return key

    def closest_preceding_node  (self, id):
        """
        :param id: the parameter id to find the closest preceding node to
        :return: return Key class type
        """
        for i in range(self.m-1,-1, -1) : #4,3,2,1,0
            # no need for i-1 as already i-1
            if self.inside(self.finger_table[i].id,self.key.id,id,False,False):
                return self.finger_table[i]
        return self.key



    def insideOld(self,x,a,b,include=True):
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

    def inside(self,x,a,b,includeLeft=True, includeRight = True):
        # earlier inclusedd the b term  we will include the a term
        if includeLeft and includeRight:
            if a<b:
                return (a <=x and x<=b)
            else:
                return (a<=x or x<=b)

        elif not includeLeft and includeRight:
            if a<b:
                return (a <x and x<=b)
            else:
                return (a<x or x<=b)

        elif includeLeft and not includeRight:
            if a<b:
                return (a <=x and x<b)
            else:
                return (a<=x or x<b)

        else:
            if a<b:
                return (a <x and x<b)
            else:
                return (a<x or x<b)




    def join(self,key):
        """
        This is a network function i.e. it recieved form the socket as string
        different from
        n'.join(n) where n' is the requesting node and n is the known node
        :param key:to be requested to join some network
        :return: assigns the predescessot and successor of the n' or id

        this function will send request to Key to join a network
        """
        if (key is not None):
            """
            Key is the n' node with the help of which we will communicate 
            """
            self.init_finger_table(key)
            # fixme update other and enable if requires
            # self.update_others()
            # TODO Move the keys in (predecessor ,n]

        else:
            """ init the network from start"""
            for i in range(self.m):
                self.finger_table[i] = self.key
            self.predecessor = self.key
            self.successor = self.finger_table[0]
    def joinSimple(self,key):
        """

        :param key: n' node
        :return:
        """
        self.predecessor = None
        self.successor = key.request_find_successor(self.key.id)

    #fixme check the implementation of update_tohers, update_finger_table and request_finger_table
    def update_others(self):
        for i in range(self.m):
            # find the last node p whose ith finger might be n
            p = Key()
            p = self.find_predecessor(self.key.id - 2**i)
            p.request_update_finger_table(self.key, i)

    #@1/3/18 Implementing the update_finger_table
    def update_finger_table(self,s,i):
        """

        :param s: Key() is hte possible node at ith position
        :param i: int() the position to check for
        :return: nothing
        """
        if self.inside(s.id, self.key.id, self.finger_table[i].id, True , False):
            self.finger_table[i] = s
            if i == 0:
                self.successor = s
            p  = self.predecessor
            p.request_update_finger_table(s,i)



    # fixme check the implemetation of this
    def init_finger_table(self,key):
        self.finger_table[0] = key.request_find_successor(self.finger_start[1])
        self.successor = self.finger_table[0] # todo rember to update successor every time finger_table[1] used
        self.predecessor = self.successor.request_predecessor()
        self.successor.request_notify()
        for i in range(0, self.m - 1):
            # Todo implment the if condition for now simple find_succers
            # if self.include(self.finger_start[i + 1],self.key.id, self.finger_table[i].id, True,False)
            #     self.finger_table[]
            self.finger_table[i+1] = key.request_find_successor(self.finger_start[i+1])



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

    # this will be done to stabilize the node after an internval
    # while True:
    #     peer.stabilize()
    #     print("Self : {}".format(peer.key))
    #     print("Successor is : {}".format(peer.successor))
    #     print("predecessor is : {}".format(peer.predecessor))
    #     sleep(5)
