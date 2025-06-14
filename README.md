# EnglishToGerman
Project on English to German Translation
Step 1 : Clone github repository


Step 2 : 
# create virtual enn and activate
python -m venv virtualEnv
.\virtualEnv\Scripts\activate

Step 2 :
# Create Secreat file and write contents like username and password api_key into that file
mkdir .streamlit
code .streamlit/secrets.toml

# install required libraries inside ur virtual env
should have python 3.10
python.exe -m pip install --upgrade pip
pip install streamlit
pip install google-generativeai
pip install gtts
pip install streamlit-webrtc openai-whisper soundfile
pip install grpcio==1.48.2
pip install "pydantic<2"
pip install pyarrow
Step 4 :
# create a login page
