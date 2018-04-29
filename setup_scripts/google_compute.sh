# create from instance gpu-template (1 min)
# - https://console.cloud.google.com/compute/instanceTemplates/list?project=mnist-cnn-195807
# - select us-east1-c

sudo apt-get update
sudo apt-get -y upgrade \
&& sudo apt-get install -y python-pip python-dev

# run startup script
sudo curl -O https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
sudo dpkg -i ./cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
sudo apt-get update
sudo apt-get install cuda-8-0 -y

# install python 2.7 and tensorflow
# pip install cuda-9-0
# wget https://www.dropbox.com/s/52zoz2ze3b58d12/cudnn-9.0-linux-x64-v7.solitairetheme8

# install anaconda
wget https://repo.continuum.io/archive/Anaconda2-5.1.0-Linux-x86_64.sh
echo "
q
yes
no" > yess.txt
sh Anaconda2-5.1.0-Linux-x86_64.sh

source ~/.bashrc
echo "yes" > yes.txt
conda create -n tensorflow pip python=2.7 < yes.txt
source activate tensorflow

pip install --ignore-installed --upgrade https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow_gpu-1.5.0-cp27-none-linux_x86_64.whl
#pip install --upgrade tensorflow-gpu==1.4



# send this over, copy usr directory
wget https://www.dropbox.com/s/uhmcp9ril7pzgpc/libcudnn7_7.0.5.15-1%2Bcuda9.0_amd64.deb
sudo dpkg -x libcudnn7_7.0.5.15-1+cuda9.0_amd64.deb libcudnn7_cuda9

sudo cp -r libcudnn7_cuda9/usr/lib/* /usr/lib/
sudo cp -r libcudnn7_cuda9/usr/share/* /usr/share/

export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64"

wget https://developer.nvidia.com/compute/cuda/9.0/Prod/local_installers/cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb
sudo dpkg -i cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb
sudo apt-key adv --fetch-keys \
http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
sudo apt-get update
echo "y" > y.txt
sudo apt-get install cuda-9-0 < y.txt

# conda install packages
conda install -c menpo dlib -y
conda install numpy -y 
conda install opencv -y
conda install -c mlgill imutils -y
conda install -c conda-forge matplotlib -y
conda install pillow -y
conda install sympy -y
conda install -c anaconda scikit-image -y