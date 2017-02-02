#!/usr/bin/env python

"""
Copyright 2017 Parham Pourdavood

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import division
from SimpleAudioIndexer import SimpleAudioIndexer as sai
from subprocess import Popen as popen
from watson_developer_cloud import ToneAnalyzerV3
from math import floor
import ast
import argparse
import speech_recognition as sr
import os
import httplib
import urllib
import ConfigParser
import shutil


def video_to_audio(video_abs_path, audio_abs_path):
    """
    Converts a video file to audio

    Paramteters
    -----------
    video_abs_path     str
    audio_abs_path     str
    """

    popen("ffmpeg -i {} -vn -acodec pcm_s16le -ar 44100 -ac 2 {}".format(
        video_abs_path, audio_abs_path), shell=True).communicate()


def audio_to_text(audio_abs_path, IBM_USERNAME, IBM_PASSWORD):
    """
    Converts audio voice into written text using IBM Watson

    Parameters
    ----------
    audio_abs_path     str
    IBM_USERNAME       str
    IBM_PASSWORD       str

    Returns
    -------
    data          str
    """
    r = sr.Recognizer()
    with sr.AudioFile(audio_abs_path) as f:
        audio = r.record(f)
    data = r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD)
    return data


def tone_json_maker(text_input, TONE_USERNAME, TONE_PASSWORD):
    """
    Takes a text as parameter and returns JSON created by IBM Tone Analyzer API

    Parameters
    ----------
    text_input      str
    TONE_USERNAME   str
    TONE_PASSWORD   str

    Returns
    -------
    jsonOutput      dict
    """
    tone_analyzer = ToneAnalyzerV3(
        username=TONE_USERNAME,
        password=TONE_PASSWORD,
        version='2016-05-19')
    jsonOutput = tone_analyzer.tone(text=text_input)
    return jsonOutput


def sentence_tone_maker(tones_list):
    """
    It takes a list which is the value of key of "tones" that is created for
    each sentence in the JSON created by tone_json_make above. The function
    returns the tone that best describes the sentence.

    Paramters
    ---------
    tones_list      list

    Returns
    -------
    best_tone       str
    """
    highest_score = 0
    best_tone = ""

    for i in range(4):
        if tones_list[i]["score"] > highest_score:
            highest_score = tones_list[i]["score"]
            best_tone = tones_list[i]["tone_name"]
    return best_tone


def sentence_tone_model(json_input):
    """
    Takes the JSON created by tone_json_maker and returns a model that we will
    use later in form of a dictionary.The model is a dictionary with keys being
    emotions and the value for each emotion is a list that consists of dicts
    with keys being sentences and values being empty tuples that we will use
    later.

    Paramters
    ---------
    json_input  dict

    Returns
    -------
    dict        dict

    """
    dict = {"anger": [], "disgust": [], "fear": [], "joy": [], "sadness": []}
    sentences_number = len(json_input["sentences_tone"])

    for i in range(sentences_number):
        sentences_text = json_input["sentences_tone"][i]["text"]
        sentences_list = json_input["sentences_tone"][i]["tone_categories"][0]["tones"]
        if sentence_tone_maker(sentences_list) == "Anger":
            dict["anger"].append({sentences_text[:-1]: ()})
        elif sentence_tone_maker(sentences_list) == "Disgust":
            dict["disgust"].append({sentences_text[:-1]: ()})
        elif sentence_tone_maker(sentences_list) == "Fear":
            dict["fear"].append({sentences_text[:-1]: ()})
        elif sentence_tone_maker(sentences_list) == "Joy":
            dict["joy"].append({sentences_text[:-1]: ()})
        else:
            dict["sadness"].append({sentences_text[:-1]: ()})
    return dict


class audio_analyzer(object):

    def __init__(self, username, password, src_dir):
        self.username = username
        self.password = password
        self.src_dir = src_dir
        self.indexer = sai(username, password, src_dir)
        self.indexer.index_audio()

    def audio_search(self, query, audio_basename=None,
                     part_of_bigger_word=False, timing_error=0.1):
        """
        A generator that searches for the `query` within the audiofiles of the
        src_dir.
        Parameters
        ----------
        query          str
                        A string that'll be searched. It'll be splitted on
                        spaces and then each word gets sequentially searched
        audio_basename str
                        Search only within the given audio_basename
        part_of_bigger_word     bool
                                `True` if it's not needed for the exact word be
                                detected and larger strings that contain the
                                given one are fine. Default is False.
        timing_error    float
                        Sometimes other words (almost always very small) would
                        be detected between the words of the `query`. This
                        parameter defines the timing difference/tolerance of
                        the search. By default it's 0.1, which means it'd be
                        acceptable if the next word of the `query` is found
                        before 0.1 seconds of the end of the previous word.
        Yields
        ------
        -               {"File Name": str,
                         "Query": `query`,
                         "Result": (float, float)}
                         The result of the search is returned as a tuple which
                         is the value of the "Result" key. The first element
                         of the tuple is the starting second of `query` and
                         the last element is the ending second of `query`
        """
        return self.indexer.search(query, audio_basename=None,
                                   part_of_bigger_word=False,
                                   timing_error=0.5)


def time_stamps_adder(model_input, username, password, src_dir):
    """
    This function uses audio_search method of audio_analyzer class to index the
    sentences in the audio and find the time stamps they happen. It then adds
    the time stamps for each sentence in the unfinished model that was returned
    by sentence_tone_model function.

    Parameters
    ----------
    model_input:        dict
                        Returned by sentence_tone_model function
    username:           str
    password:           str
    src_dr:             str
                        The directory that the audio converted from orig. video
    Returns
    -------
    model_input:        dict
    """
    searcher = audio_analyzer(username, password, src_dir)

    for i in model_input.keys():
        if model_input[i] != []:
            for j in model_input[i]:
                tmp = ' '.join(filter((lambda x: "'" not in x),
                               j.keys()[0].split(" ")))
                search_result = (list(searcher.audio_search(tmp)))
                try:
                    stamp_tuple = search_result[0]['Result']
                    j[j.keys()[0]] = stamp_tuple
                    if stamp_tuple == ():
                        model_input[i].remove(j)
                except IndexError:
                    model_input[i].remove(j)
                    continue
    return model_input


def picture_emotion(image_src, API_KEY):
    """
    This function detects the face in a picture and returns the most probable
    emotion that is recognized in the face.

    Parameters
    ----------
    image_src:      str
    API_KEY:        str

    Returns
    -------
    emotion_name:   str
    """

    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': API_KEY,
    }

    params = urllib.urlencode({
        # Request parameters
            'outputStyle': 'perFrame',
    })
    with open(image_src, 'rb') as f:
        data = f.read()

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/emotion/v1.0/recognize?%s" % params, data,
                     headers)
        response = conn.getresponse()
        data = ast.literal_eval(response.read())
        conn.close()
        emotion_dict = data[0]["scores"]
        print emotion_dict.keys()
        highest_score = 0
        emotion_name = ""
        for i in emotion_dict.keys():
            print i
            if emotion_dict[i] > highest_score:
                highest_score = emotion_dict[i]
                emotion_name = i
        if emotion_name == "happiness":
            emotion_name = "joy"
        return emotion_name
    except Exception:
        return "Not recognized"


def seconds_formatter(seconds):
    """
    Converts total seconds to HH:MM:SS.tttt format

    Parameters
    ----------
    seconds            str or numeric

    Returns
    -------
    -                  str
    """
    if type(seconds) == str:
        seconds = float(seconds)
    minutes, seconds = divmod(floor(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if minutes < 10:
        minutes = "0" + str(int(minutes))
    else:
        minutes = int(minutes)
    if hours < 10:
        hours = "0" + str(int(hours))
    else:
        hours = int(hours)
    if seconds < 10:
        seconds = "0" + str(int(seconds))
    else:
        seconds = int(seconds)
    formatted = "{}:{}:{}".format(hours, minutes, seconds)
    return formatted


def get_frame_emotion(video_src, image_dest, frame_time):
    """
    This function takes a snapshot of a video file given a certain time.certain

    Parameters
    ----------
    video_src:      str
    image_dest:     str
    frame_time:     str
                    It must be in form of HH:MM:SS (see seconds_formatter func.)
    """
    popen("ffmpeg -y -ss {} -i {} -vframes 1 -q:v 2 {}".format(
        frame_time, video_src, image_dest), shell=True).communicate()


def face_emotion_adder(model_input, video_src, image_dest, API_KEY):
    """
    Goes over the model and according the timestamp of each sentence uses the
    get_frame_emotion to take a snapshot of the video at the middle of the time
    that the sentence is happened. It then uses picture_emotion function to
    give the emotion of the face in that picture. Face emotion are added into
    the model at the end. This is out final model.

    Parameters
    ----------
    model_input:        dict
    video_src:          str
    image_Dest:         str
    API_KEY:            str
                        Microsoft Emotion API Key
    Returns
    -------
    model_input:        dict
                        New and final model with face emotions added
    """
    for i in model_input.keys():
        if model_input[i] != []:
            for j in model_input[i]:
                if j[j.keys()[0]]:
                    time_average = (j[j.keys()[0]][0] + j[j.keys()[0]][1]) / 2
                    time = seconds_formatter(time_average)
                    print j[j.keys()[0]][0]
                    print time
                    get_frame_emotion(video_src, image_dest, time)
                    a = picture_emotion(image_dest, API_KEY)
                    j[j.keys()[0]] = a
    return model_input


def ConfigParser_handler(credentials):
    """
    It uses Configparser to add our API credentials saved for the user in the
    their machine. A INI file called ".ata_credentials.ini" will be added in
    the home directory of user. The parameter credentials should be a string
    with API usernames and paswords seperated with spaces and in this order:
    IBM_USERNAME, IBM_PASSWORD, TONE_USERNAME, TONE_PASSWORD, Microsfot_API_KEY

    Parameters
    ----------
    credentials:        str

    """
    cred_list = credentials.split(" ")
    config = ConfigParser.ConfigParser()

    config.add_section("Keys")
    config.set("Keys", "IBM_USERNAME", cred_list[0])
    config.set("Keys", "IBM_PASSWORD", cred_list[1])
    config.set("Keys", "TONE_USERNAME", cred_list[2])
    config.set("Keys", "TONE_PASSWORD", cred_list[3])
    config.set("Keys", "Microsfot_API_KEY", cred_list[4])

    config_path = os.path.join(os.path.expanduser("~"), ".ata_creds.ini")

    with open(config_path, "wb") as config_file:
        config.write(config_file)

    if os.path.exists(config_path):
        print "Sucess! Your credentials were saved."
    else:
        print "Failed. Your credentials could not be saved."


def ConnfigParser_reader(cred_path):
    """
    This function gets the credential file's path that was made with
    Configparser and reads it for the user.

    Parameters
    ----------
    cred_path:      str

    Returns
    -------
    (IBM_USERNAME, IBM_PASSWORD, TONE_USERNAME,
     TONE_PASSWORD, Microsfot_API_KEY

    """
    config = ConfigParser.ConfigParser()
    config.read(cred_path)

    IBM_USERNAME = config.get("Keys", "IBM_USERNAME")
    IBM_PASSWORD = config.get("Keys", "IBM_PASSWORD")
    TONE_USERNAME = config.get("Keys", "TONE_USERNAME")
    TONE_PASSWORD = config.get("Keys", "TONE_PASSWORD")
    Microsfot_API_KEY = config.get("Keys", "Microsfot_API_KEY")

    return(IBM_USERNAME, IBM_PASSWORD, TONE_USERNAME,
           TONE_PASSWORD, Microsfot_API_KEY)


def argument_handler():
    """
    Argparse argument handler.

    """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-credentials", "--credentials",
                       help="Command for saving API credentials", type=str)
    group.add_argument("-v", "--src_vid", help="Therapy's recording video",
                       type=str)

    args = parser.parse_args()

    cred_path = os.path.join(os.path.expanduser("~"), ".ata_creds.ini")

    if args.src_vid:
        if not os.path.exists(cred_path):
            parser.error("The credentials file has not been created yet")
    return (args.credentials, args.src_vid, cred_path)


def generator(src_vid, IBM_USERNAME, IBM_PASSWORD, TONE_USERNAME,
              TONE_PASSWORD, Microsfot_API_KEY):
    """
    Uses all the functions created in this file to create the final model.
    To recap: Video to audio, speech to text, get the tone of each sentence,
    use each sentence to index the audio and get the timestaps for them,
    add the timestamps to the model, use the time stamps to take snapshot of
    that moment the sentence is spoken, detect the emotion in the face,
    add the face emotion to the model. Done!

    Parameters
    ----------
    src_vid:            str
    IBM_USERNAME:       str
    IBM_PASSWORD:       str
    TONE_USERNAME:      str
    TONE_PASSWORD:      str
    Microsfot_API_KEY:  str

    Returns
    -------
    complete_model:     dict

    """
    video_dir = os.path.dirname(src_vid)

    ata_folder = os.path.join(video_dir, ".ata")

    # Deleter the unecessary file if it was created for a previous processing
    # in order to process the video
    if os.path.exists(ata_folder):
        shutil.rmtree(ata_folder)

    os.mkdir(ata_folder)

    src_audio = os.path.join(ata_folder, "audio.wav")
    src_image = os.path.join(ata_folder, "image.jpg")

    video_to_audio(src_vid, src_audio)

    ata_text = audio_to_text(src_audio, IBM_USERNAME, IBM_PASSWORD)

    tone_json = tone_json_maker(ata_text, TONE_USERNAME, TONE_PASSWORD)

    tone_model = sentence_tone_model(tone_json)

    timed_model = time_stamps_adder(tone_model, IBM_USERNAME,
                                    IBM_PASSWORD, ata_folder)
    complete_model = face_emotion_adder(timed_model, src_vid, src_image,
                                        Microsfot_API_KEY)

    shutil.rmtree(ata_folder)

    return complete_model


def final_analysis(model_input):
    """
    "Change the format of the model so that the keys are now sentenced with
    keys beng their face and speech content emotions."

    Parameter
    ---------
    model_input:        dict

    Returns
    -------
    final_dict:         dict
    """
    final_dict = {}
    for i in model_input.keys():
        if model_input[i] != []:
            for j in model_input[i]:
                final_dict[j.keys()[0]] = {"text": i, "face": j[j.keys()[0]]}
    return final_dict


def get_analysis(model_input):
    """
    Returns a model that consists of frequency of data of our final model.

    Parameters
    ----------
    model_input:        dict

    Returns
    -------
    analysis_model:     dict

    """
    analysis_model = {"total": 0, "matched": 0, "unmatched": 0,
                      "joy": (0, 0), "anger": (0, 0), "fear": (0, 0),
                      "disgust": (0, 0), "sadness": (0, 0)}

    for i in final_an.keys():
        number_of_sentences = len(final_an.keys())

        analysis_model["total"] = number_of_sentences

        if final_an[i]["text"] == final_an[i]["face"]:
            analysis_model["matched"] += 1
            analysis_model[final_an[i]["text"]][1] += 1
        else:
            analysis_model["unmatched"] += 1

        analysis_model[final_an[i]["text"]][0] += 1

    return analysis_model


def graph_generator(analysis_model):



if __name__ == '__main__':

    credentials, src_vid, cred_path = argument_handler()

    if credentials:
        ConfigParser_handler(credentials)

    else:

        IBM_USERNAME, IBM_PASSWORD, TONE_USERNAME, TONE_PASSWORD, Microsfot_API_KEY = ConnfigParser_reader(cred_path)

        result = generator(src_vid, IBM_USERNAME, IBM_PASSWORD, TONE_USERNAME,
                           TONE_PASSWORD, Microsfot_API_KEY)
        # result = {'anger': [{u'wrong': 'Not recognized'}, {u"Perot sometimes they get a feeling she's": 'neutral'}, {u"ten to decide which restaurant we're going to end scion has to decide a": 'neutral'}, {u"so you don't lines around to pick because you like me and that is better": 'joy'}, {u'you tied Macias': ()}, {u"why don't you like Bosnia": 'joy'}], 'joy': [{u"is there any place that we take you that you don't like that makes you feel anxious": 'neutral'}, {u'we did': 'neutral'}, {u'we play leann I is I get picked to': 'neutral'}, {u'when we do that': 'neutral'}, {u'or do you rather somebody else pick it': 'neutral'}, {u'there were other': 'neutral'}, {u'you were saying': 'neutral'}, {u"round pick somebody's opinion as good restaurants that I get that he would say was to dog food": 'neutral'}, {u'and the best parents': 'neutral'}, {u'of a boy could ever have': 'neutral'}, {u'do you want a pony': 'neutral'}, {u'that was very sweet Jane and thank you': 'joy'}, {u'pretty much pretty much': ()}, {u'I like your honesty': 'neutral'}, {u"do you do something that is I will pick a restaurant that you'll like": 'neutral'}, {u'picking': 'neutral'}, {u'well': 'Not recognized'}, {u"kinda like you know I'm glad to get a shot": 'Not recognized'}, {u'actually it': 'Not recognized'}, {u'yes': 'Not recognized'}, {u'when he gets to choose a restaurant he always': 'Not recognized'}, {u"thanks Bosnia's month yes razzia": 'Not recognized'}, {u'I see': 'Not recognized'}, {u'well': ()}, {u'is acting or yeah': 'Not recognized'}], 'fear': [{u'you know I say why why would anyone silence I': ()}, {u'so okay securities': 'Not recognized'}, {u'no but really what why yeah why would you rather be naked than than Sonatine': 'Not recognized'}, {u'lying in terror': 'Not recognized'}, {u'or do you just not like the sound': ()}], 'sadness': [{u'whenever': 'Not recognized'}, {u'whenever': 'Not recognized'}, {u'and': 'Not recognized'}, {u'whenever': 'Not recognized'}, {u'wherever': 'Not recognized'}, {u'wherever': 'Not recognized'}, {u'and': 'Not recognized'}, {u'whenever': 'Not recognized'}, {u'arrow': 'Not recognized'}, {u'and': 'Not recognized'}, {u'and': 'Not recognized'}, {u'right': 'Not recognized'}, {u'every': 'Not recognized'}], 'disgust': []}
        final_an = final_analysis(result)

        result_path = os.path.join(os.path.dirname(src_vid), "ata_result.txt")

        with open(result_path, "w") as f:
            f.write(str(final_an))
