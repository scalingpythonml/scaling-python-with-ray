#!/bin/bash
SRC_DIR=./proto
DST_DIR=messaging/proto/
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/MessageDataPB.proto
