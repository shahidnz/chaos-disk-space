#!/usr/bin/env python

import subprocess
import time
import argparse

LOADFILE=1000000

class DiskManager(object):
    def __init__(self,
                 partition,
                 percent=0):
        self.percent=int(percent) #target percent value
        self.actualPercent=0
        self.partition=partition.rstrip("/")

    def cleanup(self):
        assert self.partition, "Cleanup - Correct Partition Value required"
        cmd="/bin/rm {0}/junk.file.*".format(self.partition)
        return self.run(cmd)

    def putLoad(self,
                size=LOADFILE):
        assert size >0,"Expected data size > 0"
        assert self.partition, "Correct Partition Value required"
        print("Consuming 10MB")
        cmd="/usr/bin/yes this is test file | head -c " +\
            "{0} > {1}/junk.file.{2}".format(size, self.partition, int(time.time()*1000.0))
        return self.run(cmd)


    def chaos(self):
        print("Evaluate Load")
        current=self.currentState()

        while(current < self.percent):
            print ("Loop")
            self.putLoad()
            current = self.currentState()
        print ("Target achieved: Current Disk Usage {}".format(current))

    def currentState(self):
        cmd="/bin/df -kh {0}".format(self.partition)
        s,o,e=self.run(cmd)
        data=o.decode("utf-8").split("%")[1].split(" ")[-1]
        data=int(data)
        assert int(data) >=0,"Ensuring the correct field parsed"
        self.actualPercent=data
        print ("Current Consumed :{}".format(data))
        return data

    def run(self,
            cmd):
        cmd=cmd.strip()
        print("Executing Command: {}".format(cmd))
        status=-1
        out=None
        err=None

        try:
            response=subprocess.Popen(cmd,shell=True,
                                universal_newlines=False,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out,err=response.communicate()
            status=response.returncode
        except Exception as exp:
            print(repr(exp))
        finally:
            print ("Result:{}|{}|{}".format(status, out, err))
            return status, out, err

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Partition related command options')

    #Read System status
    read_parser = subparsers.add_parser("read", help="read partition")
    read_parser.add_argument("partition", action="store",
                             help="read the partition for available space")
    read_parser.add_argument("--action", "-a", default="read", action="store_false", help="size of data")

    #Clean system state
    clean_parser = subparsers.add_parser("clean",help="clean the partition")
    clean_parser.add_argument("partition", action="store", help="clean the partition")
    clean_parser.add_argument("--action", "-a", default="clean", action="store_false", help="size of data")

    #populate
    load_parser = subparsers.add_parser("load", help="load the partition")

    load_parser.add_argument("partition", action="store", help="load the partition with some data")
    load_parser.add_argument("size", action="store", help="size of data")
    load_parser.add_argument("--action", "-a",default="load", action="store_false", help="size of data")

    args = parser.parse_args()

    assert args.partition, "Valid Partition/disk location is required"

    if (args.action == "read"):
        dm = DiskManager(args.partition)
        dm.currentState()
    elif (args.action == "clean"):
        dm = DiskManager(args.partition)
        dm.cleanup()
    elif (args.action == "load"):
        dm = DiskManager(args.partition, percent=args.size)
        dm.chaos()




