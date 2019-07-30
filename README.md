# mytool
2019/07/24
公開してもいいプログラム
自分用

## gen_run_python
.pyを実行するための.batを作成する

### 使い方
1. 実行したい.pyファイルをgen_run_python_bat.batにD&D
2. .pyファイルと同じ階層に同名のバッチファイルが生成される
3. バッチファイル実行して幸せ


## Keras_環境構築用bat

### 前提
- Anaconda
- condaコマンドが使える事

### ファイル
- Kerasインストール状況確認用bat
- 仮想環境構築用bat * 2
- 仮想環境削除用bat

### 使い方
1. keras_環境構築_CPU(or _GPU).batを実行
2. 環境に合わせてCUDA, cudnnをインストール


## VLC_rec_start_bat

### 前提
- デフォルトの場所にVLCメディアプレーヤーがインストール済み
- Windows

### ファイル
- 定期的に呼び出す側のbat(▶run_rec.bat)
- 定期的に呼び出される側のbat(rec.bat)

### 使い方
1. 録画開始時刻、録画秒数などのパラメーターを指定
2. ▶run_rec.batを実行
