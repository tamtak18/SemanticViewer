# 詳細設計書

## 1. 概要
本プログラムは、サンプルデータを用いてCHAID（Chi-squared Automatic Interaction Detector）アルゴリズムの基本的な決定木分析を行い、その結果を視覚化することを目的としています。  
具体的には、年齢層（Age_Group）と購入意欲（Purchase_High, Purchase_Low）の関係をカイ二乗検定で評価し、最適な分割を決定した後、決定木の構造をグラフで表示します。

---

## 2. 使用ライブラリ
- `numpy`：数値計算用（本コード内では直接使用していませんが、将来的な拡張を想定）
- `pandas`：データ操作・管理用
- `scipy.stats`：統計検定（カイ二乗検定）用
- `matplotlib.pyplot`：グラフ描画用
- `networkx`：グラフ構造の作成・描画用

---

## 3. データ構造

### 3.1 サンプルデータ（DataFrame）
| Age_Group | Income_Level | Purchase_High | Purchase_Low |
|-----------|--------------|---------------|--------------|
| Young     | Low          | 10            | 40           |
| Young     | Medium       | 20            | 30           |
| Young     | High         | 30            | 20           |
| Middle    | Low          | 15            | 35           |
| Middle    | Medium       | 25            | 25           |
| Middle    | High         | 40            | 10           |
| Old       | Low          | 5             | 45           |
| Old       | Medium       | 10            | 40           |
| Old       | High         | 20            | 30           |

- `Age_Group`：年齢層（Young, Middle, Old）
- `Income_Level`：収入レベル（Low, Medium, High）
- `Purchase_High`：購入意欲が高い人数
- `Purchase_Low`：購入意欲が低い人数

---

## 4. 関数設計

### 4.1 `compute_chi2(data, feature, target_high, target_low)`
#### 機能
指定した特徴量（`feature`）と購入意欲の高低（`target_high`, `target_low`）の間でカイ二乗検定を実施し、検定統計量とp値を返します。

#### 入力
- `data`：pandas DataFrame、分析対象のデータセット
- `feature`：文字列、検定対象の特徴量のカラム名（例：'Age_Group'）
- `target_high`：文字列、購入意欲が高い人数のカラム名（例：'Purchase_High'）
- `target_low`：文字列、購入意欲が低い人数のカラム名（例：'Purchase_Low'）

#### 処理内容
1. `pd.crosstab`を用いて、`feature`と`target_high`・`target_low`のクロス集計表（分割表）を作成します。
2. `chi2_contingency`関数でカイ二乗検定を実施します。
3. カイ二乗統計量（chi2）とp値（p）を取得し、返却します。

#### 出力
- `chi2`：float、カイ二乗統計量
- `p`：float、p値

---

### 4.2 `chaid_decision_tree(data)`
#### 機能
CHAIDアルゴリズムの基本的な決定木の分割を行い、最適な分割特徴量のカイ二乗検定結果を取得します。

#### 入力
- `data`：pandas DataFrame、分析対象のデータセット

#### 処理内容
1. 空の辞書`splits`を初期化します。
2. 現状では`Age_Group`に対してのみ`compute_chi2`関数を呼び出し、カイ二乗検定を実施します。
3. 検定結果（カイ二乗統計量とp値）を`splits`に格納します。
4. 分割結果をコンソールに出力します。

#### 出力
- `splits`：辞書、特徴量名をキーに、カイ二乗統計量とp値を値に持つ形式  
  例：`{'Age_Group': {'chi2': 12.3456, 'p_value': 0.0012}}`

---

### 4.3 `visualize_decision_tree()`
#### 機能
CHAID決定木の構造をグラフとして視覚化します。

#### 入力
- なし（内部で固定のノードとエッジを定義）

#### 処理内容
1. 有向グラフ`DiGraph`を作成します。
2. ルートノードとして「Purchase Intention」を追加します。
3. ルートノードから「Young」「Middle」「Old」の3つの子ノードへエッジを追加します。
4. `spring_layout`でノードの配置を決定します。
5. `nx.draw`でノードとエッジを描画し、タイトルを設定します。
6. `plt.show()`でグラフを表示します。

#### 出力
- グラフウィンドウに決定木の構造を表示

---

## 5. メイン処理の流れ

1. サンプルデータをDataFrameとして定義します。
2. `chaid_decision_tree`関数を呼び出し、`Age_Group`に対するカイ二乗検定を実施します。
3. 検定結果をコンソールに出力します。
4. `visualize_decision_tree`関数を呼び出し、決定木の構造をグラフで表示します。

---

## 6. 注意事項・今後の拡張案

- 現状の`compute_chi2`関数は`pd.crosstab`の使い方が不適切であり、正しくクロス集計ができていません。  
  → `Purchase_High`と`Purchase_Low`は数値であり、カテゴリ変数ではないため、クロス集計の方法を見直す必要があります。  
- CHAIDアルゴリズムは複数の特徴量を比較し、最も有意な分割を選択することが一般的です。  
  → 今後は`Income_Level`など他の特徴量も検定し、最適な分割を自動で選択するロジックを追加することが望ましいです。  
- 決定木の視覚化は現在固定のノード構造ですが、実際の分割結果に基づいて動的にノード・エッジを生成する機能を追加するとより実用的です。  
- データの前処理やエラーハンドリングが未実装のため、実運用時には追加が必要です。

---

以上が本プログラムの詳細設計書となります。ご不明点や追加のご要望がございましたらお知らせください。