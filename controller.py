"""
Topology Change Detector - POX Controller
Author: PANDU C V | Roll No: 21
"""

from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.discovery as discovery
import pox.openflow.spanning_tree as spanning_tree
from pox.lib.revent import *
import datetime

log = core.getLogger()

class TopologyDetector(EventMixin):

    def __init__(self):
        self.mac_to_port = {}
        self.switches = {}
        self.links = {}
        log.info("=== Topology Change Detector Started ===")

        core.openflow.addListeners(self)
        core.openflow_discovery.addListeners(self)

    def show_topology(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        log.info("─" * 50)
        log.info("[%s] Switches online : %s", now, list(self.switches.keys()))
        log.info("[%s] Links active    : %s", now, list(self.links.keys()))
        log.info("─" * 50)

    # Switch connected
    def _handle_ConnectionUp(self, event):
        dpid = dpidToStr(event.dpid)
        self.switches[dpid] = event.connection
        log.info(">>> SWITCH CONNECTED    | dpid=%s", dpid)
        self.show_topology()

        # Install table-miss: send all packets to controller
        from pox.lib.ofp import ofp_flow_mod
        msg = event.connection.msg_handlers
        from pox.openflow.libopenflow_01 import ofp_flow_mod, OFPP_CONTROLLER
        fm = ofp_flow_mod()
        fm.priority = 0
        fm.actions.append(
            __import__('pox.openflow.libopenflow_01',
                       fromlist=['ofp_action_output']).ofp_action_output(
                port=OFPP_CONTROLLER)
        )
        event.connection.send(fm)

    # Switch disconnected
    def _handle_ConnectionDown(self, event):
        dpid = dpidToStr(event.dpid)
        self.switches.pop(dpid, None)
        log.info(">>> SWITCH DISCONNECTED | dpid=%s", dpid)
        self.show_topology()

    # Link discovered
    def _handle_LinkEvent(self, event):
        link = event.link
        src = dpidToStr(link.dpid1)
        dst = dpidToStr(link.dpid2)
        key = (src, dst)

        if event.added:
            self.links[key] = (link.port1, link.port2)
            log.info(">>> LINK ADDED   | s%s:p%s --> s%s:p%s",
                    src, link.port1, dst, link.port2)
        elif event.removed:
            self.links.pop(key, None)
            log.info(">>> LINK REMOVED | s%s:p%s --> s%s:p%s",
                    src, link.port1, dst, link.port2)
        self.show_topology()

    # Packet in - L2 learning switch
    def _handle_PacketIn(self, event):
        from pox.lib.packet import ethernet
        packet = event.parsed
        if not packet.parsed:
            return

        dpid = event.dpid
        in_port = event.port

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][packet.src] = in_port

        if packet.dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][packet.dst]
        else:
            out_port = 65535  # OFPP_FLOOD

        from pox.openflow.libopenflow_01 import (
            ofp_packet_out, ofp_action_output,
            ofp_flow_mod, OFPP_FLOOD
        )

        if out_port != OFPP_FLOOD:
            fm = ofp_flow_mod()
            fm.match.dl_dst = packet.dst
            fm.match.in_port = in_port
            fm.priority = 1
            fm.idle_timeout = 30
            fm.hard_timeout = 60
            fm.actions.append(ofp_action_output(port=out_port))
            event.connection.send(fm)

        msg = ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(ofp_action_output(port=out_port))
        event.connection.send(msg)


def launch():
    core.registerNew(TopologyDetector)
