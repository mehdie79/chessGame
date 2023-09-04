import socket
import threading
import queue
# import time

class Server():
    threads = []
    def __init__(self, p, clock):
        self.HEADER = 2048
        self.PORT = 5555  # port number

        # host_name = socket.gethostname()
        # SERVER = socket.gethostbyname(host_name) # get local host IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.SERVER = s.getsockname()[0]  # get local host IP
        s.close()

        ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.server_already_running = False

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP connection
        try:
            self.server.bind(ADDR)  # Binds server to port
        except OSError as e:
            if e.errno == 10048:  # Address already in use
                self.server_already_running = True

        
        self.number_connections = 0
        self.waiting_clients_list = []
        self.player_number = 0
        # global ready_client
        # ready_client = 0

        self.p = p
        self.clock = clock
        self.game_finished = False
        # Create a Lock (mutex) instance
        self.mutex_client_connections = threading.Lock()

    

    
    
    def wait_clients_finish(self):
        for index in range(len(self.threads)):
            self.threads[index].join()

    

    def listen_to_client(self, player_id, your_player_one, connections):
        connected = True
        send_start = False
        quit_game = False
        player_one_turn = True
        print("HERE IN THE LISTEN CLIENT")
        while connected:
            if not send_start:
                send_start = True
                message = "start"
                connections[player_id].sendall(message.encode(self.FORMAT))

            if player_one_turn and your_player_one :
                    message = 'your_turn w'
                    connections[player_id].sendall(message.encode(self.FORMAT))
            elif not player_one_turn and not your_player_one:
                    message = 'your_turn b'
                    connections[player_id].sendall(message.encode(self.FORMAT))

            
            data = connections[player_id].recv(self.HEADER)
            data = data.decode(self.FORMAT)
            if data == "your_turn":
                if your_player_one:
                    player_one_turn = True
                else:
                    player_one_turn = False
            if data == "quit":
                connected = False
                quit_game = True
                message = 'quit'
                connections[player_id].sendall(message.encode(self.FORMAT))

            elif data == "restart":
                connected = False
            else:
                if (data and your_player_one and player_one_turn) or (not your_player_one and not player_one_turn):
                    msg = data.split(" ")
                    if msg[0] == "mouse_button_down":
                        
                        player_one_turn = False if player_one_turn else True
                        message = 'other_player_moved' + " " + msg[1] + " " + msg[2] + " " + msg[3] + " " + msg[4]
                        if player_one_turn:
                            connections[player_id-1].sendall(message.encode(self.FORMAT))
                        else:
                            connections[player_id+1].sendall(message.encode(self.FORMAT))
                        

                    elif msg[0] == "check_mate":
                        self.game_finished = True
                        message = 'check_mate' + " " + msg[1]
                        # self.connected = False
                        if player_one_turn: 
                            connections[player_id-1].sendall(message.encode(self.FORMAT))
                        else:
                            connections[player_id+1].sendall(message.encode(self.FORMAT))

                    elif msg[0] == "stale_mate":
                        self.game_finished = True
                        message = 'stale_mate'
                        # self.connected = False
                        if player_one_turn:
                            connections[player_id-1].sendall(message.encode(self.FORMAT))
                        else:
                            connections[player_id+1].sendall(message.encode(self.FORMAT))

        if quit_game:
            return False
        else:
            return True



        
    def initiate_client_workers(self, connections):
        player_id = 2
        result_queue = queue.Queue()
        #self.initiate_client_thread = threading.Thread(target=self.listen_to_client , args=(player_id,))
        initiate_client_thread = threading.Thread(target=lambda pid, ypn, conn: result_queue.put(self.listen_to_client(pid,ypn, conn)), args=(player_id-2,True, connections))
        initiate_client_thread.start()
        initiate_client_thread_2 = threading.Thread(target=lambda pid, ypn, conn: result_queue.put(self.listen_to_client(pid,ypn, conn)), args=(player_id-1,False, connections))
        initiate_client_thread_2.start()
        initiate_client_thread.join()
        initiate_client_thread_2.join()
        return result_queue


            

    def process_client(self, connections):
        player_id = 2

        
        result_queue = self.initiate_client_workers(connections)
        
        player_one = result_queue.get()
        player_two = result_queue.get()
        connected = True
        while connected:
            if not player_one:
                connections[player_id-2].close()
                

            if not player_two:
                connections[player_id-1].close()
                
            if not player_one and not player_two: 
                break

            if player_one and player_two:
                result_queue = self.initiate_client_workers(connections)
                player_one = result_queue.get()
                
                player_two = result_queue.get()
                continue
            else:
                if player_one:
                    self.mutex_client_connections.acquire()
                    self.number_connections += 1
                    self.waiting_clients_list.append(connections[player_id-2])   
                    self.mutex_client_connections.release()
                    connected = False

                elif player_two:
                    self.mutex_client_connections.acquire()
                    self.number_connections += 1
                    self.waiting_clients_list.append(connections[player_id-1])   
                    self.mutex_client_connections.release()
                    connected = False
        
        

    def add_connections(self, conn):
        self.waiting_clients_list.append(conn) 

    def start_server(self): 
        self.server_thread = threading.Thread(target=self.runServer)
        self.server_thread.start()
        

    def populate_connections_list(self):
        connections = []
        connections.append(self.waiting_clients_list[0])
        connections.append(self.waiting_clients_list[1])
        
        self.waiting_clients_list.pop(0)
        self.waiting_clients_list.pop(0)
        self.number_connections -= 2
        

        return connections

    def runServer(self):
       
        
        run = True
        max_connections = 2
        self.server.listen()
        # start_time = 0
        # end_time = 0
        print(f"[LISTENING] Server is listing on {self.SERVER} and port {self.PORT}")
        while run:
            conn, addr = self.server.accept()
            # the maximum player
            
            self.mutex_client_connections.acquire()
            if len(self.waiting_clients_list) > max_connections:
                self.mutex_client_connections.release()
                self.wait_clients_finish()
                run = False
            self.mutex_client_connections.release()

            self.mutex_client_connections.acquire()
            self.add_connections(conn)
            self.number_connections += 1
            self.player_number += 1
            # Threaded function
            connections = []
            if self.number_connections > 0 and self.number_connections % 2 == 0:
                connections = self.populate_connections_list()
                thread = threading.Thread(
                    target=self.process_client, args=(connections,))
                thread.start()
                self.threads.append(thread)
            
            print(f"[ACTIVE CONNECTION] {self.number_connections}")
            if len(self.waiting_clients_list) == max_connections:
                self.mutex_client_connections.release()
                self.wait_clients_finish()
                run = False
                break
            self.mutex_client_connections.release()


        


        
