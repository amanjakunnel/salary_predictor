from typing import Dict

from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfile 
import time

from doc_ai_trial import *

from tkinter.filedialog import askopenfile 
import time

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="key.json"

project_id = "gcp-summer-2022-1-356703"
location_proc = 'us'           
file_path = 'Resume.pdf'    

processor_id = '2a9f4fa0572cb604'

from tkinter import *  
import pandas as pd

from google.cloud import documentai_v1beta3 as documentai

#import gcp_backend


df = pd.read_csv("companyMapping.csv")
#import gcp_backend


def open_file():
    file_path = askopenfile(mode='r', filetypes=[('PDF', '*pdf')])
    if file_path is not None:
        pass
    file_path = (file_path.name)


def uploadFiles():
    pb1 = Progressbar(
        top, 
        orient=HORIZONTAL, 
        length=300, 
        mode='determinate'
        )
    pb1.grid(row=4, columnspan=3, pady=20)
    for i in range(5):
        top.update_idletasks()
        pb1['value'] += 20
        time.sleep(1)
    pb1.destroy()
    Label(top, text='File Uploaded Successfully!', foreground='green').grid(row=4, columnspan=3, pady=10)
    
    






def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    # print(response)
    return response







def process_document_sample(
    project_id: str, location: str, processor_id: str, file_path: str
):
    from google.cloud import documentai_v1beta3 as documentai
    from google.api_core.client_options import ClientOptions

    # Set endpoint to EU
    # options = ClientOptions(api_endpoint="eu-documentai.googleapis.com:443")
    # Instantiates a client
    client = documentai.DocumentProcessorServiceClient()

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    with open(file_path, "rb") as image:
        image_content = image.read()

    # Read the file into memory
    document = {"content": image_content, "mime_type": "application/pdf"}

    # Configure the process request
    request = {"name": name, "document": document}

    # Recognizes text entities in the PDF document
    result = client.process_document(request=request)

    document = result.document

    print("Document processing complete.")

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

    document_pages = document.pages

    my_dict = {}

    # Read the text recognition output from the processor
    print("The document contains the following paragraphs:")
    for page in document_pages:
        paragraphs = page.paragraphs
        for paragraph in paragraphs:
            paragraph_text = get_text(paragraph.layout, document)
            paragraph_text_list = paragraph_text.split(": ")
            paragraph_text_list = [s.rstrip() for s in paragraph_text_list]
            #print(paragraph_text_list)
            if len(paragraph_text_list)>1:
                my_dict[paragraph_text_list[0]] = paragraph_text_list[1]
    # print(my_dict)
     
    return my_dict       
            # print(f"Paragraph text: {paragraph_text}")
            





def predict_tabular_classification_sample(
    project: str,
    endpoint_id: str,
    instance_dict: Dict,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    # for more info on the instance schema, please use get_model_sample.py
    # and look at the yaml found in instance_schema_uri
    instance = json_format.ParseDict(instance_dict, Value())
    instances = [instance]
    parameters_dict = {}
    parameters = json_format.ParseDict(parameters_dict, Value())
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/tabular_classification_1.0.0.yaml for the format of the predictions.
    predictions = response.predictions
    for prediction in predictions:
        print(" prediction:", dict(prediction))



#tkinter code

resume_dict = process_document_sample(project_id, location_proc, processor_id, file_path)
print(resume_dict)

top = Tk()  
  
top.geometry("600x450")  
  
  
  
job_description_box = Label(top, text = "Job Description").grid(row=1, column=1)
  

    

  
e2 = Entry(top)
e2.grid(row=1, column=2) 

adhar = Label(
    top, 
    text='Upload Resume in PDF format'
    )
adhar.grid(row=2, column=0, padx=10)

adharbtn = Button(
    top, 
    text ='Choose File', 
    command = lambda:open_file()
    ) 
adharbtn.grid(row=2, column=1)

upld = Button(
    top, 
    text='Upload Files', 
    command=uploadFiles
    )
upld.grid(row=3, columnspan=3, pady=10)
  
  

def button_invoked():
    
    
    global job_title, job_description, company_name, location
    job_title = resume_dict['Job Title']
    job_description = e2.get()
    company_name = resume_dict['Company']
    location = resume_dict['Location']
    cname, headquarters, size, type_of_ownership, industry, sector = df[df['Company Name']==company_name].values.tolist()[0]
    #cname = query(cname)
    inputs_dict = {"job_title": job_title, "job_description":job_description, "company_name":company_name, "location":location, "headquarters":headquarters, "size":size, "type_of_ownership":type_of_ownership, "industry":industry, "sector":sector}
    
    predict_tabular_classification_sample(
        project = "21707064905",
        endpoint_id = "1628112837945589760",
        instance_dict = inputs_dict,
        location = "us-central1"
    )

    
    
    

sbmitbtn = Button(top, text = "Submit",activebackground = "pink", activeforeground = "blue", command=button_invoked).grid(row=4)  
top.mainloop()
top.mainloop()



