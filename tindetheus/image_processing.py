# MIT License
#
# Copyright (c) 2019 Charles Jekel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import os
import shutil
import ssl

import matplotlib.pyplot as plt
import imageio

from tindetheus.facenet_clone.facenet import to_rgb

# Python 2 vs Python 3 stuff...
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

try:
    from urllib.request import urlretrieve, urlopen
    import urllib.request
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl._create_unverified_context()
    urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context)))
except ImportError:
    from urllib import urlretrieve


def clean_temp_images():
    # delete the temp_images dir
    shutil.rmtree('temp_images')
    os.makedirs('temp_images')


def clean_temp_images_aligned():
    # delete the temp images aligned dir
    if os.path.exists('temp_images_aligned'):
        shutil.rmtree('temp_images_aligned', ignore_errors=True)


def download_url_photos(urls, userID, is_temp=False):
    # define a function which downloads the pictures of urls
    import urllib.request
    count = 0
    image_list = []
    if is_temp is True:
        os.makedirs('temp_images/temp')

    # Create SSL context that doesn't verify certificates for macOS
    ssl_context = ssl._create_unverified_context()

    for url in urls:
        if is_temp is True:
            image_list.append('temp_images/temp/'+userID+'.'+str(count)+'.jpg')
        else:
            image_list.append('temp_images/'+userID+'.'+str(count)+'.jpg')

        # Download with SSL context
        try:
            with urllib.request.urlopen(url, context=ssl_context) as response:
                with open(image_list[-1], 'wb') as out_file:
                    out_file.write(response.read())
        except Exception as e:
            print(f"Warning: Could not download image {count} for user {userID}: {e}")

        count += 1
    return image_list


def move_images_temp(image_list, userID):
    # move images from temp folder to al_database
    count = 0
    database_loc = []
    for i, j in enumerate(image_list):
        new_fname = 'al_database/'+userID+'.'+str(count)+'.jpg'
        try:
            os.rename(j, new_fname)
        except Exception as ex:
            print(ex)
            print('WARNING: unable to save file, it may already exist!',
                  'file: ' + new_fname)
        database_loc.append(new_fname)
        count += 1
    return database_loc


def move_images(image_list, userID, didILike):
    # move images from temp folder to database
    if didILike == 'Like':
        fname = 'like/'
    else:
        fname = 'dislike/'
    count = 0
    database_loc = []
    for i, j in enumerate(image_list):
        new_fname = 'database/'+fname+userID+'.'+str(count)+'.jpg'
        try:
            os.rename(j, new_fname)
        except Exception as ex:
            print(ex)
            print('WARNING: unable to save file, it may already exist!',
                  'file: ' + new_fname)
        database_loc.append(new_fname)
        count += 1
    return database_loc


def al_copy_images(image_list, userID, didILike, database_str='al/'):
    # move images from temp folder to database
    if didILike == 'Like':
        fname = 'like/'
    else:
        fname = 'dislike/'
    count = 0
    database_loc = []
    for i, j in enumerate(image_list):
        new_fname = database_str+fname+userID+'.'+str(count)+'.jpg'

        shutil.copyfile(j, new_fname)

        count += 1
    return database_loc


def show_images(images, holdon=False, title=None, nmax=49):
    # use matplotlib to display profile images
    n = len(images)
    if n > nmax:
        n = nmax
        n_col = 7
    else:
        n_col = 3
    if n % n_col == 0:
        n_row = n // n_col
    else:
        n_row = n // 3 + 1

    # Create a reasonable figure size (width, height in inches)
    # Smaller size to leave room for terminal
    figsize = (n_col * 3, n_row * 3)

    if title is None:
        fig = plt.figure(figsize=figsize)
    else:
        fig = plt.figure(title, figsize=figsize)

    # Position window on left half of screen (macOS compatible)
    try:
        manager = plt.get_current_fig_manager()
        # Use matplotlib's backend to position the window
        # Position at (0, 0) which is top-left, and let the OS handle sizing
        if hasattr(manager, 'window'):
            # For TkAgg backend on macOS
            try:
                # Get the window and position it
                manager.window.wm_geometry("+0+0")
            except:
                pass
    except:
        pass  # Fallback if positioning fails

    plt.tight_layout()
    for j, i in enumerate(images):
        if j == nmax:
            print('\n\nToo many images to show... \n\n')
            break
        temp_image = imageio.imread(i)
        if len(temp_image.shape) < 3:
            # needs to be converted to rgb
            temp_image = to_rgb(temp_image)
        plt.subplot(n_row, n_col, j+1)
        plt.imshow(temp_image)
        plt.axis('off')
        plt.subplots_adjust(wspace=0, hspace=0)

    if holdon is False:
        plt.show(block=False)
        plt.pause(0.1)
