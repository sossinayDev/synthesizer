import os
import subprocess
import zipfile
import urllib.request

# Install libraries
subprocess.run("pip install tk", shell=True)
subprocess.run("pip install pillow", shell=True)
subprocess.run("pip install pygame", shell=True)
subprocess.run("pip install pydub", shell=True)

url = "https://pixelnet.xn--ocaa-iqa.ch/static/project_data/synthesizer.zip"
zip_path = "synthesizer.zip"

urllib.request.urlretrieve(url, zip_path)

# Extract zip file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    for member in zip_ref.namelist():
        if member.startswith("synthesizer/"):
            target_path = member[len("synthesizer/"):]
            if target_path:
                zip_ref.extract(member, ".")
                os.rename(os.path.join(".", member), os.path.join(".", target_path))

# Remove the zip file after extraction
os.remove(zip_path)

# Create additional folders
dirs = [
    "patterns",
    "collections"
]
for dir in dirs:
    os.makedirs(dir, exist_ok=True)

# Run the synthesizer
subprocess.run("python main.py")