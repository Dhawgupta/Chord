import socket
import threading

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

    # implementaion according to the old paper
    def request_find_successorOld(self,id):
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
    # new request_find_successor based on the new paper
    def request_find_successor(self,id):
        """

        :param id: int() The id for whcich to ind the successor
        :return: Key() return the Key type of successor
        """
        request = "find_successor," + str(id)
        print("Sendin request : {}".format(request))
        reply = self.send_request(request)
        if (reply == "HNE"):
            print("Host Not Exists")
            return None # return None
        self.log(reply)
        attrs = reply.split(',')
        retKey = Key(id = int(attrs[0]), ipaddress=attrs[1], port = int(attrs[2]))
        return retKey
    # returns the predecessor fo rid
    def request_find_predecessor(self,id):
        """

        :param id: int() The id for whcich to ind the predecessors
        :return: Key() return the Key type of predecessors
        """
        request = "find_predecessor," + str(id)
        print("Sendin request : {}".format(request))
        reply = self.send_request(request)
        if (reply == "HNE"):
            print("Host Not Exists")
            return None # return None
        self.log(reply)
        attrs = reply.split(',')
        retKey = Key(id = int(attrs[0]), ipaddress=attrs[1], port = int(attrs[2]))
        return retKey
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
    def request_successor(self):
        """
        this returns the existing successsor from the class
        :return:  return None if successor not exist else return the key class
        """
        request = "successor"
        reply = self.send_request(request)
        if (reply == 'HNE'):
            print("host not exists")
            return
        if reply == 'None':
            return None
        attrs = reply.split(',') # split the reply
        retKey = Key(id=int(attrs[0]), ipaddress=attrs[1], port=int(attrs[2]))
        return retKey  # returns the Key class object for the successor

    def request_closest_preceding_node(self,id):
        """

        :param id:  the id for whom to find the cloese nor
        :return: Key() return s the key object of node
        """
        request = "closest_preceding_node," + str(id)
        reply = self.send_request(request)
        if (reply == 'HNE'):
            print("host not exists")
            return
        if reply == 'None':
            return None
        attrs = reply.split(',')  # split the reply
        retKey = Key(id=int(attrs[0]), ipaddress=attrs[1], port=int(attrs[2]))
        return retKey  # returns the



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

    # Notify oworking
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
    # todo if required the update_table
    def request_update_finger_table(self,s,i):
        """
    #@1/3/18
        :param s: Key() is the possible node at the ith position of table
        :param i: integer ith entry of the finger tbale
        :return:
        """
        request = "update_finger_table," + str(s)  + ","  + str(i)
        print("Request Message : {}".format(request))
        reply = self.send_request(request)
        if (reply == 'HNE'):
            print("Host Not Exists")
            return
        print("Updation Done")


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

