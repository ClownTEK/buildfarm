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

import os
import socket
import smtplib

import pisi.specfile

from buildfarm.auth import Auth
from buildfarm import logger, templates, utils
from buildfarm.config import configuration as conf


class MailerError(Exception):
    pass

def send(message, pspec = "", _type = "", subject=""):

    if not conf.sendemail:
        logger.info("Sending of notification e-mails is turned off.")
        return


    # Authentication stuff
    (username, password) = Auth().get_credentials("Mailer")

    # subjectID: ex: [release/{devel,stable}/arch]
    subjectID = "%s/%s/%s" % (conf.release.capitalize(),
                              conf.subrepository,
                              conf.architecture)


    recipients_name, recipients_email = [], []
    package_name = ""
    last_log = ""
    if pspec:
        spec = pisi.specfile.SpecFile(os.path.join(utils.get_local_repository_url(), pspec))
        recipients_name.append(spec.source.packager.name)
        recipients_email.append(spec.source.packager.email)
        package_name = os.path.basename(os.path.dirname(pspec))
        last_log = open(os.path.join(utils.get_package_log_directory(), "%s.txt" % package_name)).read()

    message = templates._all[_type] % {
                                        'log'          : last_log,
                                        'recipientName': " ".join(recipients_name),
                                        'mailTo'       : ", ".join(recipients_email),
                                        'ccList'       : conf.cclist,
                                        'mailFrom'     : conf.mailfrom,
                                        'announceAddr' : conf.announceaddr,
                                        'subject'      : pspec or subject or _type,
                                        'message'      : message,
                                        'pspec'        : pspec,
                                        'type'         : _type,
                                        'packagename'  : package_name,
                                        'distribution' : conf.name,
                                        'release'      : conf.release,
                                        'arch'         : conf.architecture,
                                        'logsdir'      : subjectID,
                                        'subjectID'    : subjectID,
                                     }

    # timeout value in seconds
    socket.setdefaulttimeout(10)

    try:
        session = smtplib.SMTP(conf.smtpserver)
    except:
        logger.error("Failed sending e-mail: Couldn't open session on %s." % conf.smtpserver)
        return

    try:
        session.login(username, password)
    except smtplib.SMTPAuthenticationError:
        logger.error("Failed sending e-mail: Authentication failed.")
        return

    try:
        if _type == "announce":
            session.sendmail(conf.mailfrom, conf.announceaddr, message)
        else:
            session.sendmail(conf.mailfrom, recipients_email + conf.cclist.split(","), message)
    except smtplib.SMTPRecipientsRefused:
        logger.error("Failed sending e-mail: Recipient refused probably because of a non-authenticated session.")

def error(message, pspec, subject=""):
    send(message, pspec, _type="error", subject=subject)

def info(message, subject=""):
    send(message, _type="info", subject=subject)

def announce(message, subject=""):
    send(message, _type="announce", subject=subject)
