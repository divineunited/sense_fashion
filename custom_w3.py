import os, shutil

def wipe_folder(folder_path):
    for the_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, the_file)
        try:
            # checking if it is a file, then deleting it using os.unlink()
            if os.path.isfile(file_path):
                # NOTE: os.remove() and os.unlink() both work the same
                os.unlink(file_path) 
            # checking if it is a directory, then delete directory -- uncomoment if you want to use this
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)