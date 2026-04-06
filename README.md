# Topology Change Detector (SDN Project)

## Objective
This project detects dynamic topology changes in a network using Software Defined Networking (SDN) with Mininet and Ryu controller.

## Features
- Detect switch connection and disconnection
- Detect link up and down
- Display updated topology
- Log all network changes
- Monitor packet flow

## Tools Used
- Mininet (network emulator)
- Ryu Controller (SDN controller)
- OpenFlow protocol

## Setup Instructions

1. Install Mininet:
   sudo apt update
   sudo apt install mininet -y

2. Install Ryu:
   pip install ryu

3. Run controller:
   ryu-manager controller.py

4. Run topology:
   sudo mn --custom topo.py --topo mytopo --controller remote

## Testing

### Normal Case
- Run: pingall
- Expected: 0% packet loss

### Failure Case
- Run: link s1 s2 down
- Result: Link removed detected

### Recovery Case
- Run: link s1 s2 up
- Result: Link added detected

## Performance Testing
- Ping: h1 ping h2
- Throughput: iperf

## Output
- Controller logs topology changes
- Ping and iperf results

## Conclusion
This project demonstrates how SDN controllers dynamically monitor and react to topology changes in real-time.
