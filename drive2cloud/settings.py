import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class CommonSettings:
    READER_TYPE = os.getenv('READER_TYPE')
    UPLOADER_TYPE = os.getenv('UPLOADER_TYPE')
    FILE_INDEX = os.getenv('FILE_INDEX')


class DropboxSettings:
    DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')
    DROPBOX_PATH = os.getenv('DROPBOX_PATH')
    MAX_CHUNK_SIZE = os.getenv('MAX_CHUNK_SIZE')


class FtpSettings:
    FTP_PATH = os.getenv('FTP_PATH')
    FTP_HOST = os.getenv('FTP_HOST')
    FTP_LOGIN = os.getenv('FTP_LOGIN')
    FTP_PWD = os.getenv('FTP_PWD')
    FTP_ENCODING = os.getenv('FTP_ENCODING')


class LocalSettings:
    LOCAL_ROOT_DIR = os.getenv('LOCAL_ROOT_DIR')
