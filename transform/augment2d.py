import cv2
import numpy as np


# Handles BGR images of type uint8
class Augment2D(object):


	# rotate_hard 	=>	rotate by 90 degrees
	# rotate_soft 	=> 	rotate by 1 degrees
	# zoom			=> 	x,y independent streching and squashing
	# noise		 	=> 	color noise
	# pixel_shift 	=> 	change brightness (independent channels)
	# blur			=> 	smooth the image
	# position_shift=>	move the image in x,y
	# lab_shift		=>  changes brightness (lab color space, independent channels)
	# contrast 		=>  changes the contrast of the image

	def __init__(self,rotate_hard=True,rotate_soft=False,zoom=0.5,noise=0.5,pixel_shift=0.5,blur=0.5,position_shift=True,lab_shift=0.5,flip=True,contrast=0.5):
		self.rotate_hard = rotate_hard
		self.rotate_soft = rotate_soft
		self.zoom=zoom
		self.noise=noise
		self.pixel_shift=pixel_shift
		self.blur = blur
		self.position_shift=position_shift
		self.lab_shift=lab_shift
		self.flip=flip
		self.contrast=contrast

	def augment(self,data,labels):

		# Order
		# lab_shift
		# pixel_shift
		# blur
		# flip
		# zoom
		# rotate_hard
		# rotate_soft
		# noise

		if self.lab_shift > 0:	data,labels = self._lab_shift(data,labels) 
		if self.pixel_shift > 0:	data,labels = self._pixel_shift(data,labels)
		if self.contrast > 0:	data,labels = self._contrast(data,labels)
		if self.blur > 0:	data,labels = self._blur(data,labels)
		if self.flip:		data,labels = self._flip(data,labels)
		if self.zoom > 0:	data,labels = self._zoom(data,labels)
		if self.rotate_hard and self.rotate_soft==False:	data,labels = self._rotate_hard(data,labels)
		if self.rotate_soft:	data,labels = self._rotate_soft(data,labels)
		if self.noise > 0:	data,labels = self._noise(data,labels)

		return data,labels


	def _pixel_shift(self,data,labels):
		for i in range(len(data)):
			shift_variance = int(self.pixel_shift*32.0)
			rgb = np.random.randint(-shift_variance,shift_variance,size=data[i].shape[-1]).astype(int)
			data[i] = data[i].astype(int)
			data[i] += rgb
			data[i] = np.clip(data[i],0,255).astype(np.uint8)
		return data,labels

	def _blur(self,data,labels):
		for i in range(len(data)):
			if np.random.uniform() < 0.25:
				continue
			kernel_size = max(1,int(np.random.randint(self.blur*10)*2+1))
			data[i] = self.correct_gray(cv2.GaussianBlur(self.correct_gray(data[i],add_dim=False),(kernel_size,kernel_size),0))
		return data,labels

	def _zoom(self,data,labels):
		zoom = -0.5 * self.zoom
		for i in range(len(data)):
			zoom_factor = zoom*np.random.uniform(size=2)
			z_data = cv2.resize(data[i],None,fx=zoom_factor[0]+1,fy=zoom_factor[1]+1,interpolation=cv2.INTER_CUBIC)
			z_label = cv2.resize(labels[i],None,fx=zoom_factor[0]+1,fy=zoom_factor[1]+1,interpolation=cv2.INTER_CUBIC)
			n_data = np.zeros_like(data[i])
			n_label = np.zeros_like(labels[i])

			x_offset = int((n_data.shape[1]-z_data.shape[1])/2.0)
			y_offset = int((n_data.shape[0]-z_data.shape[0])/2.0)
			n_data[y_offset:y_offset+z_data.shape[0], \
				x_offset:x_offset+z_data.shape[1]] = self.correct_gray(z_data)
			n_label[y_offset:y_offset+z_label.shape[0], \
				x_offset:x_offset+z_label.shape[1]] = self.correct_gray(z_label)

			data[i] = n_data
			labels[i] = n_label

		return data,labels
		
	def _rotate_hard(self,data,labels):
		for i in range(len(data)):
			height,width=data[i].shape[:2]
			rot = np.random.randint(4)
			data[i] = np.rot90(data[i],rot)
			labels[i] = np.rot90(labels[i],rot)
			#matrix = cv2.getRotationMatrix2D((width/2,height/2),np.random.randint(4)*90,1)
			#data[i] = self.correct_gray(cv2.warpAffine(data[i],matrix,(width,height)))
			#labels[i] = self.correct_gray(cv2.warpAffine(labels[i],matrix,(width,height)))
		return data,labels

	def _rotate_soft(self,data,labels):
		for i in range(len(data)):
			height,width=data[i].shape[:2]
			matrix = cv2.getRotationMatrix2D((width/2,height/2),np.random.randint(360),1)
			data[i] = self.correct_gray(cv2.warpAffine(data[i],matrix,(width,height)))
			labels[i] = self.correct_gray(cv2.warpAffine(labels[i],matrix,(width,height)))
		return data,labels

	def _noise(self,data,labels):
		for i in range(len(data)):
			height,width = data[i].shape[:2]
			rand = np.random.randint(0,256,size=data[i].size).reshape(data[i].shape)
			rand_range = np.random.uniform(size=data[i].shape[0]*data[i].shape[1]).reshape(data[i].shape[:2])
			y,x = np.where(rand_range < self.noise/2.0)

			data[i][y,x,:] = rand[y,x,:]
		return data,labels

	def _lab_shift(self,data,labels):
		for i in range(len(data)):
			lab = cv2.cvtColor(data[i],cv2.COLOR_BGR2LAB)

			shift_variance = int(self.lab_shift*32.0)
			rgb_add = np.random.randint(-shift_variance,shift_variance,size=lab.shape[-1]).astype(int)
			lab = lab.astype(int)
			lab += rgb_add
			lab = np.clip(lab,0,255).astype(np.uint8)

			data[i] = cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)
		return data,labels


	def _flip(self,data,labels):
		for i in range(len(data)):
			# 1/3 chance for flimlr,flipup,do-nothing
			val = np.random.uniform()
			# flip lr
			if val < 1.0/3.0:
				data[i] = np.fliplr(data[i])
				labels[i] = np.fliplr(labels[i])
			# flip ud
			elif val < 2.0/3.0:
				data[i] = np.flipud(data[i])
				labels[i] = np.flipud(labels[i])

		return data,labels

	def _contrast(self,data,labels):
		for i in range(len(data)):
			contrast_value = np.random.uniform()
			std = 0.5 * self.contrast
			contrast_value *= std
			contrast_value += 1-std
			contrast_value = np.clip(2.0,0.1,contrast_value)

			c_im = data[i].astype(np.float32)
			c_im *= contrast_value
			c_im = np.clip(255,0,c_im)
			data[i] = c_im.astype(np.uint8)

		return data,labels


	def correct_gray(self,image,add_dim=True):
		if add_dim:
			if len(image.shape) == 2:
				return image.reshape([image.shape[0],image.shape[1],1])
			return image
		else:
			if len(image.shape) == 3:
				if image.shape[-1] == 1:
					return image.reshape(image.shape[:2])
			return image

	def cut_size_hard(self,data,labels,cut_perc=0.1):
		for i in range(len(data)):
			r,d,l,u = np.random.uniform(size=4)*cut_perc

			height,width = data[i].shape[:2]
			right = int(width * r)
			down = int(height * d)
			left = int(width * l)
			up = int(height * u)

			data[i] = data[i][up:height-down,left:width-right]
			labels[i] = labels[i][up:height-down,left:width-right]
		return data,labels