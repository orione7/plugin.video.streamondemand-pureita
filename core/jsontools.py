# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# tvalacarta - XBMC Plugin
# ------------------------------------------------------------
# json_tools
# Parsea un string en JSON probando varios módulos
# ------------------------------------------------------------

import traceback
import logger

#Incorporadas las funciones loads() y dumps() para json y simplejson
def loads(*args, **kwargs):
  try:
    logger.info("core.jsontools.loads Probando json incluido en el interprete")
    import json
    return to_utf8(json.loads(*args, **kwargs))
  except ImportError:
    pass
  except:
   logger.info(traceback.format_exc())

  try:
    logger.info("core.jsontools.loads Probando simplejson incluido en el interprete")
    import simplejson as json
    return to_utf8(json.loads(*args, **kwargs))
  except ImportError:
    pass
  except:
   logger.info(traceback.format_exc())
   
  try:
    logger.info("core.jsontools.loads Probando simplejson en el directorio lib")
    from lib import simplejson as json
    return to_utf8(json.loads(*args, **kwargs))
  except ImportError:
    pass
  except:
   logger.info(traceback.format_exc())
   
def dumps(*args, **kwargs):
  try:
    logger.info("core.jsontools.loads Probando json incluido en el interprete")
    import json
    return json.dumps(*args, **kwargs)
  except ImportError:
    pass
  except:
   logger.info(traceback.format_exc())

  try:
    logger.info("core.jsontools.loads Probando simplejson incluido en el interprete")
    import simplejson as json
    return json.dumps(*args, **kwargs)
  except ImportError:
    pass
  except:
   logger.info(traceback.format_exc())
   
  try:
    logger.info("core.jsontools.loads Probando simplejson en el directorio lib")
    from lib import simplejson as json
    return json.dumps(*args, **kwargs)
  except ImportError:
    pass
  except:
   logger.info(traceback.format_exc())
   
 
def to_utf8(dct):
  if isinstance(dct, dict):
      return dict((to_utf8(key), to_utf8(value)) for key, value in dct.iteritems())
  elif isinstance(dct, list):
      return [to_utf8(element) for element in dct]
  elif isinstance(dct, unicode):
      return dct.encode('utf-8')
  else:
      return dct


##############
def load_json(data):
    logger.info("core.jsontools.load_json Probando simplejson en directorio lib")

    def to_utf8(dct):
        if isinstance(dct, dict):
            return dict((to_utf8(key), to_utf8(value)) for key, value in dct.iteritems())
        elif isinstance(dct, list):
            return [to_utf8(element) for element in dct]
        elif isinstance(dct, unicode):
            return dct.encode('utf-8')
        else:
            return dct

    try:
        logger.info("core.jsontools.load_json Probando simplejson en directorio lib")
        from lib import simplejson
        json_data = simplejson.loads(data, object_hook=to_utf8)
        logger.info("core.jsontools.load_json -> "+repr(json_data))
        return json_data
    except:
        logger.info(traceback.format_exc())

        try:
            logger.info("core.jsontools.load_json Probando simplejson incluido en el interprete")
            import simplejson
            json_data = simplejson.loads(data, object_hook=to_utf8)
            logger.info("core.jsontools.load_json -> "+repr(json_data))
            return json_data
        except:
            logger.info(traceback.format_exc())
            
            try:
                logger.info("core.jsontools.load_json Probando json incluido en el interprete")
                import json
                json_data = json.loads(data, object_hook=to_utf8)
                logger.info("core.jsontools.load_json -> "+repr(json_data))
                return json_data
            except:
                logger.info(traceback.format_exc())

                try:
                    logger.info("core.jsontools.load_json Probando JSON de Plex")
                    json_data = JSON.ObjectFromString(data, encoding="utf-8")
                    logger.info("core.jsontools.load_json -> "+repr(json_data))
                    return json_data
                except:
                    logger.info(traceback.format_exc())

    logger.info("core.jsontools.load_json No se ha encontrado un parser de JSON valido")
    logger.info("core.jsontools.load_json -> (nada)")
    return ""


def dump_json(data):
    logger.info("core.jsontools.dump_json Probando simplejson en directorio lib")

    try:
        logger.info("core.jsontools.dump_json Probando simplejson en directorio lib")
        from lib import simplejson
        json_data = simplejson.dumps(data, indent=4, skipkeys=True, sort_keys=True, ensure_ascii=False)
        # json_data = byteify(json_data)
        logger.info("core.jsontools.dump_json -> "+repr(json_data))
        return json_data
    except:
        logger.info(traceback.format_exc())

        try:
            logger.info("core.jsontools.dump_json Probando simplejson incluido en el interprete")
            import simplejson
            json_data = simplejson.dumps(data, indent=4, skipkeys=True, sort_keys=True, ensure_ascii=False)
            logger.info("core.jsontools.dump_json -> "+repr(json_data))
            return json_data
        except:
            logger.info(traceback.format_exc())

            try:
                logger.info("core.jsontools.dump_json Probando json incluido en el interprete")
                import json
                json_data = json.dumps(data, indent=4, skipkeys=True, sort_keys=True, ensure_ascii=False)
                logger.info("core.jsontools.dump_json -> "+repr(json_data))
                return json_data
            except:
                logger.info(traceback.format_exc())

                try:
                    logger.info("core.jsontools.dump_json Probando JSON de Plex")
                    json_data = JSON.StringFromObject(data)  #, encoding="utf-8")
                    logger.info("core.jsontools.dump_json -> "+repr(json_data))
                    return json_data
                except:
                    logger.info(traceback.format_exc())

    logger.info("core.jsontools.dump_json No se ha encontrado un parser de JSON valido")
    logger.info("core.jsontools.dump_json -> (nada)")
    return ""
