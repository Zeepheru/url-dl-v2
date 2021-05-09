import os

def lol():
    for folder in os.listdir(r'I:\Backup\Random Videos'):
        folder

def delete_duplicate_mp4s(main_dir):
    for folder in os.listdir(main_dir):
        if ".png" not in folder and ".txt" not in folder:
            f_list = os.listdir(os.path.join(main_dir, folder))
            if ".webm" in str(f_list) and ".mp4" in str(f_list):
                for f in f_list:
                    if ".mp4" in f:
                        os.remove(os.path.join(main_dir, folder, f))
                        print("Removing: " + f)
            
delete_duplicate_mp4s(r'E:\TbRF\ForgaLorga')