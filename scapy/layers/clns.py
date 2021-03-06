"""
    CLNS Extension
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 BENOCS GmbH, Berlin (Germany)
    :author:    Marcel Patzlaff, mpatzlaff@benocs.com
    :license:   GPLv2

        This module is free software; you can redistribute it and/or
        modify it under the terms of the GNU General Public License
        as published by the Free Software Foundation; either version 2
        of the License, or (at your option) any later version.

        This module is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

    :description:

        This module provides a layer and registration function for
        OSI Connectionless-mode Network Services (such as IS-IS).
                
    :TODO:

        - rework this if a better way is found/implemented to bind
          protocols such as IS-IS (or if IS-IS remains the sole CLN
          protocol)

"""
import struct

from scapy.config import conf
from scapy.fields import ByteEnumField, PacketField
from scapy.layers.l2 import LLC
from scapy.packet import Packet, bind_layers


network_layer_protocol_ids= {
    0x00 : "Null",
    0x08 : "Q.933",
    0x80 : "IEEE SNAP",
    0x81 : "ISO 8438 CLNP",
    0x82 : "ISO 9542 ES-IS",
    0x83 : "ISO 10589 IS-IS",
    0x8E : "IPv6",
    0xB0 : "FRF.9",
    0xB1 : "FRF.12",
    0xC0 : "TRILL",
    0xC1 : "IEEE 802.aq",
    0xCC : "IPv4",
    0xCF : "PPP"
}


_cln_protocols= {}

class _GenericClnsPdu(Packet):
    name= "Generic CLNS PDU"
    fields_desc= [
        ByteEnumField("nlpid", 0x00, network_layer_protocol_ids),
        PacketField("rawdata", None, conf.raw_layer)
    ]
    

class ConnectionlessNetworkService(Packet):
    name= "Connectionless-mode Network Service"
    
    def guess_payload_class(self, p):
        cls= conf.raw_layer
         
        if len(p) >= 1:
            nlpid = struct.unpack("!B", p[0])[0]
            cls= _cln_protocols.get(nlpid, _GenericClnsPdu)
             
        return cls

@conf.commands.register
def register_cln_protocol(nlpid, cln_protocol_class):
    if nlpid is None or cln_protocol_class is None:
        return
    
    _cln_protocols[nlpid]= cln_protocol_class


bind_layers(LLC, ConnectionlessNetworkService, dsap=0xfe, ssap=0xfe, ctrl=3)