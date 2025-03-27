# SemanticViewer
# / CodeLLM
「**コードをトリガーに関連ドキュメントを右側ウィンドウに自動表示する検索・生成型支援システム**」
---

## 1．システム概要

### 目的：
- 開発者が Eclipse でテーブル名やメソッド名を書くと，
- 類似の設計書や仕様書（事前に埋め込み済み）を検索し，
- 関連文書を Eclipse の右側にポップアップ／ドッキングビューで自動表示

---

## 2．構成案

### （1）設計書ベースのベクトル検索基盤
- 事前に設計書やコード断片を分割・埋め込み
  - [LangChain](https://www.langchain.com/)，[Haystack](https://haystack.deepset.ai/)，自作でも可
- 使用モデル例：BGE-M3，e5-multilingual，or SBERT
- ベクトルDB：Faiss，Weaviate，Qdrant など

### （2）コード中の「検索トリガー要素」を検出
- Eclipse Plugin が `ICompilationUnit` から AST を解析
  - テーブル名：`"tbl_user"` のような文字列定数
  - メソッド名：`getUserById()` などの識別子
- Eclipse JDT を使ってリアルタイムで検出可能

### （3）トリガー語句をLLMまたはベクトル検索へ送信
- 例：「tbl_user」という文字列を検索クエリとして投げる
- 返ってきた設計書断片（text + source filenameなど）を並べて表示

### （4）UI（右側表示）
- Eclipse の `ViewPart` を使って右側に「関連設計書」ビューを実装
- 複数の類似文書をスコア付きで並べて表示（クリックで原文表示）

---

## 3．処理フロー（図示的）

```plaintext
[コード記述]
    ↓
[Plugin が識別子 or テーブル名抽出]
    ↓
[ベクトル検索 or LLM検索（RAG）]
    ↓
[関連設計書の断片を取得]
    ↓
[右側ビューで表示（出典＋概要）]
```

---

## 4．ユーザー体験の例

### Javaコード：
```java
User user = userRepository.findByUsername("admin");
```

### 右側ビュー（自動で表示）：
```
【関連設計書】
- ER図：Userテーブル（PK: id, username, ...）
- findByUsername の定義（DAO設計書 第2版 5.2節）
- ユーザー認証設計：Basic認証処理フロー
```

---

## 5．技術的に可能な理由

- Eclipseは構文木ベースで構造情報を取得できる（JDT）
- 設計書を事前にベクトル化しておけば，LLMなしでも類似検索が可能
- LangChainやHaystackで「文書→埋め込み→RAG」基盤を構築可能
- Eclipse Pluginは独自ビューを追加できるので，右側に資料を並べるUIは自然

---

## 6．補足：生成AIとの連携強化
- 関連文書を「生成元の根拠」として，チャット型LLMと連携
- 例：「このメソッドって何をしてる？」→右側の資料に基づいて解説生成

---

## 7．今後の展開

- 関連資料の自動分類（仕様書，テーブル定義書，ER図，フローチャートなど）
- コード補完と連携して，提案コードに対する設計書根拠を横に出す
- チーム間ナレッジ共有への発展

---

もしよろしければ，次のステップとして以下のどれを進めたいか教えてください：

1. 設計書ベクトル化と検索システムの構築（LangChain/Faissなど）
2. Eclipse Plugin 側の原型コード（AST抽出＋ビュー表示）
3. LLM（ollama/LM Studio）との連携設計

それに応じて具体的なコードや構成図をご提供できます．

はい，その「**ユーザーが何もしなくてもコードに反応して自動的に関連資料が右側に“わらわら”表示されるモード**」は，非常に魅力的で，**ユーザー体験（UX）を大きく向上**させます．実装も十分に可能です．以下にその実現方法を解説いたします．

---

# 💡 Eclipseで自動ドキュメント連携モードを実現する方法

---

## ✅ ゴール

- 開発者が Eclipse 上でコードを「普通に書いているだけ」で，
- 特定のテーブル名，メソッド名，クラス名などが書かれた瞬間に，
- 背後でキーワードを自動検出して，
- 右側の「関連資料ビュー」に社内ドキュメントが“わらわら”と表示される

---

## 🏗 実現方法の概要

```plaintext
[Javaコードの編集を監視]
     ↓
[一定間隔で変化を検知]
     ↓
[ASTまたは正規表現で識別子（テーブル名やメソッド名）抽出]
     ↓
[既存のPython検索APIへクエリ送信]
     ↓
[関連資料を右ペインに表示（自動更新）]
```

---

## 第1章：編集イベントを検出する（Java）

### 方法A：`IDocumentListener`（最も簡単）

```java
IDocument document = editor.getDocumentProvider().getDocument(editor.getEditorInput());
document.addDocumentListener(new IDocumentListener() {
    @Override
    public void documentChanged(DocumentEvent event) {
        String newText = event.getDocument().get();
        // ここでキーワード抽出・検索を呼び出す
    }
    @Override
    public void documentAboutToBeChanged(DocumentEvent event) {}
});
```

- `documentChanged` の中で，全文または一部だけを分析すればOKです

---

## 第2章：キーワード抽出ロジック

### 方法A：正規表現（軽量）

```java
Pattern pattern = Pattern.compile("\\b(get\\w+|tbl_\\w+)\\b");  // メソッド名やテーブル名候補
Matcher matcher = pattern.matcher(currentText);

Set<String> keywords = new HashSet<>();
while (matcher.find()) {
    keywords.add(matcher.group());
}
```

- 過去に送信したキーワードと比較し，**新しく出てきた語句のみ**を検索対象にするのがポイント

---

## 第3章：Python API との自動連携

### 🔁 前回と同じ FastAPI サーバに POST

```java
for (String keyword : newKeywords) {
    String json = "{\"query\": \"" + keyword + "\"}";
    HttpRequest request = HttpRequest.newBuilder()
        .uri(URI.create("http://localhost:8000/search"))
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(json))
        .build();

    HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
    updateRightPane(response.body());  // 表示ビューに反映
}
```

---

## 第4章：右側ビューの動的更新

- `ViewPart` のインスタンスを保持しておけば，`updateText()` を呼び出すことで随時更新可能

```java
public void updateRightPane(String contentJson) {
    Display.getDefault().asyncExec(() -> {
        RelatedDocView view = (RelatedDocView) PlatformUI.getWorkbench()
            .getActiveWorkbenchWindow().getActivePage()
            .findView("com.example.relatedDocView");

        if (view != null) {
            view.updateText(parseJsonToReadableText(contentJson));
        }
    });
}
```

---

## 第5章：ユーザー体験の演出アイデア

| アイデア | 説明 |
|----------|------|
| 🪄 フェードイン | 新しい資料が表示されたときにふわっと出る |
| 🏷 タグ付き表示 | 「DB設計」「API仕様」などカテゴリで色分け |
| 📌 ピン留め機能 | 検索結果を固定して残せるボタン付き |

---

## 第6章：過剰検索を防ぐ工夫

- ⚠️ 文字を1文字打つごとにAPI呼ぶと重くなりますので，
- 以下のいずれかの戦略で軽量化可能：

| 方法 | 内容 |
|------|------|
| デバウンス | 編集後500ms以上変化がなければ検索開始 |
| キーワードキャッシュ | 同じ語は1回しか検索しない |
| AST解析 | メソッド/変数が追加されたときだけ検索する

---

## ✅ まとめ

- Eclipseでは「ユーザー操作なし」でコード中の語句を検出することが可能
- `IDocumentListener`を使えば容易にリアルタイム反応型のPluginが作れる
- ローカルのFastAPI（Faiss検索）とつなげば，社内文書を即表示できる
- 表示UIの工夫で“わらわら出てくる”楽しいUXも演出可能

---

ご希望があれば，この自動モードに特化した以下の支援も可能です：

1. ⚙️ Javaでのリアルタイム検索連携Pluginの雛形
2. 🔍 ASTベースで型やテーブル名だけを検出するロジック
3. 🎨 UI演出（表示の重複防止・アニメーション演出）
4. 📁 Eclipseプロジェクトとして一式セットアップ済みZip

必要に応じて，どこからスタートされるかお知らせください．そこから段階的にご一緒します！



with MCP
![MCP_ AIアプリケーションのためのオープンプロトコル](https://github.com/user-attachments/assets/8228a97a-f2d7-46dc-b977-08d4f8cc86ac)
