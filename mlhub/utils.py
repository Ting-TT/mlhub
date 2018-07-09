#!/usr/bin/python3
#
# mlhub - Machine Learning Model Repository
#
# A command line tool for managing machine learning models.
#
# Copyright 2018 (c) Graham.Williams@togaware.com All rights reserved. 
#
# This file is part of mlhub.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the ""Software""), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.

import os
import sys
import yaml
import urllib.request
import platform
import subprocess

from mlhub.constants import APPX, MLINIT, CMD, MLHUB, META_YAML, META_YML, DESC_YAML, DESC_YML, debug, DEBUG, USAGE, EXT_MLM, VERSION, APP

def print_usage():
    print(CMD)
    print(USAGE.format(CMD, EXT_MLM, MLINIT, MLHUB, MLINIT, VERSION, APP))

def create_init():
    """Check if the init dir exists and if not then create it."""

    if not os.path.exists(MLINIT): os.makedirs(MLINIT)

    return(MLINIT)

def get_repo(repo):
    """Determine the repository to use: command line, environment, default."""

    if repo is None:
        repo = MLHUB
    else:
        repo = os.path.join(repo, "") # Ensure trailing slash.

    return repo

def get_repo_meta_data(repo):
    """Read the repositories meta data file and return as a list."""

    try:
        url  = repo + META_YAML
        meta = list(yaml.load_all(urllib.request.urlopen(url).read()))
    except:
        try: 
            url  = repo + META_YML
            meta = list(yaml.load_all(urllib.request.urlopen(url).read()))
        except:
            msg = """Cannot access the Internet.

To list the models available from an ML Hub you will need an Internet connection.

You can list the models already installed locally with:

  $ ml installed
"""
            print(msg, file=sys.stderr)
            sys.exit()
        
    return(meta)

def print_meta_line(entry):
    name    = entry["meta"]["name"]
    version = entry["meta"]["version"]
    try:
        title   = entry["meta"]["title"]
    except:
        title   = entry["meta"]["description"]

    # One line message.

    MAX_TITLE = 24
    MAX_DESCR = 44
    
    if len(title) > MAX_DESCR:
        long = "..."
    else:
        long = ""

    FORMATTER = "{0:<TITLE.TITLE} {1:^6} {2:<DESCR.DESCR}{3}".replace("TITLE", str(MAX_TITLE)).replace("DESCR", str(MAX_DESCR))
    print(FORMATTER.format(name, version, title, long))

#------------------------------------------------------------------------
# CHECK MODEL INSTALLED
    
def check_model_installed(model):

    path = MLINIT + model
    if not os.path.exists(path):
        model = os.path.basename(path)
        msg = """{}model '{}' is not installed ({}).

Check for the model name amongst those installed:

  $ {} installed

Models can be installed from the ML Hub:

  $ {} install {}

Available pakages on the ML Hub can be listed with:

  $ {} available"""
        msg = msg.format(APPX, model, MLINIT, CMD, CMD, model, CMD)
        print(msg, file=sys.stderr)
        sys.exit(1)
        
    return(True)

#-----------------------------------------------------------------------
# LOAD DESCRIPTION

def load_description(model):

    desc = os.path.join(MLINIT, model, DESC_YAML)
    if os.path.exists(desc):
        entry = yaml.load(open(desc))
    else:
        desc = os.path.join(MLINIT, model, DESC_YML)
        if os.path.exists(desc):
            entry = yaml.load(open(desc))
        else:
            msg = "{}no '{}' found for '{}'."
            msg = msg.format(APPX, DESC_YAML, model)
            print(msg, file=sys.stderr)
            sys.exit(1)
    return(entry)
    
#-----------------------------------------------------------------------
# RUN CONFIGURE SCRIPT

def configure(path, script, quiet):
    """Run the provided configure scripts and handle errors and output."""

    configured = False
    
    # For now only tested/working with Ubuntu
    
    if platform.dist()[0] in set(['debian', 'Ubuntu']):
        conf = os.path.join(path, script)
        if os.path.exists(conf):
            interp = interpreter(script)
            if not quiet:
                msg = "Configuring using '{}'...".format(conf)
                print(msg)
            cmd = "{} {}".format(interp, script)
            proc = subprocess.Popen(cmd, shell=True, cwd=path, stderr=subprocess.PIPE)
            output, errors = proc.communicate()
            if proc.returncode != 0:
                print("An error was encountered:\n")
                print(errors.decode("utf-8"))
            configured = True

    return(configured)

#-----------------------------------------------------------------------
# DETERMINE THE CORRECT INTERPRETER FOR THE GIVEN SCRIPT NAME

def interpreter(script):
    
    (root, ext) = os.path.splitext(script)
    ext = ext.strip()
    if ext == ".sh":
        interpreter = "bash"
    elif ext == ".R":
        interpreter = "Rscript"
    elif ext == ".py":
        interpreter = "python3"
    else:
        msg = "Could not determine an interpreter for extension '{}'".format(ext)
        print(msg, file=sys.stderr)
        sys.exit()

    return(interpreter)
