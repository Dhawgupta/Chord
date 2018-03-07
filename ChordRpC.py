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


"""
from __future__ import print_function
import numpy as np
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
        self.files = defaultdict(list)
        # TODO the finger table will be a dict of lists of id, ip , port
        self.finger_table = dict()
        self.finger_start = dict()
        self.next_node = next_node

        for i in range(self.m):
            self.finger_start[i] = (self.id + (2**i))%(2**self.m)

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

    def start_node(self):
        print("Starting Node ...")


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
        server = RPCThreading((self.ipaddress, self.port))
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


        server.serve_forever()


    def find_successor(self,id):
        """
        Returns the successor of the id by using its own finger
        :param id: int() whose finger table is to  be found
        :return: returns list
        """
        print("Finding Successor for {}".format(id))
        n_dash = self.find_predecessor(id) # ndash is the list

        # n_dash will be of type xmlrpccleint
        print("Exiting Successor for {}".format(id))
        return Node.list_to_rpc(n_dash).get_successor()
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
        print("Finding Predecessor for {}".format(id))
        n_dash = [self.id,self.ipaddress, self.port]
        while (not Node.inside(id, n_dash[0], Node.list_to_rpc(n_dash).get_successor()[0],False,True)):
            print("Next")
            n_dash = Node.list_to_rpc(n_dash).closest_preceding_finger(id)
        print("Exiting Predecessor for {}".format(id))
        return n_dash

    def closest_preceding_finger(self,id):
        """

        :param id: the id whose precerder has to be oud
        :return: list[id,ip,port]
        """
        print("Finding Closest Preceeding Node for {}".format(id))
        for i in range(self.m-1, -1,-1): #node.id
            if (Node.inside(self.finger_table[i][0],self.id,id )):
                    return self.finger_table[i]
        print("Exiting Closest Preceeding Node for {}".format(id))

        return [self.id, self.ipaddress, self.port]



    def join(self,n_dash = None):
        """
        n.join(n') request node n' to join
        if n_dash is None then init the Chord ring
        :param n_dash: n' to which we need to contact is list of [id, ip, port]
        :return: return nothing
        """
        print("Starting to join...")
        if n_dash is not None:
            print("Next Node is specified")
            self.init_finger_table(n_dash)
            print("Finge Table Initialized")
            #todo see toif using the update others
            self.update_others()
            print("Other nodes updated")

        else:
            print("Next Node not specified")
            # ndash is None init the ring
            for i in range(self.m):
                self.finger_table[i] = [self.id, self.ipaddress, self.port]
            self.predecessor = [self.id, self.ipaddress, self.port]
            self.successor = [self.id, self.ipaddress,self.port]
            print("Ring init finished")
        print("Quitting Join")
        # fix_finger_thread =\
        threading.Thread(target=self.fix_fingers).start()
        """
        self.thread = threading.Thread(target = self.rpc_server)
        print("Starting the XML-RPC Server \nIP address : {}\nPort : {}\nKey : {}".format('127.0.0.1',self.port, self.id))

        self.thread.start()
        """


    def init_finger_table(self, n_dash):
        """
        Initilaise the finger table using n_dash
        :param n_dash:
        :return:
        """
        print("Inside init table")
        print(n_dash)
        self.finger_table[0] = Node.list_to_rpc(n_dash).find_successor(self.finger_start[0])
        self.successor = [self.finger_table[0][0], self.finger_table[0][1], self.finger_table[0][2]]
        self.predecessor =  Node.list_to_rpc(self.successor).get_predecessor()

        print("Okay")
        Node.list_to_rpc(self.successor).set_predecessor([self.id, self.ipaddress, self.port])
        Node.list_to_rpc(self.predecessor).set_successor([self.id, self.ipaddress, self.port])
        print("Okay2")
        for i in range(self.m-1):
            # todo the if conditoin mentioned in paper
            self.finger_table[i+1] = Node.list_to_rpc(n_dash).find_successor(self.finger_start[i+1])
        print("Finger table initialized")


    def update_others(self):
        print("Updating Others")
        for i in range(self.m):
            p = self.find_predecessor(self.id - 2**(i))
            Node.list_to_rpc(p).update_finger_table([self.id,self.ipaddress, self.port], i)
        print("Finieshed Updating Others")


    def update_finger_table(self,n_list, i):
        """

        :param n_list: list of [id ip port] of the new node
        :param i: i th entry in finger table
        :return:
        """
        print("Updating Finger Table")
        if (Node.inside(n_list[0],self.id,self.finger_table[i][0], True, False)):
            self.finger_table[i] = n_list
            p = self.predecessor
            Node.list_to_rpc(p).update_finger_table(n_list , i)
        print("Updated Finger Table")


        # returning bogus just for compilation
        return n_list



    def stabilize(self):
        """
        to satbalise the finger tbale
        :return:
        """
        x = Node.list_to_rpc(self.successor).get_predecessor()
        if (Node.inside(x[0], self.id,  self.successor[0] , False, False)):
            self.successor = x
        Node.list_to_rpc(self.successor).notify([self.id, self.ipaddress, self.port])

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
            i = random.randint(1, self.m-1)
            self.finger_table[i] = self.find_successor(self.finger_start[i])
            time.sleep(1)




    @staticmethod
    def list_to_rpc(list = None):
        """
        list is None
        :param list: THe list of id, ip , port
        :return: xmlrpc client
        """

        client = xmlrpclib.ServerProxy(str("http://" + list[1] + ":" + str(list[2])+"/"))
        print("http://" + list[1] + ":" + str(list[2])+"/ - is the connecting node" )
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
    elif len(sys.argv) > 4:
        next_node = [int(sys.argv[1]), sys.argv[2], int(sys.argv[3])]
        a = Node(next_node=next_node,port = int(sys.argv[4]))
        a.start_server()
        a.join(next_node)
    else:
        a  = Node()
        a.start_server()
        a.join()
