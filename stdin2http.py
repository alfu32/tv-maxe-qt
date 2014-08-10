# -*- coding: utf-8 -*-
import os, sys, subprocess, threading, time, random
import socketserver, http.server
from queue import Queue, Empty

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        q = Queue()
        t = threading.Thread(target=self.enqueue, args=(q, ))
        t.start()

        while not self.server.stop:
            try:
                byte = q.get(True, None)
            except:
                continue
            try:
                self.wfile.write(byte)
            except:
                print("Sorry, the HTTP server stopped unexpectedly.")
                self.server.stop = True
                self.server.ffmpeg.kill()
                self.server.shutdown()
                return

    def enqueue(self, q):
        while not self.server.stop:
            byte = self.server.ffmpeg.stdout.read(512)
            q.put(byte)

class Server:
    def __init__(self, port, exec_line):
        self.port = port
        self.exec_line = exec_line
        self.httpd = None

    def start(self):
        self.httpd = socketserver.ThreadingTCPServer(('', self.port), Proxy)
        self.httpd.stop = False
        self.httpd.ffmpeg = subprocess.Popen(
            self.exec_line,
            stdout=subprocess.PIPE)
        threading.Thread(target=self.httpd.serve_forever).start()
        print("HTTP server started at port {0}".format(self.port))

    def stop(self):
        if self.httpd:
            self.httpd.stop = True
            self.httpd.shutdown()
            print("HTTP server stopped")

if __name__ == '__main__':
    s = Server(8090, ['ffmpeg', '-y', '-i', 'http://1tv.ambra.ro', '-acodec', 'copy', '-vcodec', 'copy', '-f', 'avi', '-'])
    s.start()

