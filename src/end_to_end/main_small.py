import os
import glob
from tqdm import tqdm 
import librosa
import numpy as np
from string import ascii_lowercase
from pydub import AudioSegment # need ffmpeg installed as well (can be tricky on windows)

import matplotlib.pyplot as plt
# BEFORE TF IMPORT
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import tensorflow_io as tfio
from tensorflow.keras.layers.experimental import preprocessing
from tensorflow.keras import layers
from tensorflow.keras import models
from pathlib import Path
AUTOTUNE = tf.data.experimental.AUTOTUNE

	
import sys
# # Add to Model init:

# # Verify that the GPU is operational, if not use CPU
# 	if not gpu_tool.check_if_gpu_available(self.tf_device):
# 		self.tf_device = '/cpu:0'
# 	logging.info('Using this device for main computations: %s', self.tf_device)




def create_per_file_transcripts(filename):
	base_file_path = os.path.dirname(filename)
	print(f'base_file_path: {base_file_path}')
	with open(filename, 'r') as fd:
		lines = fd.readlines()
		for line in lines:
			toks = line.split(' ')
			transcript_file_name = base_file_path + '/' + toks[0] + '_indiv.txt'

			with open(transcript_file_name, 'w') as of:
				trans = " ".join([t.lower() for t in toks[1:]])
				of.write(trans)
				of.write('\n')




def gen_transcripts(data_path):
	data_dir = data_path + "/*/*/*.trans.txt"

	transcripts = glob.glob(data_dir)

	print(transcripts)
	print("Converting %d aggregate transcripts into individual transcripts" % (len(transcripts)))
	for filename in tqdm(transcripts):			# only 2 files
		print(f'RNN Tutorial Processing Dataset Transcript File: {filename}')
		create_per_file_transcripts(filename)



		# REMOVING OLD FILES? OR JUST PLACE THE PROCESSED ONES IN A NEW DIR
		# for filePath in transcripts:
		# 	try:
		# 		os.remove(filePath)
		# 	except OSError:
		# 		print("Error while deleting file")
	 


def pathlib_flac2wav(filename):
	file_path = Path(filename)
	# print(f'file_path.suffix: {file_path.suffix}')
	# print(f'file_path.suffix[1:]: {file_path.suffix[1:]}')
	# print(f'str(file_path), file_path.suffix[1:]: {str(file_path), file_path.suffix[1:]}')
	flac_tmp_audio_data = AudioSegment.from_file(file_path, file_path.suffix[1:])
	flac_tmp_audio_data.export(file_path.with_suffix(".wav"))





def gen_wavs(data_path):
	data_dir = data_path + "/*/*/*.flac"
	audio_files = glob.glob(data_dir)

	print("Converting %d aggregate audio_files into individual audio_files" % (len(audio_files)))
	for filename in tqdm(audio_files):			# only 2 files
		print(f'RNN Tutorial Processing Dataset FlacToWav File: {filename}')
		pathlib_flac2wav(filename)










#	******************ABOVE IS ONLY ONCE AND BEFORE TRAINING************************************









###################################################
def my_pad_waveform(waveform, sample_rate=16000, max_length=30):

	print(f'tf.shape(waveform): {tf.shape(waveform)}')
	# Padding for files with less than (max_length * sample_rate) samples
	max_samples = max_length * sample_rate	# maybe tf.product
	print(f'max_samples: {max_samples}')
	# samples_to_pad = max(max_samples - waveform.size, 0)
	samples_to_pad = tf.math.maximum(tf.math.subtract(tf.constant(max_samples), tf.shape(waveform)), 0)	# maybe tf.subtract
	# samples_to_pad = tf.math.maximum(tf.math.subtract(max_samples, tf.size(waveform)), 0)	# maybe tf.subtract
	print(f'samples_to_pad: {samples_to_pad}')
	# print(f'samples_to_pad.numpy(): {samples_to_pad.numpy()}')
	paddings = tf.constant([[0, samples_to_pad]])
	padded = tf.pad(waveform, paddings)

	return padded
	
def tf_pad_waveform(waveform, sample_rate=16000, max_length=1):

	print(f'tf.shape(waveform): {tf.shape(waveform)}')

	# Padding for files with less than (max_length * sample_rate) samples
	max_samples = max_length * sample_rate
	# Padding for files with less than sample_rate samples
	zero_padding = tf.zeros([sample_rate] - tf.shape(waveform), dtype=tf.float32)
	print(f'max_samples: {max_samples}')
	print(f'zero_padding: {zero_padding}')
	# Concatenate audio with padding so that all audio clips will be of the 
	# same length
	waveform = tf.cast(waveform, tf.float32)
	# print(f'waveform: {waveform}')
	equal_length = tf.concat([waveform, zero_padding], 0)

	return equal_length



def get_spectrogram(waveform):
	print('\n*********\nget_spectrogram')
	# print(f'waveform: {waveform}')

	

	# equal_length = tf_pad_waveform(waveform)
	# equal_length = my_pad_waveform(waveform)
	print(f'tf.rank(waveform): {tf.rank(waveform)}')
	equal_length = tf.cast(waveform, tf.float32)	# no padding

	# print(f'waveform: {waveform}')
	print(f'tf.rank(waveform): {tf.rank(waveform)}')
	spectrogram = tf.signal.stft(equal_length, frame_length=255, frame_step=128)

	spectrogram = tf.abs(spectrogram)

	return spectrogram


# @tf.function
def get_spectrogram_and_label_outer(waveform, label):
	print('\n*********\nget_spectrogram_and_label_outer')
	print('\n*********\nwaveform')
	# print(f'waveform: {waveform}')
	tensor = tf.range(10)
	tf.print(tensor, output_stream=sys.stderr)
	tf.print(waveform, output_stream=sys.stderr)
	spectrogram = get_spectrogram(waveform)
	spectrogram = tf.expand_dims(spectrogram, -1)





	print('\n*********\nlabel')
	tensor = tf.range(10)
	tf.print(tensor, output_stream=sys.stderr)
	print(f'label: {label}')
	tf.print(label, output_stream=sys.stderr)
	print(f'char2idx: {char2idx}')
	# print(f'outside session waveform.eval(): {waveform.eval()}')
	# print(f'outside session label.eval(): {label.eval()}')
	# with tf.compat.v1.Session() as sess:  
	# 	print(f'inside sessionwaveform.eval(): {waveform.eval()}')
	# 	print(f'inside sessionlabel.eval(): {label.eval()}')
	
	
	tf.compat.v1.enable_eager_execution()

	print(f'tf.executing_eagerly(): {tf.executing_eagerly()}')
	
	
	tf.compat.v1.enable_eager_execution()
	# tf.compat.v1.disable_eager_execution()
	num = label.numpy().decode('utf-8')
	print(num)
	# string = tf.strings.as_string(label)
	# print(f'\n\n\n\n\n\n**********************\nstring: {string}')
	# label_id = np.array([char2idx[c] for c in string])

	label_id = np.array([char2idx[c] for c in num])			# convert each transcript to label indecies for each character
	print(label_id)

	# label_id = tf.argmax(label == alphabet)				## [alphabet.index(char) for char in transcript]
	
	# spectrogram = tf.expand_dims(spectrogram, 0)
	return (spectrogram, label_id)
	# return tf.data.Dataset.from_tensor_slices((spectrogram, label_id))





@tf.function
def f():
    tensor = tf.range(10)
    tf.print(tensor, output_stream=sys.stderr)
    return tensor

##########################################
def decode_audio(audio_binary_tensor):
	print('\n*********\ndecode_audio')
	# none of these work properly 
	# audio, _ = tfio.audio.AudioIOTensor(audio_binary_tensor)
	# audio, _ = tfio.audio.decode_flac(audio_binary_tensor)
	# audio, _ = tf.audio.decode_wav(audio_binary_tensor)
	sample_rate = 16000
	max_length = 30
	max_samples = sample_rate * max_length
	audio, _ = tf.audio.decode_wav(audio_binary_tensor, desired_samples=max_samples)	# PAD/TRIM ALL AUDIO FILES to 30 seconds at 16kHz
	print(f'audio.shape: {audio.shape}')
	
	audio_sq = tf.squeeze(audio, axis=-1)
	# print(f'tf.rank(audio): {tf.rank(audio)}')
	# print(f'tf.rank(audio_sq): {tf.rank(audio_sq)}')
	# print(f'audio.shape: {audio.shape}')
	# print(f'audio_sq: {audio_sq}')
	
	return audio_sq	


print("Using TensorFlow version %s" % tf.__version__)
@tf.function
def get_waveform_and_label(audio_path, transcript_path):
	# label = get_label(file_path)
	
	tensor = tf.range(10)
	tf.print(tensor, output_stream=sys.stderr)

	print(f'audio_path: {audio_path}')
	tf.print(audio_path, output_stream=sys.stderr)
	tf.print(audio_path, output_stream=sys.stdout)
	
	print(f'transcript_path: {transcript_path}')

	audio_binary_tensor = tf.io.read_file(audio_path)

	waveform = decode_audio(audio_binary_tensor)
	
	label = tf.io.read_file(transcript_path)
	# return audio_binary_tensor, label
	return (waveform, label)

def preprocess_dataset(files):
	
	# print(f'files: {files.element_spec}')
	# print('\n\ncombined map:')
	combined_ds = files.map(get_waveform_and_label, num_parallel_calls=AUTOTUNE)	# reads files into binary and transcript text

	combined_ds = combined_ds.map(lambda x, y: tf.py_function(get_spectrogram_and_label_outer, [x, y], (tf.float32, tf.int32)), num_parallel_calls=AUTOTUNE)	# generates spectrogram and label indecies
	# combined_ds = combined_ds.map(lambda wave, label: (get_spectrogram_outer(wave), get_label_outer(label)), num_parallel_calls=AUTOTUNE)
	
	# spectrogram_ds = spectrogram_files_ds.map(get_spectrogram_outer, num_parallel_calls=AUTOTUNE)
	# label_ds = label_files_ds.map(get_label_outer, num_parallel_calls=AUTOTUNE)
	return combined_ds

def get_dataset(data_dir):

	
	data_path = Path(data_dir)
	if not data_path.exists():
		raise Exception("The data path was not configured properly")

	# waveform_ds = tf.data.Dataset.list_files(str(data_path/'*.flac'))
	if len(glob.glob(str(data_path/'*.wav'))) != len(glob.glob(str(data_path/'*.flac'))):
		# print(f'generate wav from flac because are not equal to flac\'s currently')
		gen_wavs(data_dir)

	waveform_ds = tf.data.Dataset.list_files(str(data_path/'*.wav'))

	# transcript_ds = tf.data.Dataset.list_files(str(data_path/'*_indiv.txt'))
	if len(glob.glob(str(data_path/'*_indiv.txt'))) != len(waveform_ds):
		# print(f'generate individual transcripts because are not equal to wav\'s currently')
		gen_transcripts(data_dir)
	transcript_ds = tf.data.Dataset.list_files(str(data_path/'*_indiv.txt'))
	return tf.data.Dataset.zip((waveform_ds, transcript_ds))





####################
def plot_spectrogram(spectrogram, ax):
	# Convert to frequencies to log scale and transpose so that the time is
	# represented in the x-axis (columns).
	log_spec = np.log(spectrogram.T)
	print(f'log_spec: {log_spec}')
	height = log_spec.shape[0]
	X = np.arange(30*16000, step=height + 1)
	Y = range(height)
	ax.pcolormesh(X, Y, log_spec)

def display_spec_in_dataset(dataset):

	rows = 3
	cols = 3
	n = rows*cols
	fig, axes = plt.subplots(rows, cols, figsize=(10, 10))
	for i, (spectrogram, transcript) in enumerate(dataset.take(n)):
		r = i // cols
		c = i % cols
		ax = axes[r][c]
		plot_spectrogram(np.squeeze(spectrogram.numpy()), ax)
		ax.set_title([char2idx[c] for c in transcript])	# finicky
		ax.axis('off')

	plt.show()
#########################



def create_sequential_model(input_shape, norm_layer, num_labels):
	model = models.Sequential([
		layers.Input(shape=input_shape),
		preprocessing.Resizing(32, 32), 
		# norm_layer,					# Not sure if this is causing the issue
		layers.Conv2D(32, 3, activation='relu'),
		layers.Conv2D(64, 3, activation='relu'),
		layers.MaxPooling2D(),
		layers.Dropout(0.25),
		# layers.Flatten(),					# Reshape instead??
		layers.Dense(128, activation='relu'),
		layers.Dropout(0.5),
		layers.Dense(num_labels)])

	return model



if __name__ == '__main__':
		
	
	tf.compat.v1.enable_eager_execution()
	# Set seed for experiment reproducibility
	seed = 42
	tf.random.set_seed(seed)
	np.random.seed(seed)
	print("Using Seed: ", seed)


	# train_data_dir = '../ASR/data/train-clean-100/LibriSpeech/train-clean-100'		# ignoring this big set for now
	train_data_dir = '../ASR/data/dev-clean/LibriSpeech/dev-clean'		# training on the small dev set for now (usually for validation)
	test_data_dir = '../ASR/data/test-clean/LibriSpeech/test-clean'		# testing on the test set

	train_data_dir = r'../ASR/data/small_data/dev-clean-wav'		# fast
	test_data_dir = r'../ASR/data/small_data/test-clean-wav'		# fast

	print(f'get_dataset:')
	# train_ds = get_dataset(train_data_dir)
	train_ds = get_dataset(train_data_dir)
	test_ds = get_dataset(test_data_dir)


	space_token = ' ' # "\u2581" encoded in utf-8 but underscore in ascii
	end_token = '>'     # <\s> in fairseq <eos> in other places
	blank_token = '?'   # common blank token
	alphabet = list(ascii_lowercase) + ["'", space_token, end_token, blank_token] # append spaces, end token (for fairseq), and blank_token for separating repeating characters
	num_labels = len(alphabet)

	# vectorize string
	char2idx = {u:i for i, u in enumerate(alphabet)}	# ENCODE
	idx2char = np.array(alphabet)	# DECODE

	# prep_train_ds = preprocess_dataset(train_ds, char2idx)
	prep_train_ds = preprocess_dataset(train_ds)	# should be dev
	prep_test_ds = preprocess_dataset(test_ds)
	spectrogram_ds = prep_train_ds
	
	try:
		display_spec_in_dataset(prep_train_ds)
		display_spec_in_dataset(prep_test_ds)
	except Exception as e:
		print(e)
	

	batch_size = 1
	prep_train_ds = prep_train_ds.batch(batch_size).cache().prefetch(AUTOTUNE)
	prep_test_ds = prep_test_ds.batch(batch_size).cache().prefetch(AUTOTUNE)


	for spec, trans in spectrogram_ds.take(1):
		input_shape = spec.shape
		print('Input shape:', input_shape)
		trans_shape = trans.shape
		print('Trans shape:', trans_shape)
	


	

	# def print_ret(x, y):
	# 	print(x)
	# 	return x

	norm_layer = preprocessing.Normalization()
	# norm_layer.adapt(spectrogram_ds.map(print_ret))
	norm_layer.adapt(spectrogram_ds.map(lambda x, _: x))


	sequential = create_sequential_model(input_shape, norm_layer, num_labels)

	sequential.summary()
	# def ctc_loss_func(args):
	# 	y_pred, labels, input_length, label_length = args
	# 	return tf.keras.ctc_batch_cost(labels, y_pred, input_length, label_length)
	
	from basic_model import CustomModel

	c_model = CustomModel(sequential.input, sequential.output)

	c_model.compile(optimizer=tf.keras.optimizers.Adam())

	EPOCHS = 2	# 100
	history = c_model.fit(
		prep_train_ds, 
		validation_data=prep_test_ds,  
		epochs=EPOCHS,
		callbacks=tf.keras.callbacks.EarlyStopping(verbose=1, patience=2),
	)


	# test inference

	# sample_file = test_data_dir + filename

	# sample_ds = preprocess_dataset([str(sample_file)])	# change this

	# for spectrogram, label in sample_ds.batch(1):
	# prediction = model(spectrogram)
	# plt.bar(commands, tf.nn.softmax(prediction[0]))
	# plt.title(f'Predictions for "{commands[label[0]]}"')

	# use prefix decoder and calc CER

	# plt.show()