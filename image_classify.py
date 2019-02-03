import sys
import numpy as np
from keras.preprocessing import image
from keras.models import Model
from keras.applications import imagenet_utils, mobilenet



# process an image to be mobilenet friendly
def process_image(img_path):
	img = image.load_img(img_path, target_size=(224, 224))
	img_array = image.img_to_array(img)
	img_array = np.expand_dims(img_array, axis=0)
	pImg = mobilenet.preprocess_input(img_array)
	return pImg

THRESHOLD = 0.1

def classify_image(test_img_path):
	# define the mobilenet model
	mobilenet_model = mobilenet.MobileNet()

	# process the test image
	pImg = process_image(test_img_path)

	# make predictions on test image using mobilenet
	prediction = mobilenet_model.predict(pImg)

	# obtain the top-5 predictions
	results = imagenet_utils.decode_predictions(prediction)
	print('classification results',[(clz, score) for _, clz, score in results[0]])

	return [clz for _, clz, score in results[0][0:3] if score > THRESHOLD]
