import tempfile
from PIL import Image


def generate_list_of_images():
	image1 = Image.new('RGB', (100, 100))
	image2 = Image.new('RGB', (100, 100))
	image3 = Image.new('RGB', (100, 100))
	image4 = Image.new('RGB', (100, 100))
	image5 = Image.new('RGB', (100, 100))
	image6 = Image.new('RGB', (100, 100))

	tmp_file1 = tempfile.NamedTemporaryFile(suffix='.jpg')
	tmp_file2 = tempfile.NamedTemporaryFile(suffix='.png')
	tmp_file3 = tempfile.NamedTemporaryFile(suffix='.jpg')
	tmp_file4 = tempfile.NamedTemporaryFile(suffix='.png')
	tmp_file5 = tempfile.NamedTemporaryFile(suffix='.jpg')
	tmp_file6 = tempfile.NamedTemporaryFile(suffix='.png')
	image1.save(tmp_file1)
	image2.save(tmp_file2)
	image3.save(tmp_file3)
	image4.save(tmp_file4)
	image5.save(tmp_file5)
	image6.save(tmp_file6)

	tmp_file1.seek(0)
	tmp_file2.seek(0)
	tmp_file3.seek(0)
	tmp_file4.seek(0)
	tmp_file5.seek(0)
	tmp_file6.seek(0)

	images = [
		tmp_file1,
		tmp_file2,
		tmp_file3,
		tmp_file4,
		tmp_file5,
		tmp_file6
	]
	return images
