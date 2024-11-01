import os

DOT_ENV_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '.env'))
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data'))
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates'))
BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'build'))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'reports'))