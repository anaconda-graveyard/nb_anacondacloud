FROM continuumio/miniconda
ENV LC_ALL=C

RUN apt-get update --fix-missing \
  && apt-get install -y libfreetype6 \
  && apt-get clean

RUN conda install -yn root conda-build==1.20.0

WORKDIR /opt/nb_anacondcloud
RUN conda env update

COPY . /opt/nb_anacondcloud/
RUN conda build conda.recipe \
  -c anaconda-nb-extensions \
  -c anaconda-nb-extensions/label/dev \
  -c javascript \
  -c mutirri \
  -c jakirkham \
  -c bokeh \
  -c cpcloud \
  -c auto
