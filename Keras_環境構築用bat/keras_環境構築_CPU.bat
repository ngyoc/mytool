@echo off

title :: ���\�z Keras_CPU

set env_name=keras


title :: step 1/4 ���z���쐬��... env_name �y%env_name%�z
echo  :: step 1/4 ���z���쐬��... env_name �y%env_name%�z
echo y | call conda create -n %env_name% python=3.6.3 jupyter Pillow
title :: step 1/4 ���z���쐬����
echo  :: step 1/4 ���z���쐬����


echo  :: ���z���N��
title :: ���z���N��
call activate %env_name%

:: pause

echo  :: step 2/4 �y%env_name%�z keras �C���X�g�[����...
title :: step 2/4 �y%env_name%�z keras �C���X�g�[����...
call pip install keras
echo  :: step 2/4 �y%env_name%�z keras �C���X�g�[������
title :: step 2/4 �y%env_name%�z keras �C���X�g�[������

:: pause

echo  :: step 3/4 �y%env_name%�z tensorflow �C���X�g�[����...
title :: step 3/4 �y%env_name%�z tensorflow �C���X�g�[����...
call pip install tensorflow
echo  :: step 3/4 �y%env_name%�z tensorflow �C���X�g�[������
title :: step 3/4 �y%env_name%�z tensorflow �C���X�g�[������


echo  :: step 4/4 �y%env_name%�z sklearn �C���X�g�[����...
title :: step 4/4 �y%env_name%�z sklearn �C���X�g�[����...
call pip install sklearn
echo  :: step 4/4 �y%env_name%�z sklearn �C���X�g�[������
title :: step 4/4 �y%env_name%�z sklearn �C���X�g�[������

:: pause

title :: ���\�z �y%env_name%�z �쐬����
echo  :: ���\�z �y%env_name%�z �쐬����

pause


