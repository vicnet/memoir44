# docker build -t tensorflow:vo .
# docker run -it --rm -u $(id -u):$(id -g) -v $PWD:/tmp tensorflow:vo bash
# avec display
# docker run -it --rm -u $(id -u):$(id -g) -v $PWD:/tmp -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix tensorflow:vo bash

FROM tensorflow/tensorflow:latest

# Installation des modules Python
RUN pip install Pillow
RUN pip install matplotlib
#RUN pip install tkinter
RUN apt update
RUN apt install -y python3-tk

ENV PATH=".:${PATH}"

WORKDIR /tmp

CMD ["bash"]
