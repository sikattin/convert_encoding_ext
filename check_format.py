# -*- coding: utf-8 -*-
# check_format.py
#
# 文字エンコーディングとファイル形式のチェックを行い
# 指定の形式でなければ変換を行うスクリプト.
#
import os
import sys
from logging import getLogger, StreamHandler, Formatter, WARNING, DEBUG, INFO
from subprocess import check_output, check_call

# nkfコマンド 文字エンコーディング確認.
NKF_CMD_CHKENCODE = 'nkf -g '
# nkfコマンド 変換.
NKF_CMD_CONVERT = 'nkf -s --overwrite '


class CheckFormat:
    """
    how to use:
    CheckFormat(dir_path='directory_path', loglevel='WARNING|DEBUG|INFO')
    _get_file_names() ... dir_path直下のファイル名一覧を取得する.初期化時に実行される.
    check_encoding() ... 取得したファイルの文字エンコーディングを確認するメソッド.
    change_encoding() ... Shift-JIS 以外の文字エンコーディングファイルを Shift-JISに変換するメソッド.
    change_format_to_csv() ... .txtにマッチするファイル を .csv に変換するメソッド.
    """

    def __init__(self, dir_path: str, loglevel: str):
        """
        コンストラクタ
        :param dir_path: ディレクトリパス.
        :param loglevel: ログレベル.
        """
        # ディレクトリパス.
        self._dir_path = dir_path
        # ログレベル.
        self._loglevel = loglevel
        # ファイル名の一覧
        self._file_names = []
        # (ファイル名, コマンドの実行結果) タプルを格納するリスト.
        self.cmd_ret = []

        # ロガーのセットアップを初期化時に行っておく.
        setup_logger(self._loglevel)
        # ファイル名一覧の取得を初期化時に行っておく.
        _get_file_names()

    def setup_logger(self, loglevel: str):
        """
        ロガーのセットアップを行う.
        """
        # ロガー作成.
        self._logger = getLogger(str(self))
        self._logger.setLevel(loglevel)
        # コンソールハンドラの作成.
        ch = StreamHandler()
        ch.setLevel(loglevel)
        # フォーマッターの作成.
        formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        # ロガーにコンソールハンドラを追加.
        self._logger.addHandler(ch)

    def _warning(self, msg):
        """
        WARNINGレベルのログメッセージを
        送信する.
        """
        self._logger.warning(msg)

    def _debug(self, msg):
        """
        DEBUGレベルのログメッセージを
        送信する.
        """
        self._logger.debug(msg)

    def _info(self, msg):
        """
        INFOレベルのログメッセージを
        送信する.
        """
        self._logger.info(msg)

    def check_encoding(self):
        """
        ファイルの文字エンコードを確認する関数.
        """
        cmds = [NKF_CMD_CHKENCODE + file for file in self._file_names]
        for cmd in cmds:
            cmd_list = cmd.split()
            # ファイル名を取得.
            file_name = cmd_list[2]
            # コマンドの実行結果を取得.
            try:
                cmd_result = check_output(cmd_list)
                # (file_name, cmd_result) の組でlistに格納.
                self.cmd_ret.append((file_name, cmd_result))
            except CalledProcessError as e:
                print('{0}, {1} コマンドの実行に失敗.'.format(e.output, cmd))
                raise e

    def change_encoding(self):
        """
        ファイルの文字エンコーディングを変換する関数.
        """
        for ret_tuple in self.cmd_ret:
            if not ret_tuple[1].startswith('Shift_JIS'):
               cmd = NKF_CMD_CONVERT + ret_tuple[0]
               print("""ファイル名: {0} の文字コード変換を実行します.
               変換前: {1} 変換後　Shift-JIS
               {2} コマンドを実行します.""".format(ret_tuple[0], ret_tuple[1], cmd))
               try:
                   return_code = check_call(cmd)
                   print('returncode={0}, {1} コマンドの実行に成功.'.format(return_code, cmd))
               except CalledProcessError as e:
                   print('returncode={0}, {1} コマンドの実行に失敗.'.format(e.returncode, cmd))
                   raise e
            else:
                pass

    def change_format_to_csv(self):
        """
        .txt を .csvに変換する関数.
        """
        import re
        # .txtファイルを.csvにリネーム.
        for fi in self._file_names:
            txt = re.compile(".+\.txt$")
            if txt.search(fi):
                file_name, ext = os.path.splitext(fi)
                os.rename(fi, file_name + {}.format('.csv'))
                print('{0} を {1} に変換しました.'.format(fi, file_name+'.csv'))
            else:
                pass

    def _get_file_names(self):
        """
        ファイル名の一覧を取得する関数.
        :param dir_path: ディレクトリパス.
        :return: ファイル名のリスト.
        """
        # ファイル名の一覧を取得する.ディレクトリは除外.
        for file in os.listdir(self._dir_path):
            if os.path.isfile(self._dir_path + file):
                self._file_names.append(file)

if __name__ == '__main__':
    # 引数処理.
    import argparse
    argparser = argparse.ArgumentParser(description='指定したディレクトリ配下にあるファイルの文字エンコーディング、拡張子のチェック・変換を行うコマンド.')
    argparser.add_argument('-d', '--dir', metavar='<DIRECTORY>', type=str, required=False, default='./', help="検査対象のファイルが配置されているディレクトリURI デフォルトは './' ex.check_filedir/")
    argparser.add_argument('-l', '--loglevel', type=str, required=False, default='WARNING',
                           metavar='(WARNING|INFO|DEBUG)',
                           help='ログレベル.(デフォルトは WARNING)')
    args = argparser.parse_args()

    # 初期化.
    chk_ins = CheckFormat(dir_path=args.dir, loglevel=args.loglevel)
    # フォーマット変換.
    chk_ins.change_format_to_csv()
    # 文字エンコーディングの確認.
    chk_ins.check_encoding()
    # 文字エンコーディングの変換.
    chk_ins.change_encoding()
