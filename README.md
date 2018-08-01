# ai_lab
ai_lab is a library for loading datasets, data augmentation, training management, experiment management and result documentation

# Sample

aug = Augment2D(
	blur=0.1,
	pixel_shift=0.1,
	rotate_hard=True,
	rotate_soft=False,
	noise=0.01,
	zoom=0.2,
	lab_shift=0.5,
	flip=True,
	contrast=0.5)
  
  data_in,labels_in = [im for _ in range(aug_count)], [label for _ in range(aug_count)]
  data_in,labels_in = aug.cut_size_hard(data_in,labels_in)
  data,labels = aug.augment(data_in,labels_in)
