# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 14:13:07 2024

@author: sayan
"""

import os
from google.cloud import texttospeech   #This module also needs to be installed before running this code
import PyPDF2                            #This library needs to be installed before running this code, it is used to extract text from given pdf
from google.cloud import storage



def take_User_pdf():

    """ 
    This function takes file path of the pdf, then verifies:
    1. If the file exists and can be accessed by the code or not.
    2. If the file exists, then whether it is a pdf file or not.
    3. Whether pdf file is less than 5 Mb or not, this is a constraint.

    In case any of the above consitions are failed to be fulfilled, it prompts the user to try again with the valid file path.

    The function also returns the pdf file path and the file path where the mp3 file is to be saved.
    By default, the mp3 file will have the same name as the pdf file and will be saved in the same location.

    The function returns the file path of the pdf as pdf_path, and the file path of the mp3 file as svae_directory.
    """
    #One can call another api here to take file_path, no need to take user input.
    pdf_path = input("Please enter the file path of the pdf: ")      
    file_name = os.path.basename(pdf_path)
    directory = os.path.dirname(pdf_path)
    file_name, file_extension = os.path.splitext(file_name)

    output_file=file_name+".mp3"
    save_directory=os.path.join(directory, output_file)
    
    #Checks if the file exists and can be accessed by the code or not.
    try:                                                                   
        pdf_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)        
    except Exception as error:
        print("Error: {}\n Please try again".format(error))
        #recursive calling
        pdf_path, save_directory=take_user_pdf()
    #Checks if the file exists, then whether it is a pdf file or not.
    if file_extension!=".pdf":
        print("Only pdf formats are supported, please try again.")
        #recursive calling
        pdf_path, save_directory=take_user_pdf()
    #Whether pdf file is less than 5 Mb or not, this is a constraint.
    if pdf_size_mb > 5:
        print("PDF file size exceeds the maximum limit of 5 MB.\n PLease try again.")
        #recursive calling
        pdf_path, save_directory=take_user_pdf()

    return pdf_path, save_directory,output_file


def verify_pdf_pages(pdf_path, pages=[]):
    
    """
    Verify if the specified pages are present in the given PDF file and return the valid pages.

    Parameters:
    pdf_path (str): The path to the PDF file.
    pages (list): A list of page numbers to be verified.

    Returns:
    list: A list of valid page numbers within the range of the PDF.

    Description:
    This function takes a list of page numbers and a PDF file path as inputs. 
    It verifies if the pages are within the range of the total pages in the PDF. If the list of pages is empty, 
    the function will print a message indicating that the entire PDF will be converted to audio and return the 
    original empty list. If any page number is outside the valid range, it will be removed from the list, 
    and a message will be printed indicating the removal. 
    The function returns either a list of valid page numbers that are within the PDF's range or an empty list, 
    in which case the whole pdf will be converted to an audio file.

    Notes:
    - The function uses the PyPDF2 library to read the PDF file. Make sure PyPDF2 is installed.
    - Page numbers should positive integers.

    Example:
    >>> pdf_path = "path/to/your/pdf_file.pdf"
    >>> pages = [1, 2, 3, 10, 50]
    >>> valid_pages = verify_pdf_pages(pdf_path, pages)
    >>> print("Valid pages:", valid_pages)
    """

    #if list is empty, then whole pdf is passed to be sythesized as audio
    if pages==[]:
        print("List is empty, the entire pdf will be converted to an audio file.")
        return pages

    # Open the PDF file
    pdf_file=open(pdf_path, "rb") 
    reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(reader.pages)
    final_pages=pages.copy()        
    
    # Verify if the pages are in the given PDF
    for page in pages:
        print("page ",page)
        if page < 1 or page > total_pages:
            print("Page {} is not in the given PDF and will be removed from page list. The PDF has {} pages.".format(page,total_pages))
            final_pages.remove(page)
            print("page removed")
    return final_pages


def extract_text_from_pdf(path,pages=[]):

    """
    Extract text from specified pages of a PDF file or from all pages if no pages are specified.

    Parameters:
    path (str): The path to the PDF file.
    pages (list, optional): A list of page numbers from which text will be extracted. Default is an empty list.

    Returns:
    str: The extracted text from the specified pages or from all pages if no pages are specified.

    Description:
    This function extracts text from specified pages of a PDF file or from all pages if no pages are specified. 
    If the list of pages is empty, text is extracted from all pages of the PDF. 
    If specific pages are provided, text is extracted from those pages only. 
    The function returns the extracted text as a single string.

    Notes:
    - The function uses the PyPDF2 library to read the PDF file. Make sure PyPDF2 is installed.
    """

    #opens the pdf file from path
    text = ""
    file=open(path, "rb")
    reader = PyPDF2.PdfReader(file)
    
    #If page list is empty, extracts text from the entire pdf
    if len(pages)==0:
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    #if page list is not empty, extracts texts from those pages only
    else:
        for page_num in pages:
            text += reader.pages[page_num].extract_text()
    file.close()
    
    return text

"""
    Customize the speech style
    for list of supported languages and voices, 
    visit:https://cloud.google.com/text-to-speech/docs/voices
""" 

def synthesize_speech(text, output_file,location, output_gcs_uri, output_file_name, language_code='en-GB', voice_name='en-GB-Standard-B', speaking_rate=1.0, pitch=0.0):
    
    """
    Synthesize speech from text and save it to an audio file.

    Parameters:
    text (str): The text to be synthesized into speech.
    output_file (str): The path to save the synthesized audio file.
    output_gcs_uri(str): To store audio file in google cloud bucket.
    location(str): geographical location of user.
    output_file_name(str):Name of audio file.
    language_code (str, optional): The language code of the text. Default is 'en-GB' (British English).
    voice_name (str, optional): The voice name to be used for synthesis. Default is 'en-GB-Standard-B'.
    speaking_rate (float, optional): The speaking rate. Default is 1.0 (normal speed).
    pitch (float, optional): The pitch adjustment for the synthesized speech. Default is 0.0 (normal pitch).

    Returns:
    None

    Description:
    This function synthesizes speech from the provided text using the specified language, voice, speaking rate, and pitch settings.
    The synthesized audio is saved to the specified output file path.
    The function uses the Google Cloud Text-to-Speech API for synthesis.

    Notes:
    - You need to have a Google Cloud Platform account and Text-to-Speech API enabled.
    - Install the 'google-cloud-texttospeech' package before using this function.
    - The output file will be in MP3 format.
    - The function will print a message indicating the completion of audio synthesis.

    """
    
    #This is my project id on google cloud, needs to be changed accordingly.
    project_id = "textpdf-425312"   
    
    #initializes a client that can be used to interact with the Google Cloud Text-to-Speech API, make sure your have proper ADC to authenticate
    client = texttospeech.TextToSpeechLongAudioSynthesizeClient()              
    synthesis_input =texttospeech.SynthesisInput(text=text)
    
    #initializing an object to specify the voice that will be used for synthesizing speech.
    voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)

    #initializing an object to specify the audio configuration.
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, speaking_rate=speaking_rate, pitch=pitch)

    parent = "projects/{}/locations/{}".format(project_id, location)

    request = texttospeech.SynthesizeLongAudioRequest(parent=parent, input=synthesis_input, audio_config=audio_config, voice=voice, output_gcs_uri=output_gcs_uri)
    
    print("PLease wait while file is being processed...")
   
    operation = client.synthesize_long_audio(request=request)
   
    # Set a deadline for your LRO to finish. This can be adjusted depending on the length of the input, initially set 5 minutes
    result = operation.result(timeout=300)
    print("Finished processing.\n Result(should be blank): ", result)

    # To download the mp3 file from a bucket in my google clouad, your need to replace this with  yours
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket("trial_txt_seech")
    blob = bucket.blob(output_file_name)
    blob.download_to_filename(output_file)



def main(language_code='en-GB', voice_name='en-GB-Standard-B', speaking_rate=1.0, pitch=0.0):

    #store file path of pdf,mp3 file respectively along with the file name
    pdf_path,save_path, file_name=take_User_pdf()
    
    #This right here points to the bucket under the project in google cloud account, set this to your own for adc verification
    output_gcs_uri='gs://trial_txt_seech/{}'.format(file_name)
    location='asia-south1'
    
    #Default is an empty pages list, to convert the entire pdf, add pages to here
    pages=[]
    
    #If pages are added to list, check their validity in pdf
    pages=verify_pdf_pages(pdf_path, pages)

    #extract text from pdf, or pages in pdf
    ext_text=extract_text_from_pdf(pdf_path,pages)

    #check if text is extracted or not, if it's not extracted print a message and exit
    if(ext_text is None or ext_text==""):
        print("No Text was extracted from given pdf file.")
        return False
    
    #to synthesize speech from google's api and save mp3 file, parameters are present to customize speech style
    synthesize_speech(ext_text, save_path,location, output_gcs_uri, file_name, language_code, voice_name, speaking_rate, pitch)
    return True

if __name__ == '__main__':

    #default is male, british english, can pass the customizing parameter here.
    language = 'en-GB'  # Language code
    voice = 'en-GB-Standard-B'  # Voice name
    speaking_speed = 1.0  # Speed of speech
    pitch_ = 0.0  # Pitch adjustment
    

    main(language, voice, speaking_speed, pitch_)
    