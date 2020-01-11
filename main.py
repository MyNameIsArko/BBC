import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

import bbc
bbc.bbc.run()