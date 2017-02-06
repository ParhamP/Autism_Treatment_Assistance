from setuptools import setup


setup(
    name='Autism_Treatment_Assistance',
    packages=['Autism_Treatment_Assistance'],
    version='0.4',
    scripts=['Autism_Treatment_Assistance/ata'],
    description="Employs data science and deep learning to assist therapists treat a common autism symptom that involves interpretation and correlation of facial and speech emotions",
    long_description="Please visist Autism Treatment Assistance on Github: https://github.com/ParhamP/Autism_Treatment_Assistance",
    author='Parham Pourdavood',
    author_email='ppourdavood@gmail.com',
    url='https://github.com/ParhamP/Autism_Treatment_Assistance',
    download_url='https://github.com/ParhamP/Autism_Treatment_Assistance/tarball/0.1',
    keywords=['data science, emotion recognition, psychology, autism, speech emotion recognition'],  # arbitrary keywords
    classifiers=[],
    install_requires=['SimpleAudioIndexer', 'watson_developer_cloud',
                      'SpeechRecognition', 'matplotlib', 'numpy'],
    license="Apache-2.0"
)
