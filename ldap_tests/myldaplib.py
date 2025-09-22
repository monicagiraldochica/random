#!/usr/bin/env python3
import ldap3
import subprocess
import json
import string

def readJSON(json_file,key):
	try:
		fin = open(json_file)
		json_object = json.load(fin)
		fin.close()
		return json_object[key]
	except:
		print("Error opening JSON file: "+json_file)
		return ""

def connect_to_ldap(server, user, password):
    try:
        server = ldap3.Server(server)
        conn = ldap3.Connection(server, user, password, auto_bind=True)
        return conn
    except ldap3.core.exceptions.LDAPBindError as e:
        print("LDAP bind error:", e)
        return None

def search_lab_members(conn,search_base):
    search_attributes = ['cn', 'member']

    groups = {}
    for letter in string.ascii_lowercase:
        search_filter = f"(&(objectClass=posixGroup)(cn=sg-{letter}*))"
        entries = conn.extend.standard.paged_search(search_base, search_filter, attributes=search_attributes, paged_size=500, generator=False)
        for entry in entries:
            if 'attributes' in entry:
                attrs = entry['attributes']
                group = attrs['cn'][0]
                members = attrs['member']
                groups[group] = members
    return groups

def search_posix_groups(conn,search_base):
    search_attributes = ['cn', 'gidNumber']

    groups = {}
    for letter in string.ascii_lowercase:
        search_filter = f"(&(objectClass=posixGroup)(cn={letter}*))"
        entries = conn.extend.standard.paged_search(search_base, search_filter, attributes=search_attributes, paged_size=500, generator=False)
        for entry in entries:
            if 'attributes' in entry:
                attrs = entry['attributes']
                group = attrs['cn'][0]
                try:
                    gid = int(attrs['gidNumber'][0])
                except:
                    gid = int(attrs['gidNumber'])
                groups[group] = gid
    return groups

def getGID(conn,gidNumber):
	search_base = readJSON("mainldap.json","ldap_setup")
	search_filter = "(objectClass=posixGroup)"
	attributes = ['cn', 'gidNumber']

	conn.search(search_base, search_filter, attributes=attributes)
	for entry in conn.response:
		if 'attributes' in entry:
			attributes = entry['attributes']
			try:
				gidNum = int(attributes['gidNumber'][0])
			except:
				gidNum = int(attributes['gidNumber'])
			group = attributes['cn'][0]
			if gidNum==gidNumber:
				return group
	return None

def getgidNumber(conn,gid):
	search_base = readJSON("mainldap.json","ldap_setup")
	search_filter = "(objectClass=posixGroup)"
	attributes = ['cn', 'gidNumber']

	conn.search(search_base, search_filter, attributes=attributes)
	for entry in conn.response:
		if 'attributes' in entry:
			attributes = entry['attributes']
			try:
				gidNum = int(attributes['gidNumber'][0])
			except:
				gidNum = int(attributes['gidNumber'])
			group = attributes['cn'][0]
			if group==gid:
				return gidNum
	return None

def search_posix_users(conn,search_base):
    search_attributes = ['cn', 'uidNumber']

    users = {}
    for letter in string.ascii_lowercase:
        search_filter = f"(&(objectClass=posixAccount)(uid={letter}*))"
        entries = conn.extend.standard.paged_search(search_base, search_filter, attributes=search_attributes, paged_size=500, generator=False)
        for entry in entries:
            if 'attributes' in entry:
                attrs = entry['attributes']
                user = attrs['cn'][0]
                try:
                    uid = int(attrs['uidNumber'][0])
                except:
                    uid = int(attrs['uidNumber'])
                users[user] = uid
    return users

def getUserInfo(conn,username,ldapfile):
	search_base = "ou=Users,"+readJSON(ldapfile,"ldap_setup")
	search_filter = "(objectClass=posixAccount)"
	attributes = ['cn', 'uidNumber', 'gidNumber']

	dic = {"uidNumber":None,"gidNumber":None}
	conn.search(search_base, search_filter, attributes=attributes)
	for entry in conn.response:
		if 'attributes' in entry:
			attributes = entry['attributes']
			user = attributes['cn'][0]
			if user==username:
				try:
					uid = int(attributes['uidNumber'][0])
					gid = int(attributes['gidNumber'][0])
				except:
					uid = int(attributes['uidNumber'])
					gid = int(attributes['gidNumber'])
				dic["uidNumber"] = uid
				dic["gidNumber"] = gid
				break
	
	return dic

def getDisabledUser(conn,username,ldapfile):
	search_base = "ou=DisableUsers,"+readJSON(ldapfile,"ldap_setup")
	search_filter = "(objectClass=posixAccount)"
	attributes = ['cn', 'uidNumber', 'gidNumber']

	dic = {"uidNumber":None,"gidNumber":None}
	conn.search(search_base, search_filter, attributes=attributes)
	for entry in conn.response:
		if 'attributes' in entry:
			attributes = entry['attributes']
			user = attributes['cn'][0]
			if user==username:
				try:
					uid = int(attributes['uidNumber'][0])
					gid = int(attributes['gidNumber'][0])
				except:
					uid = int(attributes['uidNumber'])
					gid = int(attributes['gidNumber'])
				dic["uidNumber"] = uid
				dic["gidNumber"] = gid
				break
	return dic

def find_next_available_gid(groups):
    max_gid = max(groups.values()) if groups else 999  # Set an initial value if no groups are found
    return max_gid + 1

def find_next_available_uid(users):
    max_uid = max(users.values()) if users else 999  # Set an initial value if no groups are found
    return max_uid + 1

def find_duplicate_gids(groups):
    duplicate_gids = {}
    seen_gids = set()
    for group, gid in groups.items():
        if gid in seen_gids:
            if gid not in duplicate_gids:
                duplicate_gids[gid] = [group]
            else:
                duplicate_gids[gid].append(group)
        else:
            seen_gids.add(gid)
    return duplicate_gids

def find_duplicate_uids(users):
    duplicate_uids = {}
    seen_uids = set()
    for user, uid in users.items():
        if uid in seen_uids:
            if uid not in duplicate_uids:
                duplicate_uids[uid] = [user]
            else:
                duplicate_uids[uid].append(user)
        else:
            seen_uids.add(uid)
    return duplicate_uids

def getStdOut(command):
        try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                return [result.stdout.replace("\n",""),result.stderr.replace("\n","")]

        except subprocess.CalledProcessError as e:
                 return ["",""]

