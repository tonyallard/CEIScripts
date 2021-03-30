#!/bin/bash

mkdir /mnt/ramdisk
chmod 777 /mnt/ramdisk
mount -t tmpfs -o size=64m,rw,relatime /mnt/ramdisk
