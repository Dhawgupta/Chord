"""
This is the new implementation using RPC XML
Currently we will be implementing it on the ports only

import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8000/")
print "3 is even: %s" % str(proxy.is_even(3))
print "100 is even: %s" % str(proxy.is_even(100))

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

def is_even(n):
    return n % 2 == 0

server = SimpleXMLRPCServer(("localhost", 8000))
print "Listening on port 8000..."
server.register_function(is_even, "is_even")
server.serve_forever()


Usage
python Program next_node.id next_node.ipaddress next_node.port <current_node.port>
python Program <current_node.port>


"""
from __future__ import print_function
#import numpy as np
import socket
import threading
import os
import sys
import random
import sha1
import netifaces
from collections import defaultdict
from uuid import getnode as get_mac
import xmlrpclib
import SimpleXMLRPCServer
import SocketServer
import time
# implement the simple xml rpc server

# nodes being passdec
# n = dict()
# n['ip'] = '127.0.0.1'
# n['id'] = key
# n['port'] = 8000
# node = list() with -0 - id, 1 - as ip address 2 - port
class RPCThreading(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
    pass


class Node:
    def __init__(self, port = random.randint(10000,20000), next_node = None):
        """
        Initialise the node with port (random) and if join the network
        :param port: the port it will listen on
        :param next_node: None if the first node else the node to contact
        """
        self.port = port
        self.ipaddress = '127.0.0.1' # Todo make a way to get the correct IP of machien
        self.mac = get_mac() # ass+
        # igns the MAC address of the machine
        self.mac_port = str(self.mac) + ":" + str(self.port) # we make the key using the combination of mac and port
        self.id = Node.get_mbit(string = self.mac_port)
        self.m = 5
        # TODO Predecessor and Successor are both of type list objects

        self.predecessor = None # lets keep them of type dict
        self.successor = None # todo keep them of type dict()
        # TODO select the type of list for finger table
        # the dictionary is of a lists for the files
        self.files = defaultdict(list)
        # TODO the finger table will be a dict of lists of id, ip , port
        self.finger_table = dict()
        self.finger_start = dict()
        self.next_node = next_node
        self.second_successor = None
        self.lock_files = threading.Lock()
        for i in range(self.m):
            self.finger_start[i] = (self.id + (2**i))%(2**self.m)


        #fixme check wether that try expcet for leaving nodes

    def create_file(self):
        """
        THis function will be called by the first nodes to preapre the hash for 100 files and stores in self.filse
        :return:
        """
        for file in os.listdir("./Files"):
            if file.endswith(".txt"):
                key = Node.get_mbit(file)
                self.lock_files.acquire()
                self.files[key].append(file)
                self.lock_files.release()
        print("Files initiated")
    @staticmethod
    def get_mbit(string,m=5):
        """
        Get the key of mbit using SHA1
        :param mac_port: the mac + port combination
        :param m: the value of m defualt to 5
        :return: returns the value from 0 to 2**m -1
        """
        hsh = sha1.sha1(string)
        m_bit = int(hsh,16)%(2**m)
        return int(m_bit)

    def connected(self):
        """
        RPC to check if the node is connected or not
        :return:
        """
        return True
    def start_node(self):
        print("Starting Node ...")

    def menu_to_print(self):
        print("Select from Following:\n1. Print IP address and ID\n2.IP Address of Successor and Predecessor\n"
              "3. The file key is contains\n4.Finger Table : ")
        choice = raw_input()

        try:
            choice = int(choice)
        except:
            choice = 5
        # print(choice)
        if choice == 1:
            # print Ip address and ID
            print("IP Address : {}\nPort : {}\nKey : {}\n".format(self.ipaddress, self.port, self.id))
        elif choice == 2:
            # print add of succ and pred
            print("Successor: Key : {}\nIPaddress : {}\nPort : {}\nPredecessor: Key : {}\nIPaddress : {}\nPort : {}\n".format(self.successor[0],self.successor[1],self.successor[2],
                                                                                                                              self.predecessor[0], self.predecessor[1], self.predecessor[2]))
        elif choice == 3:
            # print key of file it contains
            for key in self.files:
                print ("Key: {}, Files : {}".format(key, self.files[key]))
        elif choice == 4:
            # print finger_table
            for i in range(self.m):
                print("ID : {}, Key : {}".format(self.finger_start[i], self.finger_table[i][0]))
        else:
            print("Wrong Choice")

    def start_server(self):
        """
        Implement a multithreaded xmlRPC server
        :return:
        """
        self.thread = threading.Thread(target = self.rpc_server)
        print("Starting the XML-RPC Server \nIP address : {}\nPort : {}\nKey : {}".format('127.0.0.1',self.port, self.id))

        self.thread.start()

    def rpc_server(self):
        """
        THis will run the RPC Server
        """
        # server = SimpleXMLRPCServer.SimpleXMLRPCServer((self.ipaddress,self.port))
        server = RPCThreading((self.ipaddress, self.port), logRequests=False)
        # TODO register all the appropraite functions
        server.register_function(self.find_successor)
        server.register_function(self.get_successor)
        server.register_function(self.get_predecessor)
        server.register_function(self.find_predecessor)
        server.register_function(self.set_predecessor)
        server.register_function(self.closest_preceding_finger)
        server.register_function(self.join)
        server.register_function(self.update_others)
        server.register_function(self.update_finger_table)
        server.register_function(self.set_successor)
        server.register_function(self.notify)
        server.register_function(self.connected)
        server.register_function(self.give_files)


        server.serve_forever()


    def find_successor(self,id):
        """
        Returns the successor of the id by using its own finger
        :param id: int() whose finger table is to  be found
        :return: returns list
        """
        # print("Finding Successor for {}".format(id))
        n_dash = self.find_predecessor(id) # ndash is the list

        # n_dash will be of type xmlrpccleint
        # print("Exiting Successor for {}".format(id))
        try:
            return Node.list_to_rpc(n_dash).get_successor()
        except:
            raise ValueError("Node not present")
    def get_successor(self):
        """
        Get the successor of the node
        :return: list of id, ip , port
        """
        return self.successor
    def get_predecessor(self):
        return self.predecessor

    def set_predecessor(self,list):
        """
        Set the predecessor
        :param list:
        :return:
        """
        self.predecessor = list
        return list

    def set_successor(self,list):
        """
        Set the successor
        :param list:
        :return:
        """
        self.successor = list
        self.finger_table[0] = list
        return list
    def find_predecessor(self,id):
        """
        Return the predecessor for id
        :param id: int() type
        :return: list of id, ip , port
        """
        # n_dash = self
        # print("Finding Predecessor for {}".format(id))
        n_dash = [self.id,self.ipaddress, self.port]
        try:
            while (not Node.inside(id, n_dash[0], Node.list_to_rpc(n_dash).get_successor()[0],False,True)):
                # print("Next")
                n_dash = Node.list_to_rpc(n_dash).closest_preceding_finger(id)
            #   print("Exiting Predecessor for {}".format(id))
        except:
            raise ValueError('find_predecessor Node not present')
        return n_dash

    def closest_preceding_finger(self,id):
        """

        :param id: the id whose precerder has to be oud
        :return: list[id,ip,port]
        """
        # print("Finding Closest Preceeding Node for {}".format(id))
        for i in range(self.m-1, -1,-1): #node.id
            if (Node.inside(self.finger_table[i][0],self.id,id )):
                    return self.finger_table[i]
        # print("Exiting Closest Preceeding Node for {}".format(id))

        return [self.id, self.ipaddress, self.port]


    def give_files(self,id):
        """
        This function will give the files for node with id "id"
        ie. all files in (predecessor, id]
        :param id:
        :return: returns the dictionary of keys and files
        """

        # dictionary of files
        files_to_give = list()
        files_data = list()

        # iterate over dictionayr keys
        tempDict = self.files.copy()
        for key in tempDict:
            if (Node.inside(key, self.predecessor[0], id, False, True)):
                for file in tempDict[key]:
                    string =''
                    files_to_give.append(file)
                    with open('./Files/'+ file ,'r') as f:
                        a = f.read()
                        while a:
                            string = str(a) + string

                    files_data.append(string)
                # files_to_give[key] = list(tempDict[key])
                self.lock_files.acquire()
                del self.files[key]
                self.lock_files.release()

        files_and_data = [files_to_give, files_data]
        return list(files_and_data)

    def join(self,n_dash = None):
        """
        n.join(n') request node n' to join
        if n_dash is None then init the Chord ring
        :param n_dash: n' to which we need to contact is list of [id, ip, port]
        :return: return nothing
        """
        # print("Starting to join...")
        if n_dash is not None:
            # print("Next Node is specified")
            self.init_finger_table(n_dash,True)
            # print("Finge Table Initialized")
            #todo see toif using the update others
            self.update_others()
            # print("Other nodes updated")

        else:
            # print("Next Node not specified")
            # ndash is None init the ring
            for i in range(self.m):
                self.finger_table[i] = [self.id, self.ipaddress, self.port]
            self.predecessor = [self.id, self.ipaddress, self.port]
            self.successor = [self.id, self.ipaddress,self.port]
            # print("Ring init finished")
        # print("Quitting Join")
        # fix_finger_thread =\
        threading.Thread(target=self.fix_fingers).start()
        """
        self.thread = threading.Thread(target = self.rpc_server)
        print("Starting the XML-RPC Server \nIP address : {}\nPort : {}\nKey : {}".format('127.0.0.1',self.port, self.id))

        self.thread.start()
        """


    def init_finger_table(self, n_dash,first = False):
        """
        Initilaise the finger table using n_dash
        :param n_dash:
        :param first: distinguish between call from join and stablilize
        :return:
        """
        # print("Inside init table")
        # print(n_dash)
        try:
            self.finger_table[0] = Node.list_to_rpc(n_dash).find_successor(self.finger_start[0])
        except:
            raise ValueError('init_finger_table Node not exists')
        self.successor =self.finger_table[0]
        try:
            self.predecessor =  Node.list_to_rpc(self.successor).get_predecessor()
        except:
            raise ValueError('init_finger_table Node not exists')
        # fixme getting the dictionary of files from successsor
        # if first:
        #     try:
        #         pass
        #     except:
        #         raise ValueError("Successor Absent")
        if first:
            files_and_data = []
            files_and_data = Node.list_to_rpc(self.successor).give_files(self.id)
            print(files_and_data)
            files = files_and_data[0]
            data = files_and_data[1]

            # convert the file array to the dictionary
        # for file in os.listdir("./Files"):
        #     if file.endswith(".txt"):
        #         key = Node.get_mbit(file)
        #         self.lock_files.acquire()
        #         self.files[key].append(file)
        #         self.lock_files.release()
        # print("Files initiated")

            for i,file in enumerate(files):
                if file.endswith('.txt'):
                    key = Node.get_mbit(file)
                    self.lock_files.acquire()
                    self.files[key].append(file)
                    self.lock_files.release()

                    # add the file to the system
                    if not os.path.exists("./Files/" + file):
                        # the file does not exist
                        print('Creating Files {}'.format(file))
                        with open('./Files/' + file ,'wb') as f:
                            f.write(data[i])
                        # data written to the file

            print("Files added to the system: ")

            # TODO createa directory to add the files in the directory
            # we have the file
            # self.lock_files.acquire()
            # self.files = Node.list_to_rpc(self.successor).give_files(self.id)
            # self.lock_files.release()
        # print("Okay")
        try:
            Node.list_to_rpc(self.successor).set_predecessor([self.id, self.ipaddress, self.port])
            Node.list_to_rpc(self.predecessor).set_successor([self.id, self.ipaddress, self.port])
        except:
            raise ValueError('init finger table Not found')
        # print("Okay2")
        for i in range(self.m-1):
            # todo the if conditoin mentioned in paper
            try:
                self.finger_table[i+1] = Node.list_to_rpc(n_dash).find_successor(self.finger_start[i+1])
            except:
                raise ValueError('init_finger_table Node not exists')
        # print("Finger table initialized")


    def update_others(self):
        # print("Updating Others")
        for i in range(self.m):
            p = self.find_predecessor(self.id - 2**(i))
            try:
                Node.list_to_rpc(p).update_finger_table([self.id,self.ipaddress, self.port], i)
            except:
                raise ValueError('update others : Node not found')
        # print("Finieshed Updating Others")


    def update_finger_table(self,n_list, i):
        """

        :param n_list: list of [id ip port] of the new node
        :param i: i th entry in finger table
        :return:
        """
        # print("Updating Finger Table")
        if (Node.inside(n_list[0],self.id,self.finger_table[i][0], True, False)):
            self.finger_table[i] = n_list
            p = self.predecessor
            try:
                Node.list_to_rpc(p).update_finger_table(n_list , i)
            except:
                raise ValueError('update finger table Node not found')
        # print("Updated Finger Table")


        # returning bogus just for compilation
        return n_list



    def stabilize(self):
        """
        to satbalise the finger tbale
        :return:
        """
        try:
            x = Node.list_to_rpc(self.successor).get_predecessor()
            if (Node.inside(x[0], self.id,  self.successor[0] , False, False)):
                self.successor = x
            Node.list_to_rpc(self.successor).notify([self.id, self.ipaddress, self.port])
        except:
            raise ValueError("Stabilize Node not exists")
    def notify(self, list):
        """
        n.notify(n')
        :param list: contains the n'node
        :return: Should return None but return a bogus list for checking purposes
        """
        if (self.predecessor is None or Node.inside(list[0], self.predecessor[0], self.id)):
            self.predecessor = list

        return list

    def fix_fingers(self):
        while True:
            connected = False
            try:
                # to check if the successor is connected or not

                connected = Node.list_to_rpc(self.successor).connected()
            except:
                connected = False
            if connected:
                self.second_successor = Node.list_to_rpc(self.successor).get_successor()
            else:
                self.successor = self.second_successor
                self.finger_table[0] = self.successor
                try:
                    self.init_finger_table(self.successor)
                except:
                    pass
                # the successor has left
            try:
                self.stabilize()
                i = random.randint(1, self.m-1)
                self.finger_table[i] = self.find_successor(self.finger_start[i])
                if i == 0:
                    self.successor = self.finger_table[0]
            except:
                continue
            time.sleep(0.5)




    @staticmethod
    def list_to_rpc(list = None):
        """
        list is None
        :param list: THe list of id, ip , port
        :return: xmlrpc client
        """
        if list is None:
            raise ValueError('Node not Found')
        client = xmlrpclib.ServerProxy(str("http://" + list[1] + ":" + str(list[2])+"/"))
        # print("http://" + list[1] + ":" + str(list[2])+"/ - is the connecting node" )
        return client
    @staticmethod
    def inside(x,a,b,includeLeft = False, includeRight = False):
        """

        :param x: one that lies
        :param a: left limit
        :param b: right limit
        :param includeLeft: include the left limit
        :param includeRight: include the right limit

        :return: Return true if lies in the interval or false if does not
        """
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




if __name__ == '__main__':
    if len(sys.argv) > 3:
        next_node = [int(sys.argv[1]),sys.argv[2], int(sys.argv[3])]
        a = Node(next_node= next_node)
        a.start_server()
        a.join(next_node)
        a.start_node()
    elif len(sys.argv) > 4:
        next_node = [int(sys.argv[1]), sys.argv[2], int(sys.argv[3])]
        a = Node(next_node=next_node,port = int(sys.argv[4]))
        a.start_server()
        a.join(next_node)
        a.start_node()

    else:
        if len(sys.argv) == 2:
            port = int(sys.argv[1])
            a  = Node(port = port)
        else:
            a = Node()

        a.start_server()
        a.join()
        # initialise the files
        a.create_file()
        a.start_node()

    while True:
        a.menu_to_print()

