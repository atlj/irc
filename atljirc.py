# -*- coding: utf-8 -*-
import gi, time
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import socket
from threading import Thread
connected = False
channeled = False
#this var is for storing datas which re received froms erver
receivebuffer = ""

#TODO: add a paged view to message box(if yo join a room a page will open, ping pong etc., make sure that only nicks and messages re getting printed, add a logger feature and make sure it only logs the messages and the roomnames
#the s variable will be socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#this func contacts with the server
def connect(ip, port):
	notifyprint("connecting...")
	try:
		s.connect((ip, port))
		info_label.set_text(server +":"+str(port))
		notifyprint("connection is succesful")
		notifyprint("you can join to a room by clicking the key icon in top-left")
		return True
		
	except Exception as e:
		info_label.set_text(server +":"+str(port)+" (not connected)")
		notifyprint("connection has failed")
		#channel_window_show_button.set_visible(False)
		return False

#this func logins to server
def identify_to_server(username):
		receivethread.start()		
		s.send(bytes("USER "+username+" "+username+" "+username+" "+username+"\n\r", "UTF-8"))
		s.send(bytes("NICK "+username+"\n\r", "UTF-8"))

#this block is to keep the connection with server alive
def listener():
	while 1:
		global receivebuffer
		receivebuffer = s.recv(1024).decode("utf-8")
		index = text_buffer.get_end_iter()
		text_buffer.insert(index, receivebuffer)
		if not channeled:
			adj = scroll.get_vadjustment()
			adj.set_value(adj.get_upper())
			time.sleep(.1)
			adj.set_value(adj.get_upper())
		#print(s.recv(1024).decode("utf-8"))
		
def sender(message):
	if connected:
		if channeled:
			adj = scroll.get_vadjustment()
			basetext = "PRIVMSG {} : {}\r\n"
			s.send(bytes(basetext.format(channel, message), "UTF-8"))
			winprint(username +": "+message)
			adj.set_value(adj.get_upper()-adj.get_page_size())
			adj.set_value(adj.get_upper()-adj.get_page_size())
		else:
			notifyprint("you have not joined to a room yet")
	else:
		notifyprint("you are not connected to a server")

#this class is just for handling signals 
class Handler:
	#login button
	def login_click(self, button):
		
		#this block is for getting the values from entries
		global username, server, port, connected
		username = usernameentry.get_text()
		server = serverentry.get_text()
		port = int(portentry.get_text())
		if not username == "" and not " " in username:
				window.hide()
				mainwin.show_all()
				if connect(server, port):
					connected = True
					identify_to_server(username)
		#this statement is to control if the connection has established with server
		
	#clears the textbuffer1	
	def clear_button(self, button):
		start = text_buffer.get_start_iter()
		end = text_buffer.get_end_iter()
		text_buffer.delete(start, end)
		
	#this button shows the channel selector button
	
	def channel_button(self, button):	
		channel_window.show_all()
	
	def channel_abort_button(self, button):
		channel_window.hide()

		
	#this block is to autoscroll the notify window
	def notified(self, textbuffer):
		adj = notify_scroll.get_vadjustment()
		adj.set_value(adj.get_upper() - adj.get_page_size())
		adj.set_value(adj.get_upper() - adj.get_page_size())
	#the submit button in channel selector window
	def join_button(self, button):
		global channel, channeled
		channel = channel_entry.get_text()
		#we have to make sure that channel is entered properly
		if not channel == "" and not " " in channel:
			if not channel[0] == "#":
				channel = "#"+channel
			s.send(bytes("JOIN {}\r\n".format(channel), "UTF-8"))
			channeled = True	
			winprint("connecting to channel "+channel)
			channel_window.hide()
	
	#this func is to be sure only numbers entered to port entry
	def port_change(self, entry):
		try:
			#it tries to turn the value to integer, if it cant turn then it clears the input
			#TODO: if a char is insterted it deletes the whole input, make sure that it only clears the char
			int(portentry.get_text())
		except ValueError:
			portentry.set_text("")
		
	#send button in main window	
	def send_button(self, button):
		#TODO: you can send blank texts right now, this needs to be fixed asap
		sender(message_box.get_text())
		message_box.set_text("")

		
	#this function is for autoscroll the name comes from the signal which the text buffer gives when its value has changed	
	def text_add(self, textbuffer):
		#for horizontal adjustment we call this variable
		adj = scroll.get_vadjustment()
		#this line sets the value of scroll to the maximum value which is the bottom of page
		if channeled and adj.get_value() > adj.get_upper() - 700:
				adj.set_value(adj.get_upper()-adj.get_page_size())
				adj.set_value(adj.get_upper()-adj.get_page_size())

def winprint(text):
	index = text_buffer.get_end_iter()
	
	text_buffer.insert(index, text + "\n")
		
def notifyprint(text):
	notify_buffer.insert_at_cursor(text + "\n")
		
builder = Gtk.Builder()
builder.add_from_file("/root/atljirc.glade")
builder.connect_signals(Handler())

#this code block is for referencing widgets to use in handler
window = builder.get_object("login")
window.connect("delete_event", Gtk.main_quit)
window.show_all()
mainwin = builder.get_object("mainwin")
mainwin.connect("delete_event", Gtk.main_quit)
about_window = builder.get_object("about_window")
message_box = builder.get_object("message_box")
text_center = builder.get_object("text_center")
text_buffer = builder.get_object("textbuffer1")
scroll = builder.get_object("scroll")
notify_scroll = builder.get_object("notify_scroll")
notify_buffer = builder.get_object("notify_buffer")
channel_window = builder.get_object("channel_window")
info_label = builder.get_object("info_label")
channel_window_show_button = builder.get_object("channel_window_show_button")
channel_entry = builder.get_object("channel_entry")

#this code block is for naming inputs
usernameentry = builder.get_object("username_entry")
serverentry = builder.get_object("server_entry")
portentry = builder.get_object("port_entry")

receivethread = Thread(target=listener, args=())


Gtk.main()
