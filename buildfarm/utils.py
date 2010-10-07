#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Please read the COPYING file.

# Various helper functions for pisi packages

import os
import glob
import pisi.api

from buildfarm.config import configuration as conf
constants = pisi.api.ctx.const

def create_directories():
    directories = [
                    conf.workdir,
                    conf.buildfarmdir,
                    conf.repositorydir,
                    conf.logdir,
                    conf.binarypath,
                    conf.testpath,
                    conf.deltapath,
                    conf.debugpath,
                    get_local_repository_url(),
                    get_package_log_directory(),
                  ]

    for directory in directories:
        if directory and not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError:
                raise ("Directory '%s' cannot be created." % directory)

def get_local_repository_url():
    return os.path.join(conf.repositorydir, conf.release, conf.subrepository)

def get_remote_repository_url():
    return os.path.join(conf.scmrepositorybaseurl, conf.release, conf.subrepository)

def get_package_log_directory():
    return os.path.join(conf.logdir, conf.release, conf.subrepository, conf.architecture)

def get_expected_file_name(pspec):
    from pisi.specfile import SpecFile
    spec = SpecFile(pspec)
    last_update = spec.history[0]

    return pisi.util.package_filename(spec.packages[0].name,
                                      last_update.version,
                                      last_update.release)

def get_package_name(p):
    return pisi.util.split_package_filename(p)[0]

def get_package_name_from_path(p):
    return os.path.basename(os.path.dirname(p))

def is_delta_package(p):
    return p.endswith(constants.delta_package_suffix)

def is_debug_package(p):
    package_name = get_package_name(p)
    return package_name.endswith(constants.debug_name_suffix)

# FIXME:Should be reimplemented with buildnoless pisi
"""
def get_delta_packages(path, name, target=None):
    if target and isinstance(target, int):
        # Return delta packages goint to target
        pattern = "%s-[0-9]*-%d%s" % (name, target, constants.delta_package_suffix)
    else:
        # Return all delta packages
        pattern = "%s-[0-9]*-[0-9]*%s" % constants.delta_package_suffix
    return glob.glob1(path, pattern)

def get_deltas_not_going_to(path, package):
    # e.g. package <- kernel-2.6.25.20-114-45.pisi
    # Returns the list of delta packages in 'path' for 'package' going from any
    # build to any build other than 45.
    # return -> ['kernel-41-42-delta.pisi', 'kernel-41-44.delta-pisi', etc]
    name = get_package_name(package)
    target_build = get_build_no(package)
    return list(set(get_delta_packages(path, name)).difference(get_delta_packages(path, name, target_build)))
"""

