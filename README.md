# ai_lab
ai_lab is a library for loading datasets, data augmentation, training management, experiment management and result documentation

# Sample

aug = Augment2D(<br/>
	blur=0.1,<br/>
	pixel_shift=0.1,<br/>
	rotate_hard=True,<br/>
	rotate_soft=False,<br/>
	noise=0.01,<br/>
	zoom=0.2,<br/>
	lab_shift=0.5,<br/>
	flip=True,<br/>
	contrast=0.5)<br/>
  <br/>
  data_in,labels_in = [im for _ in range(aug_count)], [label for _ in range(aug_count)] # number of samples to be dublicated and augmented in different ways<br/>
  data_in,labels_in = aug.cut_size_hard(data_in,labels_in) # Randomize region/aspectratio of samples<br/>
  data,labels = aug.augment(data_in,labels_in) # augment with init parameters<br/>
