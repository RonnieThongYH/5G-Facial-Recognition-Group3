#!/bin/bash

raspivid -o - -t 0 -w 640 -h 480 -fps 90 -n | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8080/}' :demux=h264