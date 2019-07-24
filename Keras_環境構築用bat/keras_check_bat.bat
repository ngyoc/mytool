nvcc -V

call conda list tensorflow
call conda list keras
call conda list cudatoolkit
call conda list cudnn

call activate keras-gpu
call conda list tensorflow
call conda list keras
call conda list cudatoolkit
call conda list cudnn

pause
