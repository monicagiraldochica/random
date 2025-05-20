#!/usr/bin/env python3
import sys 
import getopt
import myldaplib
import ldap3

def printHelp():
	print("Mandatory arguments:\n"
		"-u newNetID or --user=newNetID for the networkID of the new user.\n" \
		"-p piNetID or --pi=piNetID for the networkID of the PI (same as newNetID if new user is a PI)\n" \
		"-f first_name or --first=first_name for the first name of the user\n" \
		"-l last_name or --last=last_name for the last name of the user\n" \
		"--ndesktops=True to add user to Neurology Desktops\n" \
		"--nsquiggles=True to add user to Neurology Squiggles\n" \
		"-h or --help for this message.")

def closeConn(conn):
	conn.unbind()
	conn.closed

def exitError(conn,msg):
	print(msg)
	closeConn(conn)

def main():
	# Read arguments
	netID = None
	piID = None
	first_name = None
	last_name = None
	email = None
	neuroDesktops = False
	neuroSquiggles = False
	
	argv = sys.argv[1:]
	try:
		opts, args = getopt.getopt(argv, "u:p:h:f:l:e:", ["user=", "pi=", "help=", "first=", "last=", "email=", "ndesktops=", "nsquiggles="])
	except:
		printHelp()
		exit("Error reading arguments")

	for opt,arg in opts:
		if opt in ["-u", "--user"]:
			netID = arg
		elif opt in ["-p", "--pi"]:
			piID = arg
		elif opt in ["-h","--help"]:
			printHelp()
			exit()
		elif opt in ["-f","--first"]:
			first_name = arg
		elif opt in ["-l","--last"]:
			last_name = arg
		elif opt in ["-e", "--email"]:
			email = arg
		elif opt in ["--ndesktops"]:
			neuroDesktops = arg
		elif opt in ["--nsquiggles"]:
			neuroSquiggles = arg

	if netID==None or piID==None or first_name==None or last_name==None or email==None:
		printHelp()
		exit("Missing arguments")
	if not email.endswith("@mcw.edu"):
		exit("email must be from MCW")
	if not neuroDesktops in [True, False]:
		printHelp()
		exit("bad value for --ndesktops")
	if not neuroSquiggles in [True, False]:
		printHelp()
		exit("bad valie for --nsquiggles")

	# Connect to LDAP
	#json_file = "mainldap.json"
	json_file = "testldap.json"
	ldap_setup = myldaplib.readJSON(json_file,"ldap_setup")
	conn = myldaplib.connect_to_ldap(myldaplib.readJSON(json_file,"ldap_server"), myldaplib.readJSON(json_file,"ldap_user"), myldaplib.readJSON(json_file,"ldap_password"))
	if not conn:
		exit("Failed to connect to LDAP server.")

	# Make sure the user doesn't have an account already
	if myldaplib.getUserInfo(conn,netID,json_file)["uidNumber"]!=None:
		exitError(conn, f"User {netID} already has an account. Send the following link that contains information on how to login: https://docs.rcc.mcw.edu/user-guide/access/login/")

	# Make sure the PI is an actual PI and already has an account (unless new user is a PI)
	if netID!=piID:
		piInfo = myldaplib.getUserInfo(conn,piID,json_file)
		if piInfo["uidNumber"]==None:
			exitError(conn, f"The PI ({piID}) doesn't have an account. Ask the PI to request an account first.")

		gidNum = piInfo["gidNumber"]
		if gidNum==None or myldaplib.getGID(conn,gidNum)!="sg-"+piID:
			exitError(conn, f"{piID} is not a PI")
		
	# Check that the user is not disabled
	disabledInfo = myldaplib.getDisabledUser(conn,netID,json_file)
	if disabledInfo["uidNumber"]!=None:
		print(f"User {netID} is disabled")

		# Find out if it was a PI
		gidNum = disabledInfo["gidNumber"]
		if gidNum==None:
			exitError(conn, f"Could not find the gid for {gidNum}")
		gid = myldaplib.getGID(conn,gidNum)
		if gid=="sg-"+netID:
			print(f"The user was a PI ({gid})")

			# Re-enable the group before enabling the user
			current_dn = "cn="+gid+",ou=DisableGroups,"+ldap_setup
			new_parent_dn = "ou=Labs,ou=Groups,"+ldap_setup

			conn.modify_dn(current_dn, "cn="+gid, new_superior=new_parent_dn)
			if conn.result["result"]==0:
				print(f"Group {gid} moved from DisabledGroups to Groups/Labs successfully.")
			else:
				exitError(conn, f"Error moving group {gid} from DisabledGroups to Groups/Labs")

		# Enable the user
		current_dn = "uid="+netID+",ou=DisableUsers,"+ldap_setup
		new_parent_dn = "ou=Users,"+ldap_setup

		conn.modify_dn(current_dn, "uid="+netID, new_superior=new_parent_dn)
		if conn.result["result"]==0:
			print(f"User {netID} moved from DisabledUsers to Users sucessfully.")
		else:
			exitError(conn, f"Error moving user {netID} from DisabledUsers to Users")

		# If it's not a PI, put user into the new group
		# THIS BELOW CHANGES FOR NEW LDAP
		# member changed to memberUid & different format
		if netID!=piID:
			dn = "cn=sg-"+piID+",ou=Labs,ou=Groups,"+ldap_setup
			dic = {
				'member': [(ldap3.MODIFY_ADD, ["uid="+netID+",ou=Users"+ldap_setup])]
				}
			conn.modify(dn, dic)

			if conn.result['result'] == 0:
				print(f"Successfully added {netID} to sg-{piID}")
			else:
				exitError(conn, f"Failed to add {netID} to sg-{piID}: {conn.result['message']}")

	# If the user was not disabled
	else:
		# Get next available UID
		users = myldaplib.search_posix_users(conn)
		if not users:
			exitError(conn, "No posixAccount objects found.")

		uidNumber = myldaplib.find_next_available_uid(users)
		print(f"Next available UID: {uidNumber}")

		# If new user is not a PI, get the gidNumber of that PI
		if netID!=piID:
			gidNumber = myldaplib.getgidNumber(conn,"sg-"+piID)
			if gidNumber==None:
				exitError(conn, f"Could not find the gidNumber of sg-"+piID)
			print(f"gidNumber for sg-{piID} is {gidNumber}")
		
		# If new user is a PI, get the next available gidNumber
		else:
			groups = myldaplib.search_posix_groups(conn)
			if not groups:
				exitError(conn, "No posixGroup objects found.")

			gidNumber = myldaplib.find_next_available_gid(groups)
			print(f"Next available GID: {gidNumber}")

		# If it's a PI, create new group in ldap
		# THIS BELOW CHANGES FOR NEW LDAP
		# member changed to memberUid & format is just netID
		if netID==piID:
			dn = "cn=sg-"+piID+",ou=Labs,ou=Groups,"+ldap_setup
			attributes = {
				'objectClass': ['top', 'posixGroup', 'groupOfNames'],
				'cn': "sg-"+piID,
				'gidNumber': gidNumber,
				'member':"uid="+netID+",ou=Users,"+ldap_setup
				}

			conn.add(dn, attributes=attributes)
			if conn.result['result'] == 0:
				print(f"Successfully created group sg-{piID}")
			else:
				exitError(conn, f"Failed to create group sg-{piID}: {conn.result['message']}")

		# Add new user in ldap
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
		if conn.result['result'] == 0:
			print(f"Successfully added user {netID}")
		else:
			exitError(conn, f"Failed to add user {netID}: {conn.result['message']}")

		# If it's not a PI, add user to the corresponding group
		# THIS BELOW CHANGES FOR NEW LDAP
		# member changed to memberUid & format is just the netID
		if netID!=piID:
			dn = "cn=sg-"+piID+",ou=Labs,ou=Groups,"+ldap_setup
			dic = {
				'member': [(ldap3.MODIFY_ADD, ["uid="+netID+",ou=Users,"+ldap_setup])]
				}

			conn.modify(dn, dic)
			if conn.result['result'] == 0:
				print(f"Successfully added user {netID} to sg-{piID} group")
			else:
				exitError(conn, f"Failed to add user {netID} to sg-{piID} group: {conn.result['message']}")

		# Add to department machine if they ask so
		if neuroDesktops:
			dn = "cn=sg-neurology-desktops,ou=Neurology,ou=Machines,ou=Groups,"+ldap_setup
			dic = {
				'member': [(ldap3.MODIFY_ADD, ["uid="+netID+",ou=Users,"+ldap_setup])]
				}

			conn.modify(dn, dic)
			if conn.result['result'] == 0:
				print(f"Successfully added user {netID} to Neurology Desktops")
			else:
				exitError(conn, f"Failed to add user {netID} to Neurology Desktops: {conn.result['message']}"        )
		
		if neuroSquiggles:
			dn = "cn=sg-neurology-squiggles,ou=Neurology,ou=Machines,ou=Groups,"+ldap_setup
			dic = {
				'member': [(ldap3.MODIFY_ADD, ["uid="+netID+",ou=Users,"+ldap_setup])]
				}

			conn.modify(dn, dic)
			if conn.result['result'] == 0:
				print(f"Successfully added user {netID} to Neurology Desktops")
			else:
				exitError(conn, f"Failed to add user {netID} to Neurology Desktops: {conn.result['message'        ]}"        )

		# Create directories and give permissions

		# Put user in SLURM scheduler

		# Set home directory quota

		# Test login

		# Send email

	# Check that here are no duplicates after all
	users = myldaplib.search_posix_users(conn)
	dupicate_uids = myldaplib.find_duplicate_uids(users)
	print(f"There are {len(dupicate_uids)} duplicate users")

	groups = myldaplib.search_posix_groups(conn)
	duplicate_gids = myldaplib.find_duplicate_gids(groups)
	print(f"There are {len(duplicate_gids)} duplicate groups")

	# Unbind and close the connection
	closeConn(conn)

if __name__ == "__main__":
	main()
