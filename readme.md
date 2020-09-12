# ImplicitGrantManager

## 概要

　Oauth2.0のImplicitGrantに準拠した認証を簡単に行うためのモジュール

## 機能

	- 認証に使うCSRFトークンと、認証用URLの生成
	- 認証結果をパースして辞書で返却
	- ローカルでウェブサーバを立ち上げ、最低限のユーザ操作で認証を実現
	- 認証結果にexpires_in(トークン有効時間(秒))のみが含まれる場合でも、現在時刻からexpires_at(UnixTimeによる有効期限)を付加

## 使い方

　example.pyをご覧ください。

