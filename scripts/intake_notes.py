#!/usr/bin/python3

import argparse
import os
import sys
import yaml
import maps
import hashlib 
#import isoties

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-p",help="parse it?",action="store_true") 
    parser.add_argument("--config-file",help="what is config?",
        default="config.notes") 
    args = parser.parse_args()

    config = yaml.load(open(args.config_file,"r"))

    if not args.p:
        sys.exit(0)

    these_entries = list(yaml.load_all(open(config["intake_file"],"r")))

    for this_entry in these_entries:

        this_hash_string = (
            str(this_entry["d"]) + 
            "".join(this_entry["t"]) +
            "".join(this_entry["f"]) +
            "".join(this_entry["n"])
            )

        this_hash_hex = hashlib.blake2b(this_hash_string.encode("utf-8")).hexdigest()
        print(this_hash_hex)

#    for i in this_file["f"]:
#        this_file["n"] = this_file["n"].sub(i,this_hash+i)
#
#    this_file["f"] = this_file["f"].concat hash in cool way
#
#    this_file["d"] = this_file["d"].parse right
#
#    with f as open(config["notebook_directory"]+"/"+this_hash)
#        print to f the entry again
#
#    os.copy(config["template_file"],config["intake_notes"])
