import os


def mp4tomp3(file_path):
    print(file_path)
    # dest = os.path.basename(file_path)
    dest = os.path.dirname(file_path) + "\\" + (os.path.splitext(os.path.basename(file_path))[0] + ".mp3").replace("TEMP_", "")
    print(dest)
    os.system("ffmpeg -i \"" + file_path + "\" \"" + dest + "\"")