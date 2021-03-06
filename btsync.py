import httplib
import base64
import urllib
import json


class BTSync(object):
    """ The BTSync class is a light wrapper around the Bittorrent Sync API.
    Currently to use the API you will need to apply for a key. You can find out
    how to do that, and learn more about the btsync API here:

        http://www.bittorrent.com/sync/developers/api

    The docstrings of this class' methods were copied from the above site.

    """

    def __init__(self, host='localhost', port='8888',
                 user='admin', pswd='password'):
        """
        Parameters
        ----------
        host : str
            IP address that the btsync api responds at.
        port : str
            Port that the btsync api responds at.
        user : str
            optional username to use if btsync api is protected.
        pswd : str
            optional password to use if btsync api is protected.

        Notes
        -----
        The host, port, user, and pswd must match the config.json file.

        """
        self.conn = httplib.HTTPConnection('{}:{}'.format(host, port))
        auth = 'Basic ' + base64.b64encode('{}:{}'.format(user, pswd))
        self.headers = {'Authorization': auth}

    def get_folders(self, secret=None):
        """
        Returns an array with folders info. If a secret is specified, will
        return info about the folder with this secret.

        [
            {
                "dir": "\\\\?\\D:\\share",
                "secret": "A54HDDMPN4T4BTBT7SPBWXDB7JVYZ2K6D",
                "size": 23762511569,
                "type": "read_write",
                "files": 3206,
                "error": 0,
                "indexing": 0
            }
        ]

        http://[address]:[port]/api?method=get_folders[&secret=(secret)]

        secret (optional) - if a secret is specified, will return info about
        the folder with this secret
        """
        params = {'method': 'get_folders'}
        if secret is not None:
            params['secret'] = secret
        return self._request(params)

    def add_folder(self, path, secret=None):
        """
        Adds a folder to Sync. If a secret is not specified, it will be
        generated automatically. The folder will have to pre-exist on the disk
        and Sync will add it into a list of syncing folders.

        Returns '0' if no errors, error code and error message otherwise.

        { "error": 0 }

        http://[address]:[port]/api?method=add_folder&dir=(folderPath)[&secret=(secret)&selective_sync=1]

        dir (required) - specify path to the sync folder
        secret (optional) - specify folder secret
        selective_sync (optional) - specify sync mode, selective - 1, all files
                                    (default) - 0
        """
        params = {'method': 'add_folder', 'dir': path}
        if secret is not None:
            params['secret'] = secret
        return self._request(params)

    def remove_folder(self, secret):
        """
        Removes folder from Sync while leaving actual folder and files on disk.
        It will remove a folder from the Sync list of folders and does not
        touch any files or folders on disk. Returns '0' if no error, '1' if
        there's no folder with specified secret.

        { "error": 0 }

        http://[address]:[port]/api?method=remove_folder&secret=(secret)

        secret (required) - specify folder secret
        """
        params = {'method': 'remove_folder', 'secret': secret}
        return self._request(params)

    def get_files(self, secret, path=None):
        """
        Returns list of files within the specified directory. If a directory is
        not specified, will return list of files and folders within the root
        folder. Note that the Selective Sync function is only available in the
        API at this time.

        [
            {
                "name": "images",
                "state": "created",
                "type": "folder"
            },
            {
                "have_pieces": 1,
                "name": "index.html",
                "size": 2726,
                "state": "created",
                "total_pieces": 1,
                "type": "file",
                "download": 1 // only for selective sync folders
            }
        ]

        http://[address]:[port]/api?method=get_files&secret=(secret)[&path=(path)]

        secret (required) - must specify folder secret
        path (optional) - specify path to a subfolder of the sync folder.
        """
        params = {'method': 'get_files'}
        if path is not None:
            params['path'] = path
        return self._request(params)

    def get_secrets(self, secret=None):
        """
        Generates read-write, read-only and encryption read-only secrets. If
        `secret` parameter is specified, will return secrets available for
        sharing under this secret.

        The Encryption Secret is new functionality. This is a secret for a
        read-only peer with encrypted content (the peer can sync files but can
        not see their content). One example use is if a user wanted to backup
        files to an untrusted, unsecure, or public location. This is set to
        disabled by default for all users but included in the API.

        {
            "read_only": "ECK2S6MDDD7EOKKJZOQNOWDTJBEEUKGME",
            "read_write": "DPFABC4IZX33WBDRXRPPCVYA353WSC3Q6",
            "encryption": "G3PNU7KTYM63VNQZFPP3Q3GAMTPRWDEZ"
        }

        http://[address]:[port]/api?method=get_secrets[&secret=(secret)&type=encryption]

        secret (required) - must specify folder secret
        type (optional) - if type=encrypted, generate secret with support of
                            encrypted peer
        """
        params = {'method': 'get_secrets'}
        if secret is not None:
            params['secret'] = secret
        return self._request(params)

    def get_os(self):
        """
        Returns OS name where BitTorrent Sync is running.
        """ 
        
        params = {'method': 'get_os'}
        return self._request(params)
        
    def get_version(self):
        """
        Returns BitTorrent Sync version.
        """
        
        params = {'method': 'get_version'}
        return self._request(params)

    def get_speed(self):
        """
        Returns current upload and download speed.
        """

        params = {'method': 'get_speed'}
        return self._request(params)

    def shutdown(self):
        """
        Gracefully stops Sync.
        """

        params = {'method': 'shutdown'}
        return self._request(params)

    def get_prefs(self):
        """
        Returns BitTorrent Sync preferences. Contains dictionary with advanced preferences. 
        Please see Sync user guide for description of each option.
        """
        
        params = {'method': 'get_prefs'}
        return self._request(params)

    def set_prefs(self, **prefs):
        """
        Sets BitTorrent Sync preferences. Parameters are the same as in 'Get preferences'. 
        Advanced preferences are set as general settings. Returns current settings.
        """
        
        params = {'method': 'set_prefs'}
        params.update(prefs)
        return self._request(params)

    def get_folder_peers(self, secret):
        """
        Returns list of peers connected to the specified folder.
        """
        
        params = {'method': 'get_folder_peers', 'secret': secret}
        return self._request(params)
    
    def get_folder_prefs(self, secret):
        """
        Returns preferences for the specified sync folder.
        """
        
        params = {'method': 'get_folder_prefs', 'secret': secret}
        return self._request(params)

    def set_folder_prefs(self, secret, **prefs):
        """
        Sets preferences for the specified sync folder. Parameters are the same as in ‘Get folder preferences’. Returns current settings.
        """

        params = {'method': 'set_folder_prefs', 'secret': secret} 
        params.update(prefs)
        return self._request(params)
   
    def set_folder_hosts(self, secret, *hosts):
        """
        Sets one or several predefined hosts for the specified sync folder. Existing list of hosts will be replaced. 
        Returns current hosts if set successfully, error code otherwise.
        """
        
        if hosts:
            params = {'method': 'set_folder_hosts', 'secret': secret, 'hosts': ",".join(hosts)}
        else:
            params = {'method': 'set_folder_hosts', 'secret': secret, 'hosts': ""}
        return self._request(params)
    
    def get_folder_hosts(self, secret):
        """
        Returns list of predefined hosts for the folder, or error code if a secret is not specified.
        """
        params = {'method': 'get_folder_hosts', 'secret': secret}
        return self._request(params)
        
    def _request(self, params):
        params = urllib.urlencode(params)
        self.conn.request('GET', '/api?' + params, '', self.headers)
        resp = self.conn.getresponse()
        if resp.status == 200:
            return json.load(resp)
        else:
            return None
