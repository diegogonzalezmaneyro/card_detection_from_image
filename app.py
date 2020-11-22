# app.py
import numpy as np

from flask import Flask
from flask_restful import Api, Resource, reqparse

from dni_detection import dni_from_image


APP = Flask(__name__)
API = Api(APP)

class Predict(Resource):

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('imageData')

        args = parser.parse_args()  # creates dict
        # output_string = detect_dni_from_image(args.image_dir)
        base64_imageData = args.imageData
        base64_cropImage = dni_from_image(base64_imageData)

        out = {'dni_image': base64_cropImage}

        return out, 200


API.add_resource(Predict, '/crop')

if __name__ == '__main__':
    APP.run(debug=True, port='1080')