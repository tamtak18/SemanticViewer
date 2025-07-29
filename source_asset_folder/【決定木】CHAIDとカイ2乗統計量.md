```python
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import networkx as nx

# サンプルデータの設定：年齢層と購入意欲
data = pd.DataFrame({
    'Age_Group': ['Young', 'Young', 'Young', 'Middle', 'Middle', 'Middle', 'Old', 'Old', 'Old'],
    'Income_Level': ['Low', 'Medium', 'High', 'Low', 'Medium', 'High', 'Low', 'Medium', 'High'],
    'Purchase_High': [10, 20, 30, 15, 25, 40, 5, 10, 20],
    'Purchase_Low': [40, 30, 20, 35, 25, 10, 45, 40, 30]
})

# カイ二乗検定を行う関数
def compute_chi2(data, feature, target_high, target_low):
    contingency_table = pd.crosstab(data[feature], [data[target_high], data[target_low]])
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    return chi2, p

# CHAIDの基本的な決定木アルゴリズム
def chaid_decision_tree(data):
    splits = {}
    
    # カイ二乗検定をAge_Groupに対して実施
    chi2_age, p_age = compute_chi2(data, 'Age_Group', 'Purchase_High', 'Purchase_Low')
    splits['Age_Group'] = {'chi2': chi2_age, 'p_value': p_age}
    
    # 結果を出力
    print(f"Best split at 'Age_Group' with chi2: {chi2_age:.4f} and p-value: {p_age:.4f}")
    
    return splits

# 決定木を視覚化する関数
def visualize_decision_tree():
    G = nx.DiGraph()
    
    # ノードの追加
    G.add_node("Purchase Intention")
    G.add_edges_from([("Purchase Intention", "Young"), ("Purchase Intention", "Middle"), ("Purchase Intention", "Old")])
    
    # グラフのレイアウト
    pos = nx.spring_layout(G)
    
    # グラフの描画
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=3000, font_size=12, font_weight='bold', arrows=True)
    
    plt.title("CHAID Decision Tree Visualization")
    plt.show()

# CHAIDアルゴリズムの実行
splits = chaid_decision_tree(data)

# 決定木の視覚化
visualize_decision_tree()

```

    Best split at 'Age_Group' with chi2: 12.0000 and p-value: 0.4457
    


    
![png](output_0_1.png)
    

