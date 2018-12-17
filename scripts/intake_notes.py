
#import yaml
import argparse
import os
#import hash
#import isoties

if main

    args.argparsenew
    args.adda command ("-p","parse it",default=False) 
    args.adda command ("config_file","config file",default="config.notes") 
    argparse it

    config = []
    with c as open(args.config_file,"r"):
        config = yamlread c
    
    if not args.p:
        return 0

    with f as open(config["intake_notes"],"r"):

        this_file = yamlread f

        this_hash = hash(this_file)

        for i in this_file["f"]:
            this_file["n"] = this_file["n"].sub(i,this_hash+i)

        this_file["f"] = this_file["f"].concat hash in cool way

        this_file["d"] = this_file["d"].parse right

        with f as open(config["notebook_directory"]+"/"+this_hash)
            print to f the entry again

    os.copy(config["template_file"],config["intake_notes"])
