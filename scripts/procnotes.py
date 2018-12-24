#!/usr/bin/python3

import argparse
import os
import sys
import yaml
import maps
import hashlib 
import datetime
import isodate
import re 
import shutil
import dominate

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-p",help="parse it?",action="store_true") 
    parser.add_argument("-q",help="query out a tag")
    parser.add_argument("--config-file",help="what is config?",
        default="config.notes") 
    args = parser.parse_args()

    config = yaml.load(open(args.config_file,"r"))

    if not args.p and args.q == "":
        raise Exception("I need to know what to do, you've told me nothing to do")

    if args.p:

        these_entries = list(yaml.load_all(open(config["intake_file"],"r")))
    
        for this_entry in these_entries:
    
            if this_entry["d"] is None or this_entry["t"] is [] or this_entry["n"] is None:
                raise Exception("You need to have a date, tags, and notes!")
    
            try:
                this_entry["correction"]
            except:
                this_entry["correction"] = ""
    
            this_hash_hex = hashlib.sha1(
                    (   str(this_entry["d"]) + 
                        "".join(this_entry["t"]) +
                        "".join(this_entry["f"]) +
                        "".join(this_entry["n"]) +
                        str(this_entry["correction"])
                        ).encode("utf-8")
                    ).hexdigest()[:10]
    
            for i, afile in enumerate(this_entry["f"]):
                if not os.path.isfile(afile):
                    raise Exception("there ain't no file "+afile)
    
            this_entry["d"] = str(this_entry["d"])
            if not re.match("^20",this_entry["d"]):
                this_entry["d"] = "20"+this_entry["d"]
    
            this_entry["d"] = isodate.parse_date(this_entry["d"])
    
            entry_dir = config["notebook_directory"]+"/"+this_hash_hex
            print(entry_dir)
            os.makedirs(entry_dir,exist_ok=True)
    
            for i, afile in enumerate(this_entry["f"]):
                try:
                    shutil.copyfile(
                        this_entry["f"][i],
                        entry_dir+"/"+this_hash_hex+"_"+this_entry["f"][i])
                except:
                    raise Exception("copying "+afile+" failed!")
                this_entry["n"] = re.sub(afile,this_hash_hex+"_"+afile,this_entry["n"])
                this_entry["f"][i] = this_hash_hex+"_"+this_entry["f"][i]
    
            with open(entry_dir+"/"+this_hash_hex+"_notes.txt","w") as notefile:
                notefile.write(yaml.dump(this_entry))
                
    
        os.makedirs(config["trash"],exist_ok=True)
        for this_entry in these_entries:
            for i, afile in enumerate(this_entry["f"]):
                this_real_filename = re.sub(r"^[0-9a-z]{10}_","",this_entry["f"][i])
                try:
                    shutil.move(
                        this_real_filename,
                        config["trash"]+"/"+this_real_filename
                        )
                except:
                    pass
    
        shutil.move(
            config["intake_file"],
            config["trash"]+"/"+this_hash_hex+"_notes.txt"
            )
    
        shutil.copyfile(
            config["template_file"],
            config["intake_file"]
            )

    if args.q:

        query_result = list()

        for eachdir in os.listdir(config["notebook_directory"]):

            this_entry = yaml.load(open(config["notebook_directory"]+"/"+eachdir+"/"+eachdir+"_notes.txt","r"))

            if args.q in this_entry['t']:

                this_entry["path"] = config["notebook_directory"]+"/"+eachdir+"/"
                query_result.append(this_entry)

        query_result = sorted(query_result, key=lambda x: str(x["d"])+str(x["correction"]))

        with open("report_"+args.q+".html","w") as f:

            report = dominate.document(title="Report for query '"+args.q+
                "', "+str(datetime.datetime.now()))

            with report.head:
                dominate.tags.link(rel='stylesheet',href=config['css'])

            _entrylist = report.add(dominate.tags.ul())

            for i in query_result:

                if i["correction"] == "":

                    _anitem = _entrylist.add(dominate.tags.li())
                    _anitem += dominate.tags.h3(str(i["d"]))
                    _anitem += dominate.tags.h4(i["t"])
    
                    for j in i["f"]:
                        _anitem += dominate.tags.h4(dominate.tags.a(j,href=i["path"]+j))
    
                    _anitem += dominate.tags.p(i["n"])

                else:

                    _anitem += dominate.tags.h6("--- correction ---")

                    _anitem += dominate.tags.h4(i["t"])
    
                    for j in i["f"]:
                        _anitem += dominate.tags.h4(dominate.tags.a(j,href=i["path"]+j))
    
                    _anitem += dominate.tags.p(i["n"])

            f.write(report.render())

