import os
from binascii import a2b_base64
from rodan.settings import MEDIA_URL, MEDIA_ROOT
from rodan.jobs.base import RodanTask
from django.conf import settings
import json
import numpy as np
import cv2 as cv
import zipfile
import logging
logger = logging.getLogger('rodan')


def media_file_path_to_public_url(media_file_path):
    chars_to_remove = len(MEDIA_ROOT)
    return os.path.join(MEDIA_URL, media_file_path[chars_to_remove:])


def get_iiif_query(resource_path):
    resource_path = resource_path.split('/')
    resource_path.remove('')
    resource_path.remove('rodan')
    resource_path.remove('data')
    del resource_path[-1]  # last element is the original uncoverted file
    resource_path.append('diva')
    resource_path.append('image.jp2')
    resource_path = '%2F'.join(resource_path)

    server_url = settings.IIPSRV_URL
    query = server_url + '?IIIF=' + resource_path

    return query


def get_image_dimensions(resource_path):
    """
    returns the image dimensions in the following format [height, width]
    """
    resource_path = resource_path.split('/')
    del resource_path[-1]   # last element is the original uncoverted file
    resource_path.append('diva')
    resource_path.append('measurement.json')
    resource_path = '/'.join(resource_path)

    data = json.load(open(resource_path))
    return [data['dims']['max_h'][-1], data['dims']['max_w'][-1]]


def get_images(resource_path):
    query_url = get_iiif_query(resource_path)
    height, width = get_image_dimensions(resource_path)
    return [
            {
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "resource": {
                    "@id": query_url,
                    "@type": "dctypes:Image",
                    "format": "image/jpeg",
                    "height":height,
                    "width":width,
                    "service": {
                        "@context": "http://iiif.io/api/image/2/context.json", "@id": query_url, "profile": "http://iiif.io/api/image/2/level2.json"
                        }
                    },
                "on": "https://images.simssa.ca/iiif/manuscripts/cdn-hsmu-m2149l4/canvas/folio-001r.json"
                }
            ]


def create_canvases(resource_path):
    height, width = get_image_dimensions(resource_path)
    data = {}
    data['@id'] = 'https://images.simssa.ca/iiif/manuscripts/cdn-hsmu-m2149l4/canvas/folio-001r.json'
    data['@type'] = 'sc:Canvas'
    data['label'] = 'Folio 001r'
    data['height'] = height
    data['width'] = width
    data['images'] = get_images(resource_path)
    return [data]


def create_sequences(resource_path):
    data = {}
    data['@type'] = 'sc:Sequence'
    data['canvases'] = create_canvases(resource_path)
    return [data]


def create_metadata(resource_path):
    return [
            {"label": "Date", "value": "1554-5"},
            {"label": "Siglum", "value": "CDN-Hsmu M2149.L4"},
            {"label": "Provenance", "value": "Salzinnes"}
            ]


def create_json(resource_path):
    data = {}
    data['@context'] = 'http://iiif.io/api/presentation/2/context.json'
    data['@id'] = 'https://images.simssa.ca/iiif/manuscripts/cdn-hsmu-m2149l4/manifest.json'
    data['@type'] = 'sc:Manifest'
    data['label'] = 'Salzinnes, CDN-Hsmu M2149.L4'
    data['metadata'] = create_metadata(resource_path)
    data['description'] = 'Image'
    data['sequences'] = create_sequences(resource_path)
    return json.dumps(data)


class PixelInteractive(RodanTask):
    name = 'Pixel_js'
    author = 'Zeyad Saleh, Ke Zhang & Andrew Hankinson'
    description = 'Pixel-level ground truth creation and correction'
    settings = {
            'title': 'Options',
            'type': 'object',
            'properties': {
                'Output Mask': {
                    'type': 'boolean',
                    'default': False
                },
                # 'Crop Image': {
                #     'type': 'boolean',
                #     'default': True
                # },
            },
            'job_queue': 'Python3',
    }
    enabled = True
    category = 'Diva - Pixel.js'
    interactive = True
    input_port_types = [
            {
                'name': 'Image',
                'resource_types': lambda mime: mime.startswith('image/'),
                'minimum': 1,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 1 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 2 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 3 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 4 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 5 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 6 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                    'name': 'PNG - Layer 7 Input',
                    'resource_types': ['image/rgba+png'],
                    'minimum': 0,
                    'maximum': 1,
                    'is_list': False
                    },
            ]
    output_port_types = [
        # {'name': 'Text output', 'minimum': 1, 'maximum': 1, 'resource_types': ['text/plain']},
        {
            'name': 'ZIP',
            'resource_types': ['application/zip'],
            'minimum': 1,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'PNG - Layer 1 Output',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'PNG - Layer 2 Output',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'PNG - Layer 3 Output',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'PNG - Layer 4 Output',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'PNG - Layer 5 Output',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'PNG - Layer 6 Output',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'PNG - Layer 7 Output',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'Background',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'Region',
            'resource_types': ['image/rgba+png'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        }
    ]

    def get_my_interface(self, inputs, settings):
        # Get input.
        layer_urls = []

        query_url = get_iiif_query(inputs['Image'][0]['resource_path'])

        for i in range(1, 8):
            if 'PNG - Layer {} Input'.format(i) in inputs:
                layer_path = inputs['PNG - Layer {} Input'.format(i)][0]['resource_path']
                layer_urls.append(media_file_path_to_public_url(layer_path))

        # Create data to pass.
        data = {
                'json': create_json(inputs['Image'][0]['resource_path']),
                'layer_urls': layer_urls,
                }
        return ('index.html', data)

    def run_my_task(self, inputs, settings, outputs):
        def remove_bg(array):
            # Create mask for alpha channel
            layer_image = cv.imdecode(array, cv.IMREAD_GRAYSCALE)
            _, alpha = cv.threshold(layer_image, 1, 255, cv.THRESH_BINARY)
            alpha = alpha == 255
            # Set background to black (reduce size) and then make transparent
            result = background*(alpha[:,:,np.newaxis])

            return result

        def convert(img):
            data = img.split(',')[1]    # Remove header from the base 64 string
            missing_padding = len(data) % 4
            if missing_padding != 0:
                data += '=' * (4 - missing_padding % 4)
            binary_data = a2b_base64(data)   # Parse base 64 image data
            array = np.fromstring(binary_data, np.uint8)

            return array

        if '@done' not in settings:
            return self.WAITING_FOR_INPUT()

        # list = settings['@user_input']    # List passed having the image data (base 64) from all layer
        background = cv.imread(inputs['Image'][0]['resource_path'], cv.IMREAD_UNCHANGED)
        background = cv.cvtColor(background, cv.COLOR_BGR2BGRA)
        output_list=settings['@user_input']    # List passed having the image data (base 64) from all layer
        # Select Region
        select_region_array = convert(output_list[len(output_list)-1])
        select_region = remove_bg(select_region_array)
        _,_,_,a = cv.split(select_region)
        x,y,w,h = cv.boundingRect(a)
        # Output path
        outfile_path = outputs["ZIP"][0]['resource_path'] + ".zip"

        with zipfile.ZipFile(outfile_path, 'w') as zipMe:        
            for i in range(len(output_list)):
                # change to bytes 
                array = convert(output_list[i])

                if settings['Output Mask']:
                    tmp = cv.imdecode(array, cv.IMREAD_UNCHANGED)
                    retval, buf = cv.imencode('.png', tmp)
                else:
                    result = remove_bg(array)
                    # if settings['Crop Image']:
                    #     result = result[y:y+h, x:x+w]
                    retval, buf = cv.imencode('.png', result)      

                if i == 0:
                    zipMe.writestr(('rgba PNG - Layer 0 (Background).png'), buf)
                    # Write to output
                    if "Background" in outputs.keys():
                        encoded_data = buf.tobytes()
                        output_file_path = outputs["Background"][0]['resource_path']
                        with open(output_file_path, 'wb') as f:
                            f.write(encoded_data)
                        logger.info(f"Write to Background : {outputs.keys()}")
                        
                elif i == len(output_list) - 1:
                    # if settings['Crop Image']:
                    #     break
                    zipMe.writestr(('rgba PNG - Selected regions.png'), buf)
                    if "Region" in outputs.keys():
                        #os.rename('rgba PNG - Selected regions.png', outputs["Region"][0]['resource_path'])
                        encoded_data = buf.tobytes()
                        output_file_path = outputs["Region"][0]['resource_path']
                        with open(output_file_path, 'wb') as f:
                            f.write(encoded_data)
                        logger.info(f"Write to Region : {outputs.keys()}")
                else:
                    zipMe.writestr(('rgba PNG - Layer {0}.png').format(i), buf)
                    prefix = 'rgba PNG - Layer {0}'.format(i)
                    #'name': 'PNG - Layer 7 Output',
                    qkey = "PNG - Layer {} Output".format(i)
                    if qkey in outputs.keys():
                        #os.rename('{}.png'.format(prefix), outputs["{} Output".format(prefix)][0]['resource_path'])
                        encoded_data = buf.tobytes()
                        output_file_path = outputs[qkey][0]['resource_path']
                        with open(output_file_path, 'wb') as f:
                            f.write(encoded_data)
                        logger.info(f"Write to {qkey} : {outputs.keys()}")

            # if settings['Crop Image']:
            #     background = background[y:y+h, x:x+w]
            retval, buf = cv.imencode('.png', background)
            zipMe.writestr(('Image.png'), buf)

        # add the files to the zip file
        os.rename(outfile_path,outputs["ZIP"][0]['resource_path'])
        logger.info("Write to zip and return True")
        return True

    def validate_my_user_input(self, inputs, settings, user_input):
        return { '@done': True, '@user_input': user_input['user_input'] }

    def my_error_information(self, exc, traceback):
	    pass
