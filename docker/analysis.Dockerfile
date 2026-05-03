FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV RETICULATE_PYTHON=/usr/bin/python3

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        r-base \
        r-base-dev \
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
        r-cran-data.table \
        r-cran-matrix \
        r-cran-survival \
        r-cran-reticulate \
        r-cran-optparse \
        r-cran-dplyr \
        r-cran-readr \
        r-cran-stringr \
        r-cran-corpcor \
        r-cran-doparallel \
        r-cran-foreach \
        r-cran-irlba \
        r-cran-qqman \
        r-cran-remotes \
        python3-numpy \
        python3-numba \
        python3-pandas \
    && rm -rf /var/lib/apt/lists/*

RUN R -q -e "options(timeout = 600, repos = c(CRAN = 'https://cloud.r-project.org')); install.packages(c('bigsnpr', 'SKAT', 'SPAtest', 'CompQuadForm', 'matrixsampling', 'GhostKnockoff'), dependencies = c('Depends', 'Imports', 'LinkingTo'))"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cmake \
        cargo \
        rustc \
        libsqlite3-dev \
        python3-dev \
    && mkdir -p /usr/lib/R \
    && ln -sfn /usr/share/R/include /usr/lib/R/include \
    && rm -rf /var/lib/apt/lists/*

RUN R -q -e "options(timeout = 600, repos = c(CRAN = 'https://cloud.r-project.org')); remotes::install_github('cran/GhostKnockoff', upgrade = 'never', dependencies = c('Depends', 'Imports', 'LinkingTo')); stopifnot(requireNamespace('GhostKnockoff', quietly = TRUE))"

# Keep command-line Python aligned with reticulate and Debian-installed packages.
RUN ln -sf /usr/bin/python3 /usr/local/bin/python3

RUN R -q -e "options(timeout = 600, repos = c(CRAN = 'https://cloud.r-project.org')); if (!requireNamespace('BiocManager', quietly = TRUE)) install.packages('BiocManager', dependencies = c('Depends', 'Imports', 'LinkingTo')); BiocManager::install(c('snpStats', 'graph', 'MatrixGenerics'), ask = FALSE, update = FALSE); remotes::install_github('shiyangm/LAVA-Knock', upgrade = 'never', dependencies = c('Depends', 'Imports', 'LinkingTo')); stopifnot(requireNamespace('snpStats', quietly = TRUE), requireNamespace('LAVAKnock', quietly = TRUE))"

WORKDIR /workspace/analysis

RUN mkdir -p /workspace/analysis /workspace/analysis/data /workspace/analysis/results

CMD ["bash"]
