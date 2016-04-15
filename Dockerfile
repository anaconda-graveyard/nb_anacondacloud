FROM continuumio/miniconda
COPY environment.yml /opt/nb_anacondcloud/
WORKDIR /opt/nb_anacondcloud
RUN conda env update
COPY . /opt/nb_anacondcloud/
RUN conda install -yn root conda-build
RUN conda build conda.recipe -c anaconda-nb-extensions \
  -c anaconda-nb-extensions/label/dev \
  -c javascript \
  -c mutirri \
  -c jakirkham \
  -c bokeh \
  -c cpcloud \
  -c auto
