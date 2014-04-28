# -*- coding: utf-8 -*-
#  StreetSign Digital Signage Project
#     (C) Copyright 2013 Daniel Fairhead
#
#    StreetSign is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    StreetSign is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.
#
"""
----------------------------------
streetsign_server.post_types.image
----------------------------------

uploaded image post type.

"""


from flask import render_template_string, request, g, flash
from werkzeug import secure_filename # pylint: disable=no-name-in-module
from os.path import splitext, join as pathjoin, isdir, abspath
from subprocess import check_call
from os import makedirs

from streetsign_server.post_types import my

########################################################################
#
# Helper functions:
#

def run_local_script(scriptname, *vargs):
    ''' run an image.<scriptname> script, with <*vargs> '''
    return check_call([splitext(abspath(__file__))[0] + scriptname] + list(vargs))

def resize_image(filename):
    ''' try to resize an image in place on the system. if fail,
        just flash a message, don't actually freak out '''
    try:
        run_local_script('.makesmall.sh', filename)
        flash('image imported and resized')
    except:
        flash('tried to resize... oh well.')

def image_path():
    ''' return the path to save images to, creating the folder if
        it doesn't exist. '''
    where = pathjoin(g.site_vars['user_dir'], 'post_images')

    if not isdir(where):
        makedirs(where)

    return where

def allow_filetype(filename):
    ''' what kinds of files are allowed? '''

    return splitext(filename)[-1].lower() in \
        ['.png','.jpg','.jpeg','.gif','.bmp','.svg']


########################################################################
#
# Now the actual post_type required functions:
#

def form(data):
    ''' return the html form for editing an image post '''
    # pylint: disable=star-args
    return render_template_string(my('.form.html'), **data)

def receive(data):
    ''' revieve the form data, including the uploaded file, and put it
        where it should be, and return all the image data we need. '''

    if 'upload' in data:
        # An image has been uploaded

        f = request.files['image_file']
        if f and allow_filetype(f.filename):
            filename = secure_filename(f.filename)
            # TODO: check for '' returned from secure_filename???

            full_path = pathjoin(image_path(), filename)
            f.save(full_path)
            resize_image(full_path)

        else:
            raise IOError('Invalid file. Sorry')
    elif 'url' in data:
        # Download an image file from an external URL.

        filename = secure_filename(data['url'])
        if filename and allow_filetype(filename):
            full_path = pathjoin(image_path(), filename)

            #try:
            if True:
                print data['url']
                run_local_script('.getexternalimage.sh',
                                 data['url'],
                                 full_path)
                flash('image Downloaded')
            #except :
            #    flash('tried to download image. Failed')
            #    raise IOError('Unable to download image! (%s)' % full_path)

            resize_image(full_path)
        else:
            raise IOError('Invalid file (%s). Sorry.' % data['url'])

    else:
        filename = data.get('filename')
        if filename and allow_filetype(filename):
            filename = secure_filename(filename)
        else:
            raise Exception('Tried to change the file, huh? Not happening')
            # TODO

    return {'content': filename,
            'filename': filename,
            'file_url': g.site_vars['user_url']+'/post_images/'+filename}

def display(data):
    ''' display the html to display the posted image. '''
    return ('<img class="post_image" src="{0}"'
           ' style="width:100%;height:auto" />'.format(data['file_url']))

def screen_js():
    ''' return the javascript for displaying these images correctly '''
    return my('.screen.js')
