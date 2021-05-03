# Specialization_theChain


For running on google colab

1. 
!git clone -b main --single-branch https://github.com/sanketshahc/Specialization_theChain.git

2. 
%%bash
MINICONDA_INSTALLER_SCRIPT=Miniconda3-4.5.4-Linux-x86_64.sh
MINICONDA_PREFIX=/usr/local
wget https://repo.continuum.io/miniconda/$MINICONDA_INSTALLER_SCRIPT
chmod +x $MINICONDA_INSTALLER_SCRIPT
./$MINICONDA_INSTALLER_SCRIPT -b -f -p $MINICONDA_PREFIX

3. 
!cd Specialization_theChain/;conda env create --file gerry.yml
