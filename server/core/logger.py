import os
import time
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger():
    '''
    The logging handling level int value:
     - CRITICAL = 50
     - FATAL = CRITICAL
     - ERROR = 40
     - WARNING = 30
     - WARN = WARNING
     - INFO = 20
     - DEBUG = 10
     - NOTSET = 0
    '''

    logger = None
    formatter = None

    @classmethod
    def init_logger(cls, consoleLevel=20, fileLevel=30, filePath="") -> None:
        '''Initialize the instance of Log.
         - (str) consoleLevel: The console outputs a log level, default value is 10.
         - (str) fileLevelL: The file output log level, the default value is 50.
         - (str) filePath: The log file directory, the default vaule is the current location.
        '''
        cls.logger = logging.Logger('PLDZ-CODESPACE-BLOG')
        cls.logger.setLevel(logging.DEBUG)
        cls.formatter = logging.Formatter(
            '[ %(levelname)s ] - PLDZ-CODESPACE-BLOG: %(message)s')
        cls.setting_log(consoleLevel, fileLevel, filePath)

    @classmethod
    def setting_log(cls, consoleLevel, fileLevel, filePath) -> None:
        '''The main function to set the logger handler.
         - (str) consoleLevel: The log level at which the information can be outputed on screen.
         - (str) fileLevel: The log level at which the file can be written.
         - (str) filePath: The log file path, If the path does not exist, one is created.
        '''
        cls.set_console_handling(consoleLevel)
        if filePath != "":
            print(filePath)
            cls.set_file_handling(fileLevel, filePath)

    @classmethod
    def set_console_handling(cls, level) -> None:
        '''Set the log level at which the information can be outputed on screen.
         - (str) level: The log level at which the information can be outputed on screen.
        '''
        consoleHandling = logging.StreamHandler()
        # The handle to control if the logger can be output on terminal.
        consoleHandling = logging.StreamHandler()
        # If you want the INFO can be outputed on terminal, you can set the level in DEBUG
        consoleHandling.setLevel(level)
        consoleHandling.setFormatter(cls.formatter)

        cls.logger.addHandler(consoleHandling)

    @classmethod
    def set_file_handling(cls, level, filePath) -> None:
        '''Set the log file path and Set the log level at which the file can be written.
         - (str) level: The log level at which the file can be written.
         - (str) filePath: The log file path, If the path does not exist, one is created.
        '''
        # The handle of the files saved.
        logPath = os.getcwd() + filePath + "/"
        if not os.path.exists(logPath):
            try:
                os.mkdir(logPath)
            except OSError:
                print("Create the log file directory `{}`  failed!".format(logPath))
                return

        logName = time.strftime('%Y-%m-%d-%H-%M-%S.log', time.localtime())
        fileHandler = TimedRotatingFileHandler(
            logPath+logName, when='midnight', backupCount=3)
        print(logPath+logName)
        fileHandler.setLevel(level)
        fileHandler.setFormatter(cls.formatter)

        cls.logger.addHandler(fileHandler)

    @classmethod
    def info(cls, message) -> None:
        cls.logger.info(message)

    @classmethod
    def debug(cls, message) -> None:
        cls.logger.debug(message)

    @classmethod
    def warning(cls, message) -> None:
        cls.logger.warning(message)

    @classmethod
    def error(cls, message) -> None:
        cls.logger.error(message)

    @classmethod
    def critical(cls, message) -> None:
        cls.logger.critical(message)
