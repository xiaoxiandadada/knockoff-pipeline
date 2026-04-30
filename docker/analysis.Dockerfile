FROM rocker/r-ver:4.4.1

ENV DEBIAN_FRONTEND=noninteractive
ENV RETICULATE_PYTHON=/usr/bin/python3

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        gfortran \
        git \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        libgit2-dev \
        libblas-dev \
        liblapack-dev \
        libfontconfig1-dev \
        libfreetype6-dev \
        libpng-dev \
        libtiff5-dev \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages \
    numpy \
    numba \
    pandas

RUN R -q -e "options(repos = c(CRAN = 'https://cloud.r-project.org')); install.packages(c('data.table', 'Matrix', 'survival', 'reticulate', 'optparse', 'bigsnpr', 'dplyr', 'readr', 'corpcor', 'SKAT', 'SPAtest', 'CompQuadForm', 'irlba', 'matrixsampling', 'qqman', 'remotes', 'BiocManager'))"
RUN R -q -e "BiocManager::install(c('snpStats', 'graph', 'MatrixGenerics'), ask = FALSE, update = FALSE)"
RUN R -q -e "remotes::install_github('shiyangm/LAVA-Knock', upgrade = 'never', dependencies = TRUE)"
RUN R -q -e "options(repos = c(CRAN = 'https://cloud.r-project.org')); install.packages('GhostKnockoff')"

WORKDIR /workspace/analysis

RUN mkdir -p /workspace/analysis /workspace/analysis/data /workspace/analysis/results

CMD ["bash"]
