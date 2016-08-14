import web

class Controller(object):
    def __init__(self):
        self.callType = ''
        pass

#todo replace self, userHash by *arg
    def GET(*arg):
        print type(arg)
        print len(arg)
        print arg
        exit()
        self = arg[0]
        self.callType = 'GET'
        self.process_main(self, arg[1])

#todo replace self, userHash by *arg
    def POST(*arg):
        self.callType = 'POST'
        self.process_main()

    def process_main(self, *arg):
        print 'process_main'
        print len(arg)
        print type(arg)
        print arg
        self.check_IP_allowed() # Will terminate all non-auth. connections 
#TODO re-implement this
        #if not session.get('logged_in', False):
            #TODO: determine the caller'
            #raise web.seeother('/login/%s?caller=%s' %(userHash, caller))

        #self.process_sub() #call the subclass implementation

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
