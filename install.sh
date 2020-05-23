#!/bin/bash
#TODO make this versionless
python3 -m pip install -r requirements.txt
chessboard_version=1.0.0
curl https://chessboardjs.com/releases/chessboardjs-${chessboard_version}.zip --output chessboardjs-${chessboard_version}.zip
mkdir chessboardjs
unzip chessboardjs-${chessboard_version}.zip -d chessboardjs
rm chessboardjs-${chessboard_version}.zip
cp -r chessboardjs/img .
rm -rf chessboardjs

