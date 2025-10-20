#!/usr/bin/env python3
import argparse
import sys 
import getopt
import myldaplib
import ldap3
import os
import shutil
import paramiko
import getpass
import re

def createDirs(conn,netID,piID,isPI,uidNumber,gidNumber,reEnbl):
	try:
		dic = {f"/qumulo_homefs/{netID}/":[700,uidNumber,gidNumber],
			f"/group/{piID}/":[755,"root",f"sg-{piID}"],
			f"/group/{piID}/work":[2770,"root",f"sg-{piID}"],
			f"/scratch/g/{piID}":[2770,"root",f"sg-{piID}"]}

		print("\nCreating directories:")
		for newdir,array in dic.items():
			os.system(f"mkdir {newdir}")
			os.system(f"chmod {array[0]} {newdir}")
			os.system(f"chown -R {array[1]}:{array[2]} {newdir}")
			input(f"{newdir} successfully created [Enter]")

			if not isPI:
				break

		if not reEnbl:
			for fname in [".bash_logout", ".bash_profile", ".bashrc", ".emacs"]:
				shutil.copy(f"/adminfs/skel/{fname}",list(dic.keys())[0])
			input(f"{list(dic.keys())[0]} successfully populated [Enter]")

	except:
		exitError(conn, "Could not create directories")

def ssh_command(hostname, port, username, password, command):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	output = None

	try:
		client.connect(hostname, port=port, username=username, password=password)
		stdin, stdout, stderr = client.exec_command(command)
		output = stdout.read().decode()
		error = stderr.read().decode()
		if error:
			print(f"+++{error}+++")

	except Exception as e:
		print(f"An error occurred: {e}")
		output = None

	finally:
		client.close()
		return output

def testUser(cmd):
	if not os.path.isfile("ssh.json"):
		raise FileNotFoundError("ssh.json not found")
	
	host = myldaplib.readJSON("ssh.json","host")
	port = myldaplib.readJSON("ssh.json","port")
	user = input("YOUR username: ")
	password = getpass.getpass(prompt="YOUR password: ")

	return ssh_command(host, port, user, password, cmd)

def getSLURMcommands():
	if not os.path.isfile("ssh2.json"):
		raise FileNotFoundError("ssh2.json not found")

	host = myldaplib.readJSON("ssh2.json","host")
	port = myldaplib.readJSON("ssh2.json","port")
	user = myldaplib.readJSON("ssh2.json","user")
	password = myldaplib.readJSON("ssh2.json","password")
	slurm_cmds = []

	result = ssh_command(host, port, user, password, "python3 slurm-update-auth-fast.py")
	if result==None:
		return slurm_cmds

	for line in result.split("\n"):
		if line=="" or line.startswith("DRY RUN - ###") or line.startswith("sacctmgr remove"):
			continue
		slurm_cmds+=[line]
		
	return slurm_cmds

def closeConn(conn):
	conn.unbind()
	conn.closed

def exitError(conn,msg):
	print(msg)
	closeConn(conn)
	sys.exit()

def confirmArgs(netID,piID,first_name,last_name,email,neuroDesktops,neuroSquiggles,alt_contact,isPI):
	print("\nThese are the input arguments:\n" \
		f"NetID of the new user:{netID}.\n" \
		f"NetID of the PI:{piID}.\n" \
		f"First name of the new user:{first_name}.\n" \
		f"Last name of the new user:{last_name}.\n" \
		f"Email of the new user:{email}.\n" \
		f"Add user to Neurology Desktops:{neuroDesktops}.\n" \
		f"Add user to Squiggles:{neuroSquiggles}.\n" \
		f"Alternative contact:{alt_contact}.")

	if isPI:
		print("New user is a PI")
	else:
		print("New user is NOT a PI")

	if input("Does this look correct? [y]: ")=='y':
		return True
	else:
		return False

def duplicateGroups(conn,ldap_setup):
	groups = myldaplib.search_posix_groups(conn,ldap_setup)
	if not groups:
		exitError(conn, "No posixGroup objects found.")

	duplicate_gids = myldaplib.find_duplicate_gids(groups)
	if len(duplicate_gids)>0:
		return True
	return False

def duplicateUsers(conn,ldap_setup):
	users = myldaplib.search_posix_users(conn,ldap_setup)
	if not users:
		exitError(conn, "No posixAccount objects found.")

	duplicate_uids = myldaplib.find_duplicate_uids(users)
	if len(duplicate_uids)>0:
		return True
	return False

def printLDAPdic(dn,attributes):
	print(f"\ndn: {dn}\nattributes:")
	for key,val in attributes.items():
		print(f"{key}: {val}")

def createGroup(ldap_setup,piID,gidNumber,conn):
	dn = f"cn=sg-{piID},ou=Labs,ou=Groups,{ldap_setup}"
	attributes = {
		'objectClass': ['top', 'posixGroup','groupOfNames'],
		'cn': f"sg-{piID}",
		'gidNumber': gidNumber,
		'member': f"uid={piID},ou=Users,{ldap_setup}"
		}

	conn.add(dn, attributes=attributes)
	if conn.result['result']==0:
		print(f"Successfully created group sg-{piID}")

		if not duplicateGroups(conn,ldap_setup):
			input("No duplicate GIDs after creating group [Enter]")
		else:
			exitError(conn,"Duplicate GIDs found after creating group")
	else:
		exitError(conn,"Failed to create group sg-{piID}: {conn.result['message']}")

def createUser(ldap_setup,netID,uidNumber,gidNumber,first_name,last_name,email,conn):
	dn = f"uid={netID},ou=Users,{ldap_setup}"
	attributes = {
		'objectClass': ['top', 'shadowAccount', 'posixAccount', 'inetOrgPerson'],
		'cn': netID,
		'gidNumber': gidNumber,
		'homeDirectory': f"/home/{netID}",
		'sn': last_name,
		'uid': netID,
		'uidNumber': uidNumber,
		'displayName': first_name+" "+last_name,
		'gecos': first_name+" "+last_name,
		'givenName': first_name,
		'loginShell':'/bin/bash',
		'mail': email,
		'userPassword': "{SASL}"+netID+"@mcw.edu"
		}

	conn.add(dn, attributes=attributes)
		
	if conn.result['result']==0:
		print(f"Successfully added user {netID}")

		if not duplicateUsers(conn,ldap_setup):
			input("No duplicate UIDs found after adding user [Enter]")
		else:
			exitError(conn,"Duplicate UIDs found after adding user")

	else:
		exitError(conn,"Failed to add user {netID}: {conn.result['message']}")

def addUserToGroup(ldap_setup,piID,netID,conn):
	dn = f"cn=sg-{piID},ou=Labs,ou=Groups,{ldap_setup}"
	attributes = {'member': [(ldap3.MODIFY_ADD, [f"uid={netID},ou=Users,{ldap_setup}"])]}

	conn.modify(dn, attributes)
	if conn.result['result']==0:
		input(f"\nSuccessfully added user {netID} to sg-{piID} group [Enter]")
	else:
		exitError(conn,f"Failed to add user {netID} to sg-{piID} group: {conn.result['message']}")

def addUserToMachine(ldap_setup,machines,netID,conn):
	dn = f"cn=sg-{machines},ou=Neurology,ou=Machines,ou=Groups,{ldap_setup}"
	attributes = {'member': [(ldap3.MODIFY_ADD, [f"uid={netID},ou=Users,{ldap_setup}"])]}

	conn.modify(dn, attributes)
	if conn.result['result']==0:
		input(f"Successfully added user {netID} to Neurology Desktops [Enter]")
	else:
		exitError(conn, f"Failed to add user {netID} to Neurology Desktops: {conn.result['message']}")

def reEnableUser(ldap_setup,netID,conn):
	old_dn = f"uid={netID},ou=DisableUsers,{ldap_setup}"
	new_rdn = f"uid={netID}"
	new_superior_dn = f"ou=Users,{ldap_setup}"

	if conn.modify_dn(old_dn, new_rdn, new_superior=new_superior_dn, delete_old_dn=True):
		input(f"Successfully changed DN of '{old_dn}' to '{new_rdn},{new_superior_dn}' [Enter]")
	else:
		exitError(conn, f"Failed to change DN: {conn.result}")

def reEnableGroup(ldap_setup,piID,conn):
	old_dn = f"cn=sg-{piID},ou=DisableGroups,{ldap_setup}"
	new_rdn = f"cn=sg-{piID}"
	new_superior_dn = f"ou=Labs,ou=Groups,{ldap_setup}"

	if conn.modify_dn(old_dn, new_rdn, new_superior=new_superior_dn, delete_old_dn=True):
		input(f"Successfully changed DN of '{old_dn}' to '{new_rdn},{new_superior_dn}' [Enter]")
	else:
		exitError(conn, f"Failed to change DN: {conn.result}")

def sanitize_text(value, capitalize=False):
	"""Remove non-alphanumeric characters and normalize capitalization."""
	if value is None:
		return None
	
	value = re.sub(r'[^a-zA-Z0-9\s]', '', value.strip())

	if value=="":
		return None	
	
	return value.capitalize() if capitalize else value

def parse_arguments():
	# Get arguments
	parser = argparse.ArgumentParser(description="RCC on boarding automation script")
	parser.add_argument("--user", help="netID of the new user")
	parser.add_argument("--pi", help="netID of the PI")
	parser.add_argument("--first", help="First name of the new user")
	parser.add_argument("--last", help="Last name of the new user")
	parser.add_argument("--email", help="Email of the new user (@mcw.edu required)")
	parser.add_argument("--ndesktops", action="store_true", help="Include NeuroDesktops access")
	parser.add_argument("--nsquiggles", action="store_true", help="Include NeuroSquiggles access")
	parser.add_argument("--alt-contact", help="Alternative contact email (PI only)")
	args = parser.parse_args()

	netID = args.user or input("netID of the new user: ")
	piID = args.pi or input("netID of the PI (same as user if it's a PI): ")
	first_name = args.first or input("First name of the new user: ")
	last_name = args.last or input("Last name of the new user: ")
	email = args.email or input("Email of the new user: ")
	alt_contact = args.alt_contact
	
	# Clean arguments
	netID = sanitize_text(netID)
	piID = sanitize_text(piID)
	first_name = sanitize_text(first_name, capitalize=True)
	last_name = sanitize_text(last_name, capitalize=True)
	email = email.strip()
	alt_contact = sanitize_text(alt_contact)

	# Check required fields
	if not netID or not piID or not first_name or not last_name or not email:
		parser.print_help()
		sys.exit("Error: Missing arguments")

	if not email.endswith("@mcw.edu"):
		sys.exit("Error: email must be from MCW")

	# Check optional fields
	isPI = (netID == piID)
	if isPI and not alt_contact:
		alt_contact = input("Alternative contact ([Enter if none]): ")
		if alt_contact and not alt_contact.endswith("@mcw.edu"):
			sys.exit("Error: Alternative contact must be an MCW email")
	elif not isPI and alt_contact:
		print("Warning: Alternative contact provided, but user is not a PI. Ignoring input.")
		alt_contact = None

	return [ netID, piID, first_name, last_name, email, args.ndesktops, args.nsquiggles, alt_contact, isPI ]

def main():
	# Read and check arguments
	[ netID, piID, first_name, last_name, email, neuroDesktops, neuroSquiggles, alt_contact, isPI ] = parse_arguments()
	
	if not confirmArgs(netID,piID,first_name,last_name,email,neuroDesktops,neuroSquiggles,alt_contact,isPI):
		sys.exit("Correct arguments & re-run the script. Exiting.")

	# Check that the id is correct in Active directory
	if input(f"Is the netID '{netID}' for '{first_name} {last_name}' correct in Active Directory? [y]: ")!='y':
		netID = input("Correct netID: ")

	# Check that the PI is an actual PI
	if isPI:
		print(f"Check in Google to confirm that {first_name} {last_name} is a PI at MCW.")
		if input("Did the PI checkout? [y]: ")!='y':
			sys.exit("Investigate further before adding user")

	# Connect to LDAP
	json_file = "mainldap.json"
	ldap_setup = myldaplib.readJSON(json_file,"ldap_setup")
	conn = myldaplib.connect_to_ldap(myldaplib.readJSON(json_file,"ldap_server"), myldaplib.readJSON(json_file,"ldap_user"), myldaplib.readJSON(json_file,"ldap_password"))
	if not conn:
		sys.exit("Failed to connect to LDAP server.")

	# Make sure the user doesn't have an account already
	if myldaplib.getUserInfo(conn,netID,ldap_setup)["uidNumber"]!=None:
		exitError(conn, f"User {netID} already has an account. Send the following link that contains information on how to login: https://docs.rcc.mcw.edu/user-guide/access/login/")

	# Make sure the users' PI is an actual PI and already has an account (unless new user is a PI)
	if not isPI:
		piInfo = myldaplib.getUserInfo(conn,piID,ldap_setup)
		if piInfo["uidNumber"]==None:
			exitError(conn, f"The PI ({piID}) doesn't have an account. Ask the PI to request an account first.")

		gidNum = piInfo["gidNumber"]
		if gidNum==None or myldaplib.getGID(conn,gidNum,ldap_setup)!=f"sg-{piID}":
			exitError(conn, f"{piID} is not a PI")
		
	# Check that the user is not disabled
	reEnbl = False
	if myldaplib.getDisabledUser(conn,netID,json_file)["uidNumber"]!=None:
		if input(f"User {netID} is disabled. Do you whish to re-enable? [y]: ")!='y':
			exitError(conn, f"\nInvestigate further.")
		else:
			if isPI:
				reEnableGroup(ldap_setup,piID,conn)
			reEnableUser(ldap_setup,netID,conn)
			reEnbl = True
	print("\n")

	# Get next available UID
	if not reEnbl:
		users = myldaplib.search_posix_users(conn,ldap_setup)
		if not users:
			exitError(conn, "No posixAccount objects found.")

		uidNumber = myldaplib.find_next_available_uid(users)
		input(f"Using UID: {uidNumber} [Enter]")
	else:
		uidNumber = myldaplib.getUserInfo(conn,netID,ldap_setup)['uidNumber']
		input(f"UID of re-enabled user {netID}: {uidNumber} [Enter]")
	
	# If new user is not a PI, get the gidNumber of his/her PI
	if not isPI:
		gidNumber = myldaplib.getGIDnumber(conn,f"sg-{piID}",ldap_setup)
		if gidNumber==None:
			exitError(conn, f"Could not find the gidNumber of sg-{piID}")
		print(f"gidNumber for sg-{piID} is {gidNumber}")
		
	# If new user is a PI and not re-enabled, get the next available gidNumber
	elif not reEnbl:
		groups = myldaplib.search_posix_groups(conn,ldap_setup)
		if not groups:
			exitError(conn, "No posixGroup objects found.")

		gidNumber = myldaplib.find_next_available_gid(groups)
		input(f"Using GID: {gidNumber} [Enter]")

	# If new user is a re-enabled PI
	else:
		gidNumber = myldaplib.getUserInfo(conn,netID,ldap_setup)['gidNumber']
		input(f"GID of re-enabled group sg-{netID} is {gidNumber} [Enter]")

	# If it's a PI and is not re-enabled, create new group in ldap
	if isPI and not reEnbl:
		createGroup(ldap_setup,piID,gidNumber,conn)

	# Add new user in ldap (if it's not a re-enabled user)
	if not reEnbl:
		createUser(ldap_setup,netID,uidNumber,gidNumber,first_name,last_name,email,conn)
		userInfo = myldaplib.getUserInfo(conn,netID,ldap_setup)
		printLDAPdic(userInfo.pop("dn"),userInfo)
		if input("Looks OK? [y]: ")!="y" and input("Are you sure there are errors? Program will abort [y]: ")=='y':
			exitError(conn, "User created with errors")

	# If it's not a PI, add user to the new group
	if not isPI:
		if myldaplib.isMemberOfLab(conn,ldap_setup,piID,netID):
			if reEnbl:
				print(f"\n{netID} was already a member of sg-{piID}.")
			else:
				exitError(conn, f"{netID} is already a member of sg-{piID}. This doesn't make sense since it's a new user.")
		else:
			addUserToGroup(ldap_setup,piID,netID,conn)
			if not myldaplib.isMemberOfLab(conn,ldap_setup,piID,netID):
				exitError(conn, f"{netID} doesn't appear in the list of members for sg-{piID}. Check LDAP.")

	# Add to department machine if they ask so
	if neuroDesktops:
		addUserToMachine(ldap_setup,"neurology-desktops",netID,conn)
		
	if neuroSquiggles:
		addUserToMachine(ldap_setup,"neurology-squiggles",netID,conn)

	# Create directories and give permissions
	createDirs(conn,netID,piID,isPI,uidNumber,gidNumber,reEnbl)
	
	# Put user in SLURM scheduler
	input("\nLogin to hn01 [Enter]")
	input("ssh to sn01 [Enter]")
	input("Login as root [Enter]")
	try:
		for cmd in getSLURMcommands():
			input(f"Run: {cmd} [Enter]")
		
		remaining = getSLURMcommands()
		if len(remaining)==0:
			print("no more commands to run")
		else:
			print("There are still some commands that need to run: "+", ".join(remaining))
			input("Run the commands that still need to be run and re-check the output of python3 slurm-update-auth-fast.py [Enter]")
	except FileNotFoundError as e:
		exitError(conn, e)

	# Set home directory quota
	if not reEnbl:
		secret_line1 = myldaplib.readJSON(json_file,"secret_line1")
		input(f"\nSet directory quota:\n{secret_line1}")
		input(f"Add homefs/{netID}/ with 100GB [Enter]")

		if netID==piID:
			input(f"Add groupfs/{piID}/ with 1TB [Enter]")
			input("Mount SMB qfs2 (use mcwcorp) [Enter]")
			input(f"Go to KeePass and get the password for admin in Storage > qfs1 nvme. Do not close KeePass. [Enter]")
			secret_line2 = myldaplib.readJSON(json_file,"secret_line2")
			input(secret_line2)
			print("Now you can close KeePass")
			input(f"Create quota for scratchfs/g/{piID}/ with 5TB")

	# Send email
	if not os.path.isfile("email_newAcct.txt"):
		exitError(conn, "Could not find email_newAcct.txt")
	file1 = open("email_newAcct.txt","r")
	email_content = file1.read()
	file1.close()
	email_content = email_content.replace("<first_name>",first_name).replace("<netID>",netID)
	print("\n"+email_content)
	input("Send email. Make sure to change Default Customer for the correct UserID! [Enter]")

	# Unbind and close the connection
	closeConn(conn)

if __name__ == "__main__":
	main()
