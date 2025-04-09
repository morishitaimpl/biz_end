import sys
sys.dont_write_bytecode = True
import math

import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
from torchvision import models

# 画像の一辺のサイズ (この大きさにリサイズされるので要確認)
cellSize = 384

# クラス全体の数
classesSize = 3

# 繰り返す回数
epochSize = 10

# ミニバッチのサイズ
batchSize = 5

# 学習時のサンプルを学習：検証データに分ける学習側の割合
splitRateTrain = 0.8


# データ変換
data_transforms = T.Compose([
    T.Resize(int(cellSize * 1.2)),
    T.RandomRotation(degrees = 15),
    T.RandomApply([T.GaussianBlur(5, sigma = (0.1, 5.0))], p = 0.5),
    T.ColorJitter(brightness = 0.5, contrast = 0.5, saturation = 0.5, hue = [-0.2, 0.2]), 
    T.RandomHorizontalFlip(0.5),
    T.CenterCrop(cellSize),
    T.ToTensor(),
    # T.RandomErasing(p=0.5, scale=(0.02, 0.33), ratio=(0.3, 3.3))
    ])

def calc_acc(output, label): # 結果が一致するラベルの数をカウントする
    p_arg = torch.argmax(output, dim = 1)
    return torch.sum(label == p_arg)

class build_model(nn.Module):
    def __init__(self):
        super(build_model, self).__init__()
        self.model_pre = models.efficientnet_v2_s(weights = models.EfficientNet_V2_S_Weights.DEFAULT)
        self.bn = nn.BatchNorm1d(1000)
        self.dropout = nn.Dropout(0.3) #0.5から0.3に変更
        self.classifier = nn.Linear(1000, classesSize)

    def forward(self, input):
        mid_features = self.model_pre(input)
        x = self.bn(mid_features) # BNを追加
        x = self.dropout(x) # dropoutを追加
        x = self.classifier(x)
        return x



if __name__ == "__main__":
    import os
    from torchinfo import summary
    from torchviz import make_dot

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(DEVICE)

    mdl = build_model()
    print(mdl)
    summary(mdl, (batchSize, 3, cellSize, cellSize))
    
    x = torch.randn(batchSize, 3, cellSize, cellSize).to(DEVICE) # 適当な入力
    y = mdl(x) # その出力
    
    img = make_dot(y, params = dict(mdl.named_parameters())) # 計算グラフの表示
    img.format = "png"
    img.render("_model_graph") # グラフを画像に保存
    os.remove("_model_graph") # 拡張子無しのファイルもできるので個別に削除