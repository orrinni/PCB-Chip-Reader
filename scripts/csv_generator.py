import os
import cv2
import csv
import random
import shutil
from PIL import Image

def get_parent_dir(n=1):
    """ returns the n-th parent dicrectory of the current
    working directory """
    current_path = os.path.dirname(os.path.abspath(__file__))
    for k in range(n):
        current_path = os.path.dirname(current_path)
    return current_path

""" This function takes in a directory of images
and will save the size of each image into a csv
file. Name is the name of the final csv file."""
def create_csv(name):
    file_list = os.listdir(os.getcwd())
    file_list.remove('csv_generator.py')
    csv_file = open(name + ".csv", "w", newline='')
    csv_writer = csv.writer(csv_file, quotechar="'")
    csv_writer.writerow(['"image"', '"xmin"', '"ymin"', '"xmax"', '"ymax"', '"label"'])
    for fil in file_list:
        try:
            image = cv2.imread(os.getcwd() + "/" + fil, cv2.IMREAD_UNCHANGED)
            dim = image.shape
            fil2 = '"' + fil + '"'
            csv_writer.writerow([fil2, 0, 0, dim[1], dim[0]])
        except:
            x=1
    csv_file.close()
    
def list_to_csv(list1):
    images = get_parent_dir(1) + "/images"
    cwd = os.getcwd()
    os.chdir(images)
    
    csv_file = open("results.csv", "w", newline='')
    csv_writer = csv.writer(csv_file)
    
    while True:
        if len(list1) > 5:
            csv_writer.writerow(list1[0:5])
            list1 = list1[5:]
        else:
            csv_writer.writerow(list1)
            break
    
    csv_file.close()
    os.chdir(cwd)
        
        


"""Takes an image, dimensions in the form
[xmin, ymin, xmax, ymax], and a folder to be saved to.
Crops the iamge based on those dimensions and saves it 
as a .jpg file in that folder."""
def crop_image(image_path, dims, folder):
    image = Image.open(image_path)
    if image.mode != "RGB":
            image = image.convert("RGB")
    cropped = image.crop((dims[0], dims[1], dims[2], dims[3]))
    name = folder + "/" + str(random.randint(0,10000)) + ".jpg" 
    
    try:
        cropped.save(name)
    except:
        print(dims, image.size)

"""Deletes a directory and all of its contents."""
def del_directory(directory):
    try:
        shutil.rmtree(directory)
    except:
        print("Error ocurred while deleting directory: " + directory)

"""Returns a list of the strings from a list of BB's."""
def string_recognition(image_path, bb_list, input_labels):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    conf_inter = image.shape[0]/10
    center_list = []
    return_list = []
    
    for num in range(len(bb_list)):
        centerx = (bb_list[num][4] - bb_list[num][2])/2
        centery = (bb_list[num][5] - bb_list[num][3])/2
        center_list.append([centerx, centery, input_labels[bb_list[num][6]]])
    
    center_list.sort(key=lambda x: x[0])
    
    while center_list:
        first_bb = center_list.pop(0)
        word = first_bb[2][0]
        for center in center_list:
            if ((center[1] >= first_bb[1] - conf_inter) or \
            (center[1] <= first_bb[1] + conf_inter)) and \
            (center[2][1] == first_bb[2][1]):
                word += center[2][0]
                center_list.remove(center)
        return_list.append(word)
        
    return return_list





