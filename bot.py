# bot.py

import random
from io import BytesIO

import requests
import tweepy
from PIL import Image
from PIL import ImageFile

from secrets import *


ImageFile.LOAD_TRUNCATED_IMAGES = True

# create an OAuthHandler instance
# Twitter requires all requests use OAuth for authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
# Construct the API instance
api = tweepy.API(auth)


def tweet_image(url, username, status_id):
    filename = 'temp.png'
    # send a get request
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        # read date from downloaded bytes and returns a PIL.Image.Image object
        i = Image.open(BytesIO(request.content))
        # saves the image under the given filename
        i.save(filename)
        scramble(filename)
        # update the authenticated user's status
        # if I'm tweeting at myself, don't go into infinite loop
        if(username == "jacobcfuller"):
            api.update_with_media('scramble.png',
                                  status='test',
                                  in_reply_to_status_id=status_id)
        else:
            api.update_with_media('scramble.png',
                                  status='@{0}'.format(username),
                                  in_reply_to_status_id=status_id)

    else:
        print("unable to download image")


def scramble(filename):
    BLOCKLEN = 64

    img = Image.open(filename)
    width, height = img.size

    xblock = width // BLOCKLEN
    yblock = height // BLOCKLEN
    # creates sequence of 4-tuples (box) defining the left, upper, right, and lower pixel coordinate
    blockmap = [(xb * BLOCKLEN, yb * BLOCKLEN, (xb + 1) * BLOCKLEN, (yb + 1) * BLOCKLEN)
                for xb in range(xblock) for yb in range(yblock)]

    shuffle = list(blockmap)
    # shuffle the sequence
    random.shuffle(shuffle)

    # creates a new image with the given mode and size
    result = Image.new(img.mode, (width, height))
    for box, sbox in zip(blockmap, shuffle):
        # returns a rectangular region from this original image.
        crop = img.crop(sbox)
        # Pastes the croppeed pixel into the new image object
        result.paste(crop, box)
    result.save('scramble.png')


# create a class inheriting from the tweepy StreamListener
class BotStreamer(tweepy.StreamListener):
    # called when a new status arrives which is passed down fro mthe on_data method of the StreamListener
    def on_status(self, status):
        username = status.user.screen_name
        status_id = status.id

        # entities provide structured data from Tweets including resolved URLs,
        # media, hashtags, and mentions without having to parse text
        if 'media' in status.entities:
            for image in status.entities['media']:
                tweet_image(image['media_url'], username, status_id)


myStreamListener = BotStreamer()
# construct stream instance
stream = tweepy.Stream(auth, myStreamListener)
stream.filter(track=['@jacobcfuller'])
