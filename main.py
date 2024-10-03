import subprocess
from typing import Any, List
import csv, json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from customexceptions import SubProcessException
import logging

app = FastAPI()

# Need to implement middleware and allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# bash command to up server: uvicorn main:app --host 0.0.0.0 --reload
# --host 0.0.0.0 is to bind server to all network interfaces

def analyze_images():
    # bash_command = ["./install_x86_64_linux/Release/bin/OFIQSampleApp","-c","data/ofiq_config.jaxn","-i ","testimage/b-01-smile.png","-o","results.csv"] 
    bash_command = ['./OFIQ-Project/install_x86_64_linux//Release//bin//OFIQSampleApp', '-c', 'OFIQ-Project/data/ofiq_config.jaxn', '-i', 'OFIQ-Project/data/tests/images/b-01-smile.png', '-o', 'results.csv'] 
    # bash_command = ['./OFIQ-Project/install_x86_64_linux//Release//bin//OFIQSampleApp', '-c', 'data/ofiq_config.jaxn', '-i', 'OFIQ-Project/data/tests/images/b-01-smile.png', '-o', 'results.csv'] 

    # Below code lines using Popen to stream output as process is running
    # Start a process and interact with it
    # result = subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # for line in result.stdout:
    #     print(line.decode().strip())
    
    # Use this for normal run
    result = subprocess.run(bash_command,capture_output=True,text=True)
    print(f"{result.returncode}:",result.stderr)
    logging.error(f"Subprocess error: {result.returncode}: {result.stderr}")
    if result.returncode != 0:
       raise SubProcessException(           
           error_message=f"{result.stderr}"
       )
    

@app.exception_handler(SubProcessException)
async def subprocess_exception_handling(request: Request, exc: SubProcessException):
    
    return JSONResponse(status_code=401,
                        content={"message":exc.error_message}
                        )      
      
def read_results() -> List:
    # # Read output line by line
    # for line in process.stdout:
    #     print(line.decode().strip())  # Decode bytes to string
    with open('results.csv','r') as file:
        data_dict = csv.DictReader(file,delimiter=';')
        data_list = [row for row in data_dict]
    
    return data_list
    
@app.get("/getresults")
def getResults():
    try:
        analyze_images()
        data = read_results()
        return JSONResponse(status_code=200,
                            content=data
                            )
    except SubProcessException as e:
        raise e #must reraise e to show error message

# Below is to facilitate code testing locally
if __name__=="__main__":
    analyze_images()
    data = read_results()
    print(data)

