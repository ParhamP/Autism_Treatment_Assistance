# Autism Treatment Assistance

<!-- <img align="center" src="https://github.com/ParhamP/Autism_Treatment_Assistance/blob/master/images/logo.png?raw=true" alt="..."> -->

<p align="center">
<img src="https://github.com/ParhamP/Autism_Treatment_Assistance/blob/master/images/logo.png?raw=true">
</p>

## Description

Autism Treatment Assistance introduces an advanced tool that assists pyschologists and therapists effectively treat a common autism symptom that makes it difficult for autistic people to interpret emotions and to give prpoper facial expressions when confronted with different emotions.


ATA uses IBM Watson Tone Analyzer and Microsoft Emotion API to detect emotions in both speech and facial expressions of an autistic patient during a therapy session, and by comparing the two it will report to the therapist a detailed analysis and graphical representation of how the patient performed during the session and how in-sync the facial expressions were with correlation to the content of speech.

## How It Works

### 1- Video to Audio to Speech:

The video of the therapy gets converted to audio and then the speech of the audio gets converted to text using IBM Watson Speech-to-Text API.

### 2- Analyzing the Content of Speech:

The program uses IBM Watson Tone Analyzer to determine the dominant emotion in the content of each sentence.

### 3- Searching and Indexing Audio:

It then uses SimpleAudioIndexer to search through the audio to index when those sentences exactly 
happended.

### 4- Recognize the emotion in Face during Timestamped Sentences

Using the saved timestamps, the program uses Microsoft Emotion API to detect the dominant face emotions during those sentences.

### 5- Build a model

A comprehensive model is created that consists of sentences and their coressponding face and speech emotions. 

### 6- Turn Data into Insights

Returns various analysis and versions of the model.

### 7- Graphical and Statistical Representation of Data

Uses matplotlib and numpy libraries to draw statistical and graphical representations of data


## Get Started

### Dependencies

- IBM Watson Speech to Text API Username and Password (Here)
- IBM Watson Tone Analyzer API Username and Passowrd (Here)
- Microsoft Emotion API Key (Here)
- SimpleAudioIndexer
- matplotlib
- numpy
- ffmpeg

### Install

`sudo pip install Autism_Treatment_Assistance`

### Usage

Have your therapy video and API keys ready.

1- Just for the first time let the program (using ConfigParser) save your API credentials so you don't have to enter them each time. (Preserve the order and place them in a string)

`ata -credentials "IBM_USERNAME IBM_PASSWORD IBM_TONE_USERNAME IBM_TONE_PASSWORD Microsfot_API_KEY"`

2- `ata -v ABS_PATH_TO_VIDEO -d ABS_PATH_FOR_DESTINATION`

3- A folder named ATA containing the analysis and gaphs is created in the destination that you chose.

## Samples

<p align="center">
<img src="https://github.com/ParhamP/Autism_Treatment_Assistance/blob/master/images/emotions_total.png?raw=true">
<img src="https://github.com/ParhamP/Autism_Treatment_Assistance/blob/master/images/matchness.png?raw=true">
<img src="https://github.com/ParhamP/Autism_Treatment_Assistance/blob/master/images/general_data.png?raw=true">
<img src="https://github.com/ParhamP/Autism_Treatment_Assistance/blob/master/images/emotions_matched.png?raw=true">
</p>

## History

Originally a hackathon project at PennApps, University of Pennsylvania, Winter 2017. Link to original project at Devpost: [Here](https://devpost.com/software/autism-treatment-assistance> "Here")

## Future of ATA

This project is still under improvement. The author is trying to collaborate with an actuall psychologist to improve the application.

## Thanks

I thank the people who conributed code and/or ideas:

[aalireza](https://github.com/aalireza> "aalireza")
