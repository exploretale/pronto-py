# -*- coding: utf-8 -*-

import os
import constants
from flask import current_app as app
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def upload(image):
    if image and allowed_file(image.filename):
        # Make the filename safe, remove unsupported characters
        image_name = secure_filename(image.filename)
        # Move the file from the temporal folder to the upload folder we set up
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
        return constants.IMAGE_UPLOAD_DIR + image_name
