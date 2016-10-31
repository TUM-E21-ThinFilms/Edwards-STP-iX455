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

def as_string_list(array):
    ls = []
        
    for el in array:
        if isinstance(el, (int, long)):
            ls.append(chr(el))
	elif isinstance(el, basestring) and len(el) > 1:
	    ls = ls + as_string_list(el)		
	elif isinstance(el, list):
	    ls = ls + as_string_list(el)
        else:
            ls.append(el)
     
    return ls

def as_integer_list(array):
    ls = []
        
    for el in array:
	if isinstance(el, basestring) and len(el) > 1:
	    ls = ls + as_integer_list(el)
	    continue

        if not isinstance(el, (int, long)):    
            ls.append(ord(el))
        else:
            ls.append(el)
     
    return ls

class Message(object):
   
    CHAR_ACK = 0x06
    CHAR_NAK = 0x15
       
    PAYLOAD_FRAME_MAX_LEN = 255
    
    def __init__(self):
        self.frame = []
        
    def get_frame_length(self):
        return len(self.frame)
        
    def get_frame(self, index):
        if index >= len(self.frame):
            raise ValueError("index out of range")
            
        return self.frame[index]
        
    def add_frame(self, frame):
        if not isinstance(frame, Frame):
            raise TypeError()
        
        self.frame.append(frame)
        frame.set_block_number(len(self.frame))
        frame.set_terminating(True)

	if len(self.frame) > 1:
	    self.frame[-1].set_terminating(False)

    def finish(self):        
        for frame in self.frame:
            frame.set_checksum(frame.compute_checksum())
            
    def __str__(self):
        return "Message<"+str(len(self.frame))+" frames>"

class Payload(object):
    
    CHAR_BSP = 0x20
    CHAR_QUERY = 0x3f    
    CHAR_NAK = 0x21
    CHAR_ACK = 0x23

    PAYLOAD_MAX_LEN = 255
    PAYLOAD_MIN_LEN = 2
    
    TYPE_CONTROL = 1
    TYPE_QUERY = 2
    TYPE_NONE = 4
    TYPE_ACK = 8
    TYPE_NAK = 16
    
    def __init__(self, raw_payload, is_first=True):
        self.is_first = is_first
        
        if raw_payload is None or not isinstance(raw_payload, list):
            self.payload = [0, 0]
        else:
            self.payload = raw_payload
        
    def is_valid(self):
        if not isinstance(self.payload, list):
            return False
        
        if len(self.payload) < self.PAYLOAD_MIN_LEN or len(self.payload) > self.PAYLOAD_MAX_LEN:
            return False
    
        return True
    
    def set_control(self):
        if self.is_first:
            self.payload[0] = self.CHAR_BSP
        else:
            raise RuntimeError("Cannot set control if this payload is not the first one")
        
    def set_query(self):
        if self.is_first:
            self.payload[0] = self.CHAR_QUERY
        else:
            raise RuntimeError("Cannot set query if this payload is not the first one")
        
    def get_type(self):
        if self.is_first:
            return self.TYPE_NONE

        if self.payload[0] == self.CHAR_BSP:
            return self.TYPE_CONTROL
        elif self.payload[0] == self.CHAR_QUERY:
            return self.TYPE_QUERY
        elif self.payload[0] == self.CHAR_NAK:
	    return self.TYPE_NAK
	else:
	    return self.TYPE_ACK
        
    def set_command(self, cmd):
        if self.is_first:
            self.payload[1] = cmd
        else:
            raise RuntimeError("Cannot set command if this payload is not the first one")
        
    def get_command(self):
        return self.frame[1]
    
    def set_parameter(self, index, value):
        if isinstance(value, list):
            length = len(value)
        else:            
            value = [value]
            length = 1
            
        if self.is_first:
            required_length = 2 + index + length
            offset_index = 2 + index
        else:
            required_length = index + length
            offset_index = index
        
        if required_length > self.PAYLOAD_MAX_LEN or index < 0:
            raise ValueError("index out of range")
        
        if len(self.payload) < required_length:
            self.payload = self.payload + (required_length - len(self.payload)) * [0]
            
        for i in range(0, length):
            self.payload[offset_index + i] = value[i]
    
    def get_parameter(self, index, length):
        if self.is_first:
            required_len = 2 + index + length
            offset_index = 2 + index
        else:
            required_len = index + length
            offset_index = index
        
        if index < 0 or length < 0 or required_len > self.PAYLOAD_MAX_LEN:
            raise ValueError("index or length out of range")
            
        array = length * [0]
            
        for i in range(0, length):
            array[i] = self.payload[offset_index + i]
            
        return array
    
    def get_raw(self):
        return as_string_list(self.payload)
    
class Frame(object):
      
    CHAR_STX = 0x02
    CHAR_ETX = 0x03
    CHAR_ETB = 0x17
    
    def __init__(self, raw_frame=None, is_first=True):
        
        self.is_first = is_first
	self.frame = 4*[0]
	self.frame[0] = self.CHAR_STX
	self.terminator = self.CHAR_ETX
        
        if isinstance(raw_frame, Payload):
            self.payload = raw_frame
            self.chksum = 0xFF
            self.set_terminating(True)
        elif raw_frame is None or not isinstance(raw_frame, list) or len(raw_frame) < 6:
            self.payload = Payload(None, self.is_first)
            self.set_terminating(True)
            self.chksum = 0xFF
        else:
            self.frame[1:4] = raw_frame[1:4]
            self.terminator = raw_frame[-2]
            
            if not (self.terminator == self.CHAR_ETB or self.terminator == self.CHAR_ETX):
                self.set_terminating(True)
            
            self.payload = Payload(raw_frame[4:-2], self.is_first)
            self.chksum = raw_frame[-1]

    def is_valid(self):        
        if not self.frame[0] == self.CHAR_STX:
            return False
        
        block_number = self.get_block_number()
        
        if block_number < 0 or block_number > 999:
            return False
        
        if not self.payload.is_valid():
            return False
               
        if not self.get_checksum() == self.compute_checksum():
            return False
        
        return True
        
    def compute_checksum(self):
        
        array = as_integer_list(self.frame + self.payload.get_raw() + [self.terminator, 0xFF])
        
        chksum = 0x00
        
        for el in array:
            chksum = chksum ^ el
            
        return chksum
    
    def get_checksum(self):
        return self.chksum
    
    def set_checksum(self, checksum):
        self.chksum = checksum
        
    def set_block_number(self, number):
        if number < 0 or number >= 1000:
            raise ValueError("block number must be positive and <= 1000")
        
        string = str(number).zfill(3)
        array = []

        for char in string:
            array.append(char)
        
        self.frame[1] = ord(array[0])
        self.frame[2] = ord(array[1])
        self.frame[3] = ord(array[2])
        
    def get_block_number(self):
        number = map(chr, self.frame[1:4])
        return int("".join(number))
        
    def set_payload(self, payload):
        if not isinstance(payload, Payload):
            raise TypeError()
        
        self.payload = payload
        
    def get_payload(self):
        return self.payload
        
    def set_terminating(self, is_terminating):
        if is_terminating:
            self.terminator = self.CHAR_ETX
        else:
            self.terminator = self.CHAR_ETB
        
    def is_terminating(self):
        return (self.terminator == self.CHAR_ETX)
    
    def get_raw(self):
        return as_string_list(self.frame + self.payload.get_raw() + [self.terminator, self.chksum])
    
    
class AbstractResponse(object):
    def __init__(self, message):
	self.msg = None

        if isinstance(message, Message):
            self.msg = message
        
    def get_response(self):
        return self.msg
    
    def is_valid(self):
        return self.msg.is_valid() and self._is_valid()
        
    def _is_valid(self):
        return True
    
    def _raw_to_integer(self, data):
        str = as_string_list(data)
        return int("".join(str), 16)
        
    def _integer_to_raw(self, integer):
        hexa = hex(integer)[2:]
        return [hexa[i:i+2] for i in range(0, len(hexa), 2)]

    def is_successful(self):
	return self.msg.get_frame(0).get_payload().get_type() == Payload.TYPE_ACK
