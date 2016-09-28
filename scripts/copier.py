#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import paramiko


class RemoteFileCopier(object):

    def __init__(self, server, username, password=None):

        self.server = server
        self.username = username
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.server, username=self.username,
                password=password)


rfc = RemoteFileCopier('172.22.68.155', 'sysadmin')
