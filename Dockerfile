FROM python:3.10

EXPOSE 8080

COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt 

COPY index.html /usr/local/lib/python3.10/site-packages/streamlit/static/index.html
COPY favicon.png /usr/local/lib/python3.10/site-packages/streamlit/static/favicon.png
COPY app.py app.py
COPY functions.py functions.py
COPY Text Text
COPY .streamlit .streamlit
COPY Backend/imp_minmax.csv Backend/imp_minmax.csv
COPY Backend/df_stack.csv Backend/df_stack.csv
RUN find /usr/local/lib/python3.10/site-packages/streamlit -type f \( -iname \*.py -o -iname \*.js \) -print0 | xargs -0 sed -i 's/healthz/health-check/g'
WORKDIR .

ENTRYPOINT [ "streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false"]




