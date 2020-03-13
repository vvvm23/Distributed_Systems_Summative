# Networks and Systems: Distributed Systems Summative

## Prerequisites
- Python 3 (A version that supports f-strings)
- Pyro4 Python Package

## How to run the system
1. Run the command `python -m Pyro4.naming`
2. Run the command `python back_server.py` as many times as you want. More instances mean more tolerance to faults if a server goes down.
3. Run the command `python front_server.py` to start the front end server.
4. Run the command `python client.py` as many times as you want to create client instances.

## How to disable a backend component for testing
The simplest solution would be to simply stop the server running by terminating the program. However you can also run the command `python server_status.py` and select a server from the menu to toggle the server status to 'down' (but will not actually terminate the program). Do the same again to toggle the status to 'up'

## Requirements
### System Design
Provided is a png showing the major operations among the various systems (the clients, front end server, back-end servers and web services)

### Back-end Server Implementation
I have implemented a back end server program. This can be run as many times as you wish to create more and more back-end servers (and so handle more faults). These servers process the user orders and can handle other servers going down.

### Front-end Server Implementation
I have implemented a front end server that forwards requests from the client to the primary server. It also selects the new primary server if the previous has gone down.

To test the capability of primary switching, I provided another program to allow the state of the back-end to be easily changed for testing.

### Client Implementation
I implemented a simple command line program to allow a user to make all requests supported by the servers and display responses from the server.

### Use of Web Services
The back-end server can connect to two external web services to validate and retrieve the longitude and latitude of the delivery post code. I use two external web services in case one is unavailable, giving some fault tolerance.
