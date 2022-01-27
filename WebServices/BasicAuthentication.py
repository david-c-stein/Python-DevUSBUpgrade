import base64

'''
Example usage:

def check_credentials(user, pwd):
    return user == 'foo'

@basic_auth(check_credentials)
class MyHandler(tornado.web.RequestHandler):
    pass
    
'''


def basic_auth(auth_func=lambda *args, **kwargs: True, after_login_func=lambda *args, **kwargs: None, realm='Restricted'):
    def basic_auth_decorator(handler_class):
        def wrap_execute(handler_execute):
            def require_basic_auth(handler, kwargs):
                def create_auth_header():
                    handler.set_status(401)
                    handler.set_header('WWW-Authenticate', 'Basic realm=%s' % realm)
                    handler._transforms = []
                    handler.finish()

                auth_header = handler.request.headers.get('Authorization')

                if auth_header is None or not auth_header.startswith('Basic '):
                    create_auth_header()
                else:
                    auth_decoded = base64.decodestring(auth_header[6:])
                    user, pwd = auth_decoded.split(':', 2)

                    if auth_func(user, pwd):
                        after_login_func(handler, kwargs, user, pwd)
                    else:
                        create_auth_header()

            def _execute(self, transforms, *args, **kwargs):
                require_basic_auth(self, kwargs)
                return handler_execute(self, transforms, *args, **kwargs)

            return _execute

        handler_class._execute = wrap_execute(handler_class._execute)
        return handler_class
    return basic_auth_decorator

    
    #=================================================================
    
    
    
'''
Example usage:

@httpauth
class SessionCreateHandler(tornado.web.RequestHandler):
    @allowedRole('administrator')
    def get(self):
        # Contains user found in previous auth
        print self.request.headers.get('auth')
        self.write('ok')
        
-or-

@httpauth
class SessionCreateHandler(tornado.web.RequestHandler):
    @allowedRole(['administrator', 'super-administrator'])
    def get(self):
        # Contains user found in previous auth
        print self.request.headers.get('auth')
        self.write('ok')
'''    
    
    
import base64
 
def _checkAuth(login, password):
    ''' Check user can access or not to this element '''
    # TODO: return None if user is refused
    # TODO: do database check here, to get user.
    return {
        'login': 'okay',
        'password': 'okay',
        'role': 'okay'
    }
 
def httpauth(handler_class):
    ''' Handle Tornado HTTP Basic Auth '''
    def wrap_execute(handler_execute):
        def require_auth(handler, kwargs):
            auth_header = handler.request.headers.get('Authorization')
 
            if auth_header is None or not auth_header.startswith('Basic '):
                handler.set_status(401)
                handler.set_header('WWW-Authenticate', 'Basic realm=Restricted')
                handler._transforms = []
                handler.finish()
                return False
 
            auth_decoded    = base64.decodestring(auth_header[6:])
            login, password = auth_decoded.split(':', 2)
            auth_found      = _checkAuth(login, password)
 
            if auth_found is None:
                handler.set_status(401)
                handler.set_header('WWW-Authenticate', 'Basic realm=Restricted')
                handler._transforms = []
                handler.finish()
                return False
            else:
                handler.request.headers.add('auth', auth_found)
 
            return True
 
        def _execute(self, transforms, *args, **kwargs):
            if not require_auth(self, kwargs):
                return False
            return handler_execute(self, transforms, *args, **kwargs)
 
        return _execute
 
    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class


# The _checkAuth should return a user object, and this
# configure which property from that objet get the 'role'
_userRolePropertyName = 'role'
 
def _checkRole(role, roles):
    ''' Check given role is inside or equals to roles '''
    # Roles is a list not a single element
    if isinstance(roles, list):
        found = False
        for r in roles:
            if r == role:
                found = True
                break
 
        if found == True:
            return True
 
    # Role is a single string
    else:
        if role == roles:
            return True
 
    return False
 
 
def allowedRole(roles = None):
    def decorator(func):
        def decorated(self, *args, **kwargs):
            user = self.request.headers.get('auth')
 
            # User is refused
            if user is None:
                raise Exception('Cannot proceed role check: user not found')
 
            role = user[_userRolePropertyName]
 
            if _checkRole(role, roles) == False:
                self.set_status(403)
                self._transforms = []
                self.finish()
                return None
 
            return func(self, *args, **kwargs)
        return decorated
    return decorator
 
 
def refusedRole(roles = None):
    def decorator(func):
        def decorated(self, *args, **kwargs):
            user = self.request.headers.get('auth')
 
            # User is refused
            if user is None:
                raise Exception('Cannot proceed role check: user not found')
 
            role = user[_userRolePropertyName]
 
            if _checkRole(role, roles) == True:
                self.set_status(403)
                self._transforms = []
                self.finish()
                return None
 
            return func(self, *args, **kwargs)
        return decorated
    return decorator
    
    
    
    
    

    