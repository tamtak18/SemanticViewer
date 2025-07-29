# 詳細設計書

---

## 1. 概要

本プログラムは、複数の観測データに対してカイ二乗検定を実施し、さらに簡易的なCHAID（Chi-squared Automatic Interaction Detector）アルゴリズムを用いた決定木の構築とその可視化を行うものです。  
Pythonの主要ライブラリである`scipy.stats`、`pandas`、`numpy`、`matplotlib`、`networkx`を活用しています。

---

## 2. 機能一覧

1. **カイ二乗検定の実施（複数例）**  
   - 2×2のクロス集計表に基づき、カイ二乗統計量、自由度、p値を計算し表示します。

2. **簡易CHAIDアルゴリズムによる分割評価**  
   - サンプルデータに対し、指定した特徴量とターゲット変数の関係をカイ二乗検定で評価します。

3. **CHAID決定木の構築と可視化**  
   - `networkx`を用いて決定木構造を作成し、`matplotlib`で日本語フォント対応のグラフを描画します。

---

## 3. 詳細設計

### 3.1 カイ二乗検定部分

#### 3.1.1 入力データ

- 2次元リスト `observed`  
  - 行：カテゴリ（例：高温・低温、明るい照明・暗い照明、カテゴリーA・B）  
  - 列：結果（例：ビール購入・非購入）

#### 3.1.2 処理手順

1. **行数・列数の取得**  
   - `num_rows = len(observed)`  
   - `num_columns = len(observed[0])`

2. **自由度の計算**  
   - `degrees_of_freedom = (num_rows - 1) * (num_columns - 1)`

3. **総計、行合計、列合計の計算**  
   - `total = sum([sum(row) for row in observed])`  
   - `row_totals = [sum(row) for row in observed]`  
   - `col_totals = [sum([observed[i][j] for i in range(num_rows)]) for j in range(num_columns)]`

4. **期待度数の計算**  
   - `expected[i][j] = (row_totals[i] * col_totals[j]) / total`

5. **カイ二乗統計量の計算**  
   - \(\chi^2 = \sum_{i,j} \frac{(O_{ij} - E_{ij})^2}{E_{ij}}\)

6. **p値の計算**  
   - `p_value = 1 - chi2.cdf(chi2_value, degrees_of_freedom)`

7. **結果の表示**  
   - カイ二乗値、自由度、p値をコンソールに出力

#### 3.1.3 出力例

```
カイ二乗値: 33.333333333333336
自由度: 1
p 値: 8.602325267042627e-09
```

---

### 3.2 簡易CHAIDアルゴリズム部分

#### 3.2.1 入力データ

- `pandas.DataFrame`形式のサンプルデータ  
  - カラム例：`年齢層`、`性別`、`購入回数`、`購入した`  
  - ターゲット変数「購入した」は0/1の数値に変換済み

#### 3.2.2 処理手順

1. **カイ二乗検定関数 `compute_chi2`**  
   - 引数：データフレーム、特徴量名、ターゲット変数名（デフォルトは「購入した」）  
   - 処理：`pd.crosstab`でクロス集計表を作成し、`chi2_contingency`でカイ二乗検定を実施  
   - 出力：カイ二乗値とp値

2. **CHAID決定木構築関数 `chaid_decision_tree`**  
   - 引数：データフレーム  
   - 処理：特徴量「購入回数」に対してカイ二乗検定を実施し、結果を辞書に格納  
   - 出力：分割結果の辞書（特徴量名をキーに、カイ二乗値とp値を格納）

3. **結果表示**  
   - 最適な分割として「購入回数」を表示（本実装では簡易的に1特徴量のみ）

#### 3.2.3 出力例

```
最適な分割は '購入回数' (chi2: 4.1234, p-value: 0.0423)
```

---

### 3.3 CHAID決定木の可視化部分

#### 3.3.1 使用ライブラリ

- `networkx`：グラフ構造の作成  
- `matplotlib`：グラフ描画  
- `matplotlib.font_manager`：日本語フォント設定

#### 3.3.2 日本語フォント設定

- Windows環境のメイリオフォントを指定  
- `jp_font = fm.FontProperties(fname='C:/Windows/Fonts/meiryo.ttc')`

#### 3.3.3 決定木構造の作成

- 有向グラフ `nx.DiGraph()`を作成  
- ルートノード：「購入回数」  
- 「購入回数」の値（0〜5）ごとに子ノードを作成  
- さらに「性別」（男性・女性）で分割した子ノードを作成  
- リーフノードとして「購入した」「購入しなかった」の予測ノードをランダムに追加

#### 3.3.4 ノードの階層的配置関数 `hierarchy_pos`

- 再帰的にノードの位置を計算し、階層的に配置  
- 横方向の間隔や中央位置をパラメータで調整可能  
- リーフノードの位置調整も実施（1回目のコードではリーフノードを左にずらす処理あり）

#### 3.3.5 グラフ描画関数 `visualize_decision_tree`

- ノードの位置を計算し、`nx.draw`でノードを描画  
- 日本語ラベルをノードの中心に表示（男性・女性ノードは斜め表示）  
- 図のタイトルに日本語フォントを適用  
- 図のサイズを大きめに設定し見やすく調整

#### 3.3.6 実行結果

- CHAID決定木の構造が階層的に表示され、各ノードに日本語のラベルが付与される

---

## 4. 変数一覧

| 変数名             | 型           | 説明                                       |
|--------------------|--------------|--------------------------------------------|
| observed           | list of list | 観測度数の2次元リスト                       |
| num_rows           | int          | 行数（カテゴリ数）                         |
| num_columns        | int          | 列数（結果のカテゴリ数）                   |
| degrees_of_freedom | int          | 自由度                                     |
| total              | int          | 総計（全観測度数の合計）                   |
| row_totals         | list of int  | 各行の合計                                 |
| col_totals         | list of int  | 各列の合計                                 |
| expected           | list of list | 期待度数の2次元リスト                       |
| chi2_value         | float        | カイ二乗統計量                             |
| p_value            | float        | p値（上側確率）                            |
| df                 | pandas.DataFrame | サンプルデータフレーム                     |
| jp_font            | FontProperties | 日本語フォント設定                         |
| splits             | dict         | CHAID分割結果を格納する辞書                 |
| G                  | nx.DiGraph   | 決定木のグラフオブジェクト                   |
| pos                | dict         | ノードの座標を格納する辞書                   |

---

## 5. 関数一覧

| 関数名                 | 引数                         | 戻り値               | 概要                                         |
|------------------------|------------------------------|----------------------|----------------------------------------------|
| `compute_chi2`         | data, feature, target='購入した' | (chi2, p)            | 指定特徴量とターゲットのカイ二乗検定を実施   |
| `chaid_decision_tree`  | data                         | splits (dict)        | 簡易的なCHAIDアルゴリズムで分割評価を実施    |
| `hierarchy_pos`        | G, root, vert_gap, vert_loc, xcenter, horizontal_spacing | pos (dict)           | グラフのノードを階層的に配置する座標計算     |
| `_hierarchy_pos`       | G, root, vert_gap, vert_loc, xcenter, horizontal_spacing, pos, parent | pos (dict)           | `hierarchy_pos`の再帰処理本体                 |
| `visualize_decision_tree` | なし                       | なし                 | CHAID決定木のグラフを描画し表示               |

---

## 6. 実行環境・前提条件

- Python 3.x  
- ライブラリ：`numpy`, `pandas`, `scipy`, `matplotlib`, `networkx`  
- Windows環境（日本語フォント設定がWindowsのメイリオフォントを想定）  
- フォントパスは環境に応じて適宜変更が必要

---

## 7. 補足・注意事項

- カイ二乗検定は2×2のクロス集計表を想定していますが、`chi2_contingency`は任意のサイズに対応可能です。  
- CHAIDアルゴリズムは本実装では非常に簡易的で、分割基準の最適化や複数段階の分割は実装されていません。  
- 決定木のリーフノードの予測ラベルはランダムに生成しているため、実際の予測結果とは異なります。  
- 日本語フォントの設定は環境依存のため、他OSの場合はフォントパスの変更が必要です。  
- グラフのノード位置調整は手動でパラメータを調整しているため、ノード数や構造が変わると再調整が必要になる可能性があります。

---

以上が本プログラムの詳細設計書となります。ご不明点や追加のご要望がございましたらお知らせください。