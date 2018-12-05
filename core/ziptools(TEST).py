# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# streamondemand-pureita-master - XBMC Plugin
# Zip Tools
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand-pureita-master/
#------------------------------------------------------------
import zipfile
import os
import os.path

import logger


class ziptools:
    def extract(self, file, dir):
        logger.info("file=%s" % file)
        logger.info("dir=%s" % dir)

        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)

        zf = zipfile.ZipFile(file)
        self._createstructure(file, dir)
        num_files = len(zf.namelist())

        for name in zf.namelist():
            logger.info("name=%s" % name)
            if not name.endswith('/'):
                content = zf.read(name)
                name = name.replace('-master', '')
                logger.info("no es un directorio")
                try:
                    (path, filename) = os.path.split(os.path.join(dir, name))
                    logger.info("path=%s" % path)
                    logger.info("name=%s" % name)
                    os.makedirs(path)
                except:
                    pass
                outfilename = os.path.join(dir, name)
                logger.info("outfilename=%s" % outfilename)
                try:
                    outfile = open(outfilename, 'wb')
                    outfile.write(content)
                except:
                    logger.info("Error en fichero " + name)

    def _createstructure(self, file, dir):
        self._makedirs(self._listdirs(file), dir)

    def _makedirs(self, directories, basedir):
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                os.mkdir(curdir)

    def _listdirs(self, file):
        zf = zipfile.ZipFile(file)
        dirs = []
        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name.replace('-master', ''))

        dirs.sort()
        return dirs
