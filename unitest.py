import unittest
from unittest.mock import patch
from client.client import send_file
from server.server import handle_client, receive_file as server_receive_file

class TestClientServer(unittest.TestCase):

#Unit tests for client.py functions
    
    #Test sending a file from client to server.
    @patch('client.client')
    def test_send_file(self, mock_client):
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'Test data')) as mock_file:
            send_file("test.txt")
            mock_client.sendall.assert_called()

 # Unit tests for server.py functions
    
    #Test handling a client connection on the server.
    @patch('server.server.accept')
    def test_handle_client(self, mock_accept):
        mock_conn = mock_accept.return_value[0]
        mock_addr = mock_accept.return_value[1]
        handle_client(mock_conn, mock_addr)
        mock_conn.recv.assert_called()
    
    #Test receiving a file from client to server.
    @patch('server.server')
    def test_server_receive_file(self, mock_server):
        
        mock_conn = mock_server.accept.return_value[0]
        server_receive_file(mock_conn)
        mock_conn.recv.assert_called()

if __name__ == '__main__':
    unittest.main()