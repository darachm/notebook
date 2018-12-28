#!/usr/bin/python3

import argparse
import os
import sys
import yaml
import hashlib 
import datetime
import isodate
import re 
import shutil
import dominate
import dominate.util

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-p",help="parse it?",action="store_true") 
    parser.add_argument("-q",help="query out a tag")
    parser.add_argument("-c",help="copy over template file",action="store_true")
    parser.add_argument("-t",help="test formatting",action="store_true")
    parser.add_argument("--config-file",help="what is config?",
        default=".notebook_config") 
    args = parser.parse_args()

    try:
        config = yaml.load(open(args.config_file,"r"))
    except:
        raise Exception("\n"+""" 
There's no config file! Please make one. Here's an example:

template_file: ".notes.yaml"
intake_file: "notes.yaml"
notebook_directory: "book"
raw_notebook: "raw_notebook.yaml"
trash: "trash"
css: .style.css
""")

    if not args.p and args.q == "":
        raise Exception("I need to know what to do, you've told me nothing to do")

    try:
        raw_notebook = list(yaml.load_all(open(config["notebook_directory"]+"/"+config["raw_notebook"],"r")))
    except:
        os.makedirs(config["notebook_directory"],exist_ok=True)
        with open(config["notebook_directory"]+"/"+config["raw_notebook"],"w") as f:
            f.write("")
        raise Exception("\n"+"""
I couldn't find a raw notebook file, at all. You are probably just starting up.
So I made an empty file, which should work. Re-run it!
""")
    if len(raw_notebook) == 0:
        raw_notebook = {}
    else:
        raw_notebook = raw_notebook[0]

    if args.p:

        try:
            these_entries = list(yaml.load_all(open(config["intake_file"],"r")))
        except:
            shutil.copyfile(
                config["template_file"],
                config["intake_file"]
                )
            raise Exception("\n"+"""
I couldn't find an intake file, at all. You are probably just starting up.
So I copied over the template to `notes.yaml` and you should be able to edit
that and then retry parsing the intake file (`notes.yaml`)
""")

        procd_entries = list()

        for this_entry in these_entries:
    
            if this_entry["d"] is None or this_entry["t"] is [] or this_entry["n"] is None:
                raise Exception("\n"+"""
For a note to be parsed and recorded, you need to have a date, tags, and notes!
This corresponds to the `d:`, `t:`, and `n:` fields respectively.
""")
    
            try:
                this_entry["correction"]
            except:
                this_entry["correction"] = ""
    
            this_hash_hex = hashlib.sha1(
                    (   str(this_entry["d"]) + 
                        #"".join(this_entry["t"]) +
                        #"".join(this_entry["f"]) +
                        "".join(this_entry["n"]) +
                        str(this_entry["correction"]) +
                        str(datetime.datetime.now())
                        ).encode("utf-8")
                    ).hexdigest()[:10]
    
            for i, afile in enumerate(this_entry["f"]):
                if not os.path.isfile(afile):
                    raise Exception("there ain't no file "+afile)
    
            this_entry["d"] = str(this_entry["d"])
            if not re.match("^20",this_entry["d"]):
                this_entry["d"] = "20"+this_entry["d"]
    
            this_entry["d"] = isodate.parse_date(this_entry["d"])
            this_entry["hash"] = this_hash_hex

            procd_entries.append(this_entry)

        if not args.t:

            for this_entry in procd_entries:

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
                      raw_notebook[this_entry["hash"]] = this_entry
      
                  os.makedirs(config["trash"],exist_ok=True)
                  for this_entry in these_entries:
                      for i, afile in enumerate(this_entry["f"]):
                          this_real_filename = re.sub(r"^[0-9a-z]{10}_","",this_entry["f"][i])
                          try:
                              pass
                              shutil.move(
                                  this_real_filename,
                                  config["trash"]+"/"+this_real_filename
                                  )
                          except:
                              pass
              
                  shutil.move(
                      config["intake_file"],
                      config["trash"]+"/"+this_hash_hex+"_"+str(datetime.datetime.now())+"_notes.txt"
                      )
              
        elif args.t:

            with open("test_report.html","w") as test_report:

                report = dominate.document(title="Test report")
        
                with report.head:
                    dominate.tags.link(rel='stylesheet',href=config['css'])
        
                _entrylist = report.add(dominate.tags.ul())
        
                for this_entry in procd_entries:
        
                    if this_entry["correction"] == "":
    
                        _anitem = _entrylist.add(dominate.tags.li())
                        _anitem += dominate.tags.h3(str(this_entry["d"]))
                        _anitem += dominate.tags.h4(this_entry["hash"])
                        _anitem += dominate.tags.h4(" ".join(this_entry["t"]))
        
                        for j in this_entry["f"]:
                            _anitem += dominate.tags.h4(dominate.tags.a(j,
                                href=config["notebook_directory"]+"/"+this_entry["hash"]+"/"+j))
        
                        _anitem += dominate.tags.p(dominate.util.raw(this_entry["n"]))
    
                    else:
    
                        _anitem += dominate.tags.h6("--- correction ---")
    
                        _anitem += dominate.tags.h4(this_entry["hash"])
                        _anitem += dominate.tags.h4(" ".join(this_entry["t"]))
        
                        for j in this_entry["f"]:
                            _anitem += dominate.tags.h4(dominate.tags.a(j,
                                href=config["notebook_directory"]+"/"+this_entry["hash"]+"/"+j))
        
                        _anitem += dominate.tags.p(dominate.util.raw(this_entry["n"]))
    
                test_report.write(report.render())

    if args.q:

        query_result = list()

        for each_key in raw_notebook:
    
            each_entry = raw_notebook[each_key]

            if args.q in each_entry['t']:

                query_result.append(each_entry)

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
                    _anitem += dominate.tags.h4(i["hash"])
                    _anitem += dominate.tags.h4(" ".join(i["t"]))
    
                    for j in i["f"]:
                        _anitem += dominate.tags.h4(dominate.tags.a(j,
                            href=config["notebook_directory"]+"/"+i["hash"]+"/"+j))
    
                    _anitem += dominate.tags.p(dominate.util.raw(i["n"]))

                else:

                    _anitem += dominate.tags.h6("--- correction ---")

                    _anitem += dominate.tags.h4(i["hash"])
                    _anitem += dominate.tags.h4(" ".join(i["t"]))
    
                    for j in i["f"]:
                        _anitem += dominate.tags.h4(dominate.tags.a(j,
                            href=config["notebook_directory"]+"/"+i["hash"]+"/"+j))
    
                    _anitem += dominate.tags.p(dominate.util.raw(i["n"]))

            f.write(report.render())

    with open(config["notebook_directory"]+"/"+config["raw_notebook"],"w") as notefile:
        notefile.write(yaml.dump(raw_notebook))

    if args.c:
        shutil.copyfile(
           config["template_file"],
           config["intake_file"]
           )

