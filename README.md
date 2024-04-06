# Paper Recommender (論文レコメンダー)

自然言語の入力文を解析し、おすすめの論文をレコメンドするアプリ



https://github.com/traffine/paper-recommender/assets/45656383/31141cbb-3d98-4c98-8e05-13417e3eb85a



以下の機能があります。

- キーワードの自動抽出
  - ユーザーの自然言語の入力にある完全一致、類語から論文のキーワードを抽出します。
- ユーザーの入力と論文概要の類似度をもとにレコメンド
  - キーワードで論文をフィルタリングしたのち、ユーザーの入力と近い概要の論文を最大 3 件レコメンドします。
- 会話内において、二度同じ論文を勧めない
  - 一度レコメンドされた論文はレコメンドされません。（会話をやり直すとレコメンドされます。）
- AI の人格を付与
  - AI の発言には、独自のキャラクター設定が反映されています。

## サンプルデータ

[交通工学論文集 2024 年 10 巻 3 号](https://www.jstage.jst.go.jp/browse/jste/-char/ja)の論文タイトル、キーワード、概要、DOI を利用させていただいています。

## 環境設定

### 1. DynamoDB の作成

`terraform` ディレクトリに移動し、以下のコマンドを実行します。

```bash
$ export AWS_PROFILE=<your profile name>
$ terraform init
$ terraform apply
```

AWS に DynamoDB が作成されます。

### 2. Pinecone の作成

1. [Pinecone](https://www.pinecone.io/) にサインインします。

2. 「Create index」をクリックします。

![Pinecone | 1](/docs/images/pc_1.png)

3. Index を作成します。

| パラメータ     | 内容              |
| -------------- | ----------------- |
| インデックス名 | paper-recommender |
| METRIC         | cosine            |
| DIMENSIONS     | 1536              |

![Pinecone | 2](/docs/images/pc_2.png)

4. インデックス名、ENVIRONMENT、API キーをメモします。

![Pinecone | 3](/docs/images/pc_3.png)
![Pinecone | 4](/docs/images/pc_4.png)

### 3. 環境変数の設定

以下のコマンドを実行します。

```bash
export LOCAL=y
export AWS_PROFILE=default
export OPENAI_API_KEY=sk-xxxx
export PINECONE_API_KEY=abcd
export PINECONE_ENVIRONMENT=gcp-starter
export PINECONE_INDEX=paper-recommender
```

### 4. ローカル環境を構築

以下のコマンドを実行します。

```bash
$ python -m venv venv
$ . venv/bin/activate
$ pip install --upgrade pip
$ pip install poetry
$ poetry install
```

### 5. Pinecone に論文データを格納

以下のコマンドを実行します。

```bash
$ cd api
$ python utils/pc.py
```

## ローカル実行

### FastAPI

```bash
$ make run
```

### Streamlit

```bash
$ make st
```

## Docker 実行

1. `.env.sample` を元に `.env`のファイルを作成
2. `api` のフォルダに移動し、`make up` で起動
3. `make down` でシャットダウン

## Mecab 辞書更新作業

1. `data/papers/j-stage.json` を更新

手動で論文を追加、編集、削除などを行う

2. `data/dictionary/user.dic`を更新

以下を実行

```bash
$ python scripts/userdic.py
$ /opt/homebrew/Cellar/mecab/0.996/libexec/mecab/mecab-dict-index -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd -u data/dictionary/user.dic -f utf-8 -t utf-8 data/dictionary/userdic.csv
```
