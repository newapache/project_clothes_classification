from subprocess import check_output
from os import listdir
import sys
from os.path import isfile, join


images = [f for f in listdir("20191026_07") if isfile(join("20191026_07", f))]
for img in images:
	img_path = "20191026_07/"+str(img)
	out = check_output(["python","label_image.py",img_path])
	temp_cloth = out.decode('utf-8').split(":")[0]
	predict_score = out.decode('utf-8').split(":")[2].split()[0]
	#print(temp_cloth, predict_score)
	if float(predict_score) >= 60.0 :
		print(temp_cloth)
	else:
		continue

