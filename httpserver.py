import socket
import time
import signal
import traceback
import os

def main():

    server = create_connection(port = 8080)

    while True:
        # 1. Wait for the browser to send a HTTP Request
        connection_to_browser = accept_browser_connection_to(server)

        # 2. Read the HTTP Request from the browser
        reader_from_browser = connection_to_browser.makefile(mode='rb')
        try:
            request_line = reader_from_browser.readline().decode("utf-8") # decode converts from bytes to text
            print()
            print('Request:')
            print(request_line)
            file_name = get_requested_filename(request_line)
            file_type = get_file_type(file_name)
        except Exception as e:
            print("Error while reading HTTP Request:", e)
            traceback.print_exc() # Print what line the server crashed on.
            shutdown_connection(connection_to_browser)
            continue

        # 3. Write the HTTP Response back to the browser
        writer_to_browser = connection_to_browser.makefile(mode='wb')
        try:
            # TODO: read "Hello, World!" from an HTML file instead of this encoded string.
            # response_body = "Hello, World! 12345".encode("utf-8")

            if(file_name == "./public/shutdown"):
                print("Server shutting down")
                shutdown_connection(connection_to_browser)
                exit()

            with open(file_name, "rb") as f:
                file_contents = f.read()

            response_body = file_contents
            
            content_type = get_content_type(file_type)

            response_headers = "\r\n".join([
                'HTTP/1.1 200 OK',
                f'Content-Type: {content_type}',
                f'Content-length: {len(response_body)}',
                'Connection: close',
                '\r\n'
            ]).encode("utf-8") # encode converts strings to raw bytes

            # These lines just PRINT the HTTP Response to your Terminal.
            print()
            print('Response headers:')
            print(response_headers)
            print()
            print('Response body:')
            print(response_body)
            print()

            # These lines do the real work; they WRITE the HTTP Response to the Browser.
            writer_to_browser.write(response_headers)
            writer_to_browser.write(response_body)
            writer_to_browser.flush()
        except Exception as e:
            print("Error while writing HTTP Response:", e)
            traceback.print_exc() # print what line the server crashed on
    
        shutdown_connection(connection_to_browser)

def get_requested_filename(request_line):
    fn = "./" + request_line.split(" ")[1]
    print(fn)
    return fn

def get_file_type(file_name):
    ft = file_name[file_name.rfind("."):]
    print(ft)
    return ft

def get_content_type(file_type):
    if(file_type == ".png"):
        return 'image/png'
    elif((file_type == ".jpeg")):
        return 'image/jpeg'
    elif(file_type == ".html"):
        return 'text/html; charset=utf-8'
    elif(file_type == ".ico"):
        return 'image/x-icon'
    elif(file_type == ".js"):
        return 'text/javascript; charset=utf-8'
    elif(file_type == ".css"):
        return 'text/css; charset=utf-8'
    return "ERROR: Wrong Content Type"

# Don't worry about the details of the rest of the code below.
# It is VERY low-level code for creating the underlying connection to the browser.

def create_connection(port):
    addr = ("", port)  # "" = all network adapters; usually what you want.
    server = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True) # prevent rare IPV6 softlock on localhost connections
    server.settimeout(2)
    print(f'Server started on port {port}. Try: http://localhost:{port}/index.html')
    return server

def accept_browser_connection_to(server):
    while True:
        try:
            (conn, address) = server.accept()
            conn.settimeout(2)
            return conn
        except socket.timeout:
            print(".", end="", flush=True)
        except KeyboardInterrupt:
            exit(0)

def shutdown_connection(connection_to_browser):
    connection_to_browser.shutdown(socket.SHUT_RDWR)
    connection_to_browser.close()


if __name__ == "__main__":
    print()
    main()

