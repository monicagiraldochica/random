import os

fin = open("R/diff.txt","r")
fout1 = open("R/sucess.txt","a+")
fout2 = open("R/fail.txt","a+")

for line in fin:
	line = line.replace("\n","").replace("> ","")
	output1 = os.popen("cat R/sucess.txt | grep "+line+" | head -n 1").read().replace("\n","")
	output2 = os.popen("cat R/fail.txt | grep "+line+" | head -n 1").read().replace("\n","")
	if output1==line or output2==line:
		continue

	print("Installing "+line+"...\n")
	print("Rscript -e \"install.packages('"+line+"')\"")
	try:
		os.system("Rscript -e \"install.packages('"+line+"')\"")
	except:
		print("exception")

	if os.path.isdir("/hpc/apps/R/4.5.0/lib64/R/library/"+line+"/"):
		print("\nsucess\n")
		fout1.write(line+"\n")
	else:
		print("\nfailure\n")
		fout2.write(line+"\n")
		
fout2.close()
fout1.close()
fin.close()
