import os

fin = open("R/diff.txt","r")
for line in fin:
	line = line.replace("\n","").replace("> ","")
	fout1 = open("R/sucess.txt","r")
	fout2 = open("R/fail.txt","r")
	output1 = os.popen("cat R/sucess.txt | grep "+line+" | head -n 1").read().replace("\n","")
	output2 = os.popen("cat R/fail.txt | grep "+line+" | head -n 1").read().replace("\n","")
	fout2.close()
	fout1.close()
	if output1==line or output2==line:
		continue

	print("Installing "+line+"...\n")
	print("Rscript -e \"install.packages('"+line+"')\"")
	os.system("Rscript -e \"install.packages('"+line+"')\"")

	if os.path.isdir("/hpc/apps/R/4.5.0/lib64/R/library/"+line+"/"):
		print("\nsucess\n")
		fout1 = open("R/sucess.txt","a")
		fout1.write(line+"\n")
		fout1.close()
	else:
		print("\nTrying with bioconductor...")
		print("Rscript -e \"BiocManager::install(c('"+line+"'))\"")
		os.system("Rscript -e \"BiocManager::install(c('"+line+"'))\"")
		
		if os.path.isdir("/hpc/apps/R/4.5.0/lib64/R/library/"+line+"/"):
			print("\nsucess\n")
			fout1 = open("R/sucess.txt","a")
			fout1.write(line+"\n")
			fout1.close()
		else:
			print("\nfailure\n")
			fout2 = open("R/fail.txt","a")
			fout2.write(line+"\n")
			fout2.close()
fin.close()
