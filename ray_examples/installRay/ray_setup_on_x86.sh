#tag::install[]
conda create -n ray python=3.7  mamba -y
conda activate ray
# In a conda env this won't be auto-installed with ray so add them
pip install jinja2 python-dateutil cloudpickle packaging pygments \
    psutil nbconvert ray
#end::install[]
