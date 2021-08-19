import glob
from config import*


for file in glob.glob(home_dir+"/secure/keys/private/*"):
    print(file)