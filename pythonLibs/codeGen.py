
def classGen(className, namespace=None):
    try:
        # generate class object
        logger.info(className)
        newClass = type(className, (DefinitionBase,), dict( log = logger('CODEGEN' + __name__ + "." + className )) )
        globals()[className] = newClass
        
        # add namespace to class object
        if namespace:
            setattr( newClass, '__namespace__',  myGlobals.DUTdesc['namespace'] )
        return newClass
    except Exception as e:
        msg = '-- CODEGEN Error - classGen --------------------------'
        msg += str(e)
        msg += '\n'
        msg += '-- classname ---------------------------------'
        msg += className
        msg += '\n'
        logger.exception(msg)
        exit(2)

def methodGen(classObj, methodName, methodCode ):
    d = {}
    try:
        logger.info( methodName )
        exec methodCode in d
        setattr(classObj, methodName, d[(methodName)])
    except Exception as e:
        msg = '-- CODEGEN Error - methodGen -------------------------'
        msg += str(e)
        msg += '\n'
        msg += '-- methodName --------------------------------'
        msg += methodName
        msg += '\n'
        msg += '-- methodCode --------------------------------'
        lines = methodCode.splitlines()
        lineno = 1
        for line in lines:
            msg += "%2d :  %s \n" % (lineno, line)
            lineno += 1
        msg += '\n'
        logger.exception(msg)
        exit(2)
