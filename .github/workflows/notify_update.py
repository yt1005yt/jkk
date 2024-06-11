name: Notify Update

on:
  schedule:
    - cron: '*/10 * * * *'  # 毎時10分ごとに実行

jobs:
  notify:
    runs-on: ubuntu-latest

    steps:
    - name: リポジトリのチェックアウト
      uses: actions/checkout@v2

    - name: Pythonのセットアップ
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'

    - name: 依存関係のインストール
      run: |
        python -m pip install --upgrade pip
        pip install requests beautifulsoup4

    - name: スクリプトの実行
      run: python notify_update.py
      env:
        LINE_TOKEN: ${{ secrets.LINE_TOKEN }}
        URL: "https://jkkwatcher.com/recentupdate/"