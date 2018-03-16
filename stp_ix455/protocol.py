# Copyright (C) 2016, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import slave
import logging
import time
import e21_util

from slave.protocol import Protocol
from slave.transport import Timeout
from stp_ix455.message import Message, Frame, Payload


from e21_util.lock import InterProcessTransportLock
from e21_util.error import CommunicationError

class STPProtocol(Protocol):
    def __init__(self, logger=None):

        if logger is None:
            logger = logging.getLogger(__name__)
            logger.addHandler(logging.NullHandler())

        self.logger = logger

    def set_logger(self, logger):
        self.logger = logger

    def send_message(self, transport, message):        
        message.finish()
        
        frame_number = message.get_frame_length()
        
        if frame_number <= 0:
            self.logger.info("Nothing to send")
            return
        
        for frame_index in range(0, frame_number):
            current_frame = message.get_frame(frame_index)
            self.send_frame(transport, current_frame)
            
        
    def send_frame(self, transport, frame, retries=4):
        if retries < 0:
            raise CommunicationError("Could not send frame")
        
        raw_data = frame.get_raw()

        data = map(hex, map(ord, raw_data))
        
        self.logger.debug('Write ('+str(len(data))+' bytes): "%s"', " ".join(data))
        
        transport.write("".join(raw_data))
 
        time.sleep(1)
       
        try:
            response = ord(transport.read_bytes(1))
        except slave.transport.Timeout:
            self.send_frame(transport, frame, retries - 1)
        
        # retransmit the frame, if:
        #   1. we receive a NAK
        #   2. we receive nothing after 2 seconds

        if response == Message.CHAR_NAK:
            self.logger.warning("Received NAK(%s). Re-Transmitting message", hex(Message.CHAR_NAK))
            self.send_frame(transport, frame, retries - 1)

        if not response == Message.CHAR_ACK:
            self.logger.debug('Write not successful. Received response "%s". Retry...', hex(response))
            self.send_frame(transport, frame, retries-1)    
            
            
    def read_response_frame(self, transport, retries=4):
        if retries < 0:
            raise CommunicationError("Could not read response")
        
        response = []
        
        try:              
            first = ord(transport.read_bytes(1))
        except slave.transport.Timeout:
            first = None
                          
        if not first == Frame.CHAR_STX:
            transport.write(chr(Message.CHAR_NAK))
            return self.read_response_frame(transport, retries - 1)
        
        response.append(first)
        i=0
        while i < 255 + 5:
            try:
                byte = ord(transport.read_bytes(1))
            except slave.transport.Timeout:
                transport.write(chr(Message.CHAR_NAK))
                return self.read_response_frame(transport, retries - 1)
                          
            response.append(byte)
            
            if byte == Frame.CHAR_ETB or byte == Frame.CHAR_ETX:
                break

            i = i + 1
                
        try:
            last = ord(transport.read_bytes(1))
        except slave.transport.Timeout:
            transport.write(chr(Message.CHAR_NAK))
            return self.read_response_frame(transport, retries - 1)
                          
        response.append(last)
        
        self.logger.debug('Response (%s bytes): "%s"', str(len(response)), " ".join(map(hex, response)))
        
        return Frame(response)
    
    def read_response(self, transport, max_frames=2):
        message = Message()
        i = 0
        while i < max_frames:
            #transport.write(Message.CHAR_ACK)
            frame = self.read_response_frame(transport)
            
            if not frame.is_valid():
                self.logger.warning("Received an invalid frame.") 
                          
            message.add_frame(frame)
            
            if frame.is_terminating():
                break
            
            transport.write(chr(Message.CHAR_ACK))
                          
            i = i + 1
            
        return message
    
    def query(self, transport, abstract_msg):
        with InterProcessTransportLock(transport):
            msg = abstract_msg.get_message()

            if not isinstance(msg, Message):
                raise TypeError("message must be an instance of Message")

            self.logger.debug('Send message "%s": %s', msg, abstract_msg)

            self.send_message(transport, msg)
            time.sleep(1)
            response = self.read_response(transport)
            return response

    def clear(self, transport):
        with InterProcessTransportLock(transport):
            self.logger.debug("Clearing buffer...")
            try:
                while True:
                    transport.read_bytes(25)
            except:
                pass

    def write(self, transport, message):
        return self.query(transport, message)
