FROM public.ecr.aws/lambda/python:3.9
COPY requirements.txt ./

#RUN yum -y check-update || { rc=$?; [ "$rc" -eq 100 ] && exit 0; exit "$rc"; }&& yum install libgl1
RUN yum install mesa-libGL -y
RUN python3.9 -m pip install pyheif -t .
RUN python3.9 -m pip install -r requirements.txt
COPY app.py ./
CMD ["app.lambda_handler"]


