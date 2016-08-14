import web

class Controller(object):
    def __init__(self):
        self.callType = ''
        pass

#todo replace self, userHash by *arg
    def GET(*arg):
        self = arg[0]
        self.callType = 'GET'
        self.process_main(self, arg[1:])

#todo replace self, userHash by *arg
    def POST(*arg):
        self = arg[0]
        self.callType = 'POST'
        self.process_main(arg)

    def process_main(*arg):
        self = arg[0]
        self.check_IP_allowed() # Will terminate all non-auth. connections 
#TODO re-implement this
        #if not session.get('logged_in', False):
            #TODO: determine the caller'
            #raise web.seeother('/login/%s?caller=%s' %(userHash, caller))

        self.process_sub(arg) #call the subclass implementation

    # Should be implemented by subclass
    def process_sub(self):
        raise NotImplementedError

    # Checks if IP is allowed
    # If not imidialty sends a 404 and stops all processing
    def check_IP_allowed(self):
        from config import config
        from iptools import IpRangeList
        ip = web.ctx['ip']
        ipRanges = config['IpRanges'].split()
        start = ipRanges[0:][::2]
        stop = ipRanges[1:][::2]

        for start,stop in zip(start,stop):
            ipRange = IpRangeList( (start,stop) )
            if ip in ipRange:
                return

        raise web.notfound()
