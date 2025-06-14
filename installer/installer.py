import os
import subprocess
import zipfile
import urllib.request

# Check if pip is installed
try:
    subprocess.run(["pip", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
except Exception:
    print("pip is not installed. Please install pip/python before running this script.")
    input("Press Enter to open store")
    subprocess.run("start https://apps.microsoft.com/detail/9pnrbtzxmb4z?hl=de-DE&gl=CH", shell=True)
    exit(1)

# Install libraries
subprocess.run("pip install tk", shell=True)
subprocess.run("pip install pillow", shell=True)
subprocess.run("pip install pygame", shell=True)
subprocess.run("pip install pydub", shell=True)
subprocess.run("pip install requests", shell=True)

# Install ffmpeg
ffmpeg_installed = False
try:
    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    ffmpeg_installed = True
except Exception:
    ffmpeg_installed = False
    
if not ffmpeg_installed:
    ans = input("FFmpeg is required but not installed. Do you want to install it? (y/n): ").strip().lower()
    if ans == "y" or ans == "yes":
        print("Installing FFmpeg...")
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        os.makedirs( os.path.join(os.path.expanduser("~"), "Documents"), exist_ok=True)
        open(os.path.join(os.path.expanduser("~"), "Documents", "ffmpeg.zip"), 'w').close()
        ffmpeg_zip_path = os.path.join(os.path.expanduser("~"), "Documents", "ffmpeg.zip")
        ffmpeg_extract_path = os.path.join(os.path.expanduser("~"), "ffmpeg")

        # Download ffmpeg zip
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip_path)

        # Extract ffmpeg zip
        with zipfile.ZipFile(ffmpeg_zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_extract_path)

        # Find the extracted ffmpeg bin directory
        ffmpeg_dirs = [d for d in os.listdir(ffmpeg_extract_path) if os.path.isdir(os.path.join(ffmpeg_extract_path, d))]
        if ffmpeg_dirs:
            ffmpeg_bin = os.path.join(ffmpeg_extract_path, ffmpeg_dirs[0], "bin")
            os.environ["PATH"] += os.pathsep + ffmpeg_bin

        # Remove ffmpeg zip after extraction
        os.remove(ffmpeg_zip_path)

# Download project files

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