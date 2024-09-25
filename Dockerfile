FROM python:3.10

RUN pip install --upgrade pip

WORKDIR /app

RUN pip install streamlit-img-label pascal_voc_writer streamlit google-api-python-client google-cloud-aiplatform google-cloud-storage google-cloud-vision numpy pycocotools opencv-python-headless

COPY Main.py .
COPY images.zip .

CMD streamlit run Main.py --server.port=8080 --server.enableXsrfProtection=false