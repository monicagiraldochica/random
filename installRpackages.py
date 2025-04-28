import os

os.chdir("/scratch/g/rccadmin/mkeith/R")
v_new = "4.5.0"
v_old = "4.4.2"

# Get the list of missing packages
# Opening in write mode will empty it's previous content if file exist
fnew = open(v_new+".txt",'w')
for item in sorted(os.listdir("/hpc/apps/R/"+v_new+"/lib64/R/library/"), key=str.casefold):
	if not item.startswith("00LOCK"):
		_ = fnew.write(item+"\n")
fnew.close()

fold = open(v_old+".txt",'w')
for item in sorted(os.listdir("/hpc/apps/R/"+v_old+"/lib64/R/library/"), key=str.casefold):
        if not item.startswith("00LOCK"):
                _ = fold.write(item+"\n")
fold.close()

if os.path.exists("diff.txt"):
	 os.remove("diff.txt")
os.system("diff "+v_new+".txt "+v_old+".txt >> diff.txt")

# Create files to store the libraries that successfully & unsuccessfully installed
fout1 = open("sucess.txt",'w')
fout1.close()
fout2 = open("fail.txt",'w')
fout2.close()

# Install dependencies of some missing packages
print("Installing ggforce (dependency)...\n")
print("Rscript -e \"install.packages('ggforce')\"")
os.system("Rscript -e \"install.packages('ggforce')\"")

# Install missing packages
git_pkgs = {
	"SeuratData":"satijalab/seurat-data",
	"SeuratDisk":"mojaveazure/seurat-disk",
	"SeuratWrappers":"satijalab/seurat-wrappers",
	"CellChat":"jinworks/CellChat",
	"monocle3":"cole-trapnell-lab/monocle3",
	"presto":"immunogenomics/presto",
	"proteoDA":"ByrumLab/proteoDA",
	"rbokeh":"hafen/rbokeh",
	"SCENIC":"aertslab/SCENIC",
	"SCopeLoomR":"aertslab/SCopeLoomR",
	"velocyto.R":"velocyto-team/velocyto.R"
	}

fin = open("diff.txt","r")
for line in fin:
	line = line.replace("\n","").replace("> ","")
	if line.startswith("<") or line[0].isdigit() or line in git_pkgs.keys():
		continue

	fout1 = open("sucess.txt","r")
	fout2 = open("fail.txt","r")
	output1 = os.popen("cat sucess.txt | grep "+line+" | head -n 1").read().replace("\n","")
	output2 = os.popen("cat fail.txt | grep "+line+" | head -n 1").read().replace("\n","")
	fout2.close()
	fout1.close()
	if output1==line or output2==line:
		continue

	# Using the default install method
	print("Installing "+line+"...\n")
	print("Rscript -e \"install.packages('"+line+"')\"")
	os.system("Rscript -e \"install.packages('"+line+"')\"")

	if os.path.isdir("/hpc/apps/R/"+v_new+"/lib64/R/library/"+line+"/"):
		print("\nsucess\n")
		fout1 = open("sucess.txt","a")
		_ = fout1.write(line+"\n")
		fout1.close()
	else:
		# Using Bioconductor
		print("\nTrying with bioconductor...")
		print("Rscript -e \"BiocManager::install(c('"+line+"'))\"")
		os.system("Rscript -e \"BiocManager::install(c('"+line+"'))\"")
		
		if os.path.isdir("/hpc/apps/R/"+v_new+"/lib64/R/library/"+line+"/"):
			print("\nsucess\n")
			fout1 = open("sucess.txt","a")
			_ = fout1.write(line+"\n")
			fout1.close()
		else:
			print("\nfailure\n")
			fout2 = open("fail.txt","a")
			_ = fout2.write(line+"\n")
			fout2.close()
fin.close()

# Install Git packages
for pkg,repo in git_pkgs.items():
	print("\nInstalling "+pkg+"...")
	print("Rscript -e \"devtools::install_github('"+repo+"')\"")
	os.system("Rscript -e \"devtools::install_github('"+repo+"')\"")

	if os.path.isdir("/hpc/apps/R/"+v_new+"/lib64/R/library/"+line+"/"):
		print("\nsucess\n")
		fout1 = open("sucess.txt","a")
		_ = fout1.write(line+"\n")
		fout1.close()
	else:
		print("\nfailure\n")
		fout2 = open("fail.txt","a")
		_ = fout2.write(line+"\n")
		fout2.close()
	
