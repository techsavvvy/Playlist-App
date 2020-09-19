from app import ALLOWED_EXTENSIONS
import os

def is_valid_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def modify_file_name(filename, id):
    split_name=filename.rsplit('.', 1)
    return split_name[0]+'___'+id+'___.'+split_name[1]

def check_file_name_already_exist(filename, id):
    file_name=modify_file_name(filename,id)
    if os.path.exists('app/audio/'+file_name):
        return True
    return False
