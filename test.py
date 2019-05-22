from keras.preprocessing import image

from PIL import Image, ExifTags

# https://gist.github.com/baraldilorenzo/07d7802847aaad0a35d3

def image_orient(img_path):

    try:
        # load image from disk
        image=Image.open(img_path)
        print(image.size) # flag

        # It grabs the "Orientation" tag from the ExifTags collection and later uses it for testing the orientation value. 
        # It cycles through all the different tag keys until it finds the right one and then breaks, leaving the key value at the correct key.
        for key in ExifTags.TAGS.keys():
            print(key)
            if ExifTags.TAGS[key]=='Orientation':
                break
        
        exif=dict(image._getexif().items())
        print(key)
        print(exif)

        # here, it uses the correct key to check orientation
        if exif[key] == 3:
            image=image.rotate(180, expand=True)
        elif exif[key] == 6:
            image=image.rotate(270, expand=True)
        elif exif[key] == 8:
            image=image.rotate(90, expand=True)
        print(image.size) # flag

        # override the image
        image.save(img_path)
        image.close()

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        print('No Exif Key')
        pass

    # height = img.shape[0]
    # width = img.shape[1]
    # print(img.shape)

    # if height > width:
    #     # rotate it if it's a vertical image
    #     image_style = 'transform:rotate(90deg); width:325px;'
    # else:
    #     # otherwise the image is landscape
    #     image_style = 'transform:rotate(0deg); width:525px;'

    # return image_style

path = 'static\\uploads\\IMG_3869.JPG'
print(image_orient(path))
