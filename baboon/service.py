import logging

from config import config
from transport import Transport
from diffman import Diffman


class Service(object):
    def __init__(self):
        """
        """

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        self.xmpp = Transport(self._handle_event)
        self.xmpp.register_plugin('xep_0030')  # Service Discovery
        self.xmpp.register_plugin('xep_0004')  # Data Forms
        self.xmpp.register_plugin('xep_0060')  # PubSub
        self.xmpp.register_plugin('xep_0199')  # XMPP Ping

        self.diffman = Diffman()

    def start(self):
        if self.xmpp.connect():
            self.xmpp.process()
        else:
            print("Unable to connect.")

    def broadcast(self, filepath, patch):
        self.xmpp.broadcast(filepath, patch)

    def make_patch(self, oldfile, newfile):
        """ Creates a patch between oldfile and newfile
        """
        patch = self.diffman.diff(oldfile, newfile)
        self.logger.debug("Created the patch: %s" % patch)
        return patch

    def apply_patch(self, project_name, thepatch, thefile):
        """ Applies the patch on the file 'thefile'.
        Returns True if success
        """
        return self.diffman.patch(thepatch, "%s%s"
                                  % (config.path, thefile))

    def _handle_event(self, msg):
        if msg['type'] == 'headline':
            self.logger.info("Received pubsub item(s)")
            self.logger.debug("Received pubsub item(s) : %s" %
                              msg['pubsub_event'])

            for item in msg['pubsub_event']['items']['substanzas']:
                try:
                    payload = item['payload']
                    project_name = payload[0].text
                    filepath = payload[1].text
                    thediff = payload[2].text
                    author = payload[3].text

                    if author != config.jid:
                        result = self.apply_patch(project_name, thediff,
                                              filepath)
                        if False in result[1]:
                            msg = "Conflict detected"
                            self.logger.info(msg)
                            self.notify(msg)
                        else:
                            msg = "Everything seems to be perfect"
                            self.logger.debug(msg)
                            self.notify(msg)
                except:
                    # ugly hack to match good patch item
                    pass

        else:
            self.logger.debug("Received pubsub event: %s" %
                              msg['pubsub_event'])

    def notify(self, msg):
        self.xmpp.sendMessage(config.admin_jid, msg)
