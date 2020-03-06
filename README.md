# Networks and Systems: Compiler Design Summative

## Prerequisites
- Python 3
- Pyro4 Python Package

## How to run the system
1. Run the command `python -m Pyro4.naming`
2. Run the command `python back_server.py` as many times as you want. More instances mean more tolerance to faults if a server goes down.
3. Run the command `python front_server.py` to start the front end server.
4. Run the command `python client.py` as many times as you want to create client instances.

## How to disable a backend component for testing
The simplest solution would be to simply stop the server running by terminating the program. However you can also run the command `python server_status.py` and select a server from the menu to toggle the server status to 'down' (but will not actually terminate the program). Do the same again to toggle the status to 'up'
