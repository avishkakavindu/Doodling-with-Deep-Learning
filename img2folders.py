import shutil
import os
import pandas as pd

# def save_img(name):
#     the_dir = "D:\doodle images\{}".format(name.split('_')[0])
#     file_name = "D:\doodle images\{}.png".format(name)
#     if os.path.isdir(the_dir):
#         try:
#             shutil.move(file_name, the_dir)
#         except:
#             pass
#     else:
#         os.mkdir(the_dir)
#         shutil.move(file_name, the_dir)

train_dir = 'dataset/'

# # how many rows from each csv?
# get_n = 1

# for file in os.listdir(train_dir):
#     try:
#         train = pd.read_csv(train_dir + file, index_col='key_id')
#     except:
#         continue
#     print('Currently Saving: {}'.format(str(file)))
    
#     for i in range(train.shape[0]):
#         label = '{}_{}'.format(train['word'].iloc[0], i)
#         save_img(label)

for file in os.listdir(train_dir):
    try:
        train = pd.read_csv(train_dir + file, index_col='key_id')
    except:
        continue
    print('Currently Saving: {}'.format(str(file)))
    
    label = '{}'.format(train['word'].iloc[0])
    
    the_dir = "D:\doo"
    file_name = "D:\doodle images\{}".format(label)

    shutil.move(file_name, the_dir)
