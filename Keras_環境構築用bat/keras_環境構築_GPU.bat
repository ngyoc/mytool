@echo off

title :: 環境構築 Keras_GPU

set env_name=keras_gpu


title :: step 1/4 仮想環境作成中... env_name 【%env_name%】
echo  :: step 1/4 仮想環境作成中... env_name 【%env_name%】

echo y | call conda create -n %env_name% python=3.6.3 jupyter Pillow

title :: step 1/4 仮想環境作成完了
echo  :: step 1/4 仮想環境作成完了


echo  :: 仮想環境起動
title :: 仮想環境起動
call activate %env_name%

:: pause

echo  :: step 2/4 【%env_name%】 tensorflow-gpu インストール中...
title :: step 2/4 【%env_name%】 tensorflow-gpu インストール中...
echo y | call conda install -n %env_name% tensorflow-gpu
echo y | call conda install -n %env_name% cudatoolkit==9.0
echo  :: step 2/4 【%env_name%】 tensorflow-gpu インストール完了
title :: step 2/4 【%env_name%】 tensorflow-gpu インストール完了

:: pause

echo  :: step 3/4 【%env_name%】 keras インストール中...
title :: step 3/4 【%env_name%】 keras インストール中...
echo y | call conda install -n %env_name% keras
echo  :: step 3/4 【%env_name%】 keras インストール完了
title :: step 3/4 【%env_name%】 keras インストール完了

:: pause

echo  :: step 4/4 【%env_name%】 sklearn インストール中...
title :: step 4/4 【%env_name%】 sklearn インストール中...
call pip install sklearn
echo  :: step 4/4 【%env_name%】 sklearn インストール完了
title :: step 4/4 【%env_name%】 sklearn インストール完了

:: pause

title :: 環境構築 【%env_name%】 作成完了
echo  :: 環境構築 【%env_name%】 作成完了

pause


