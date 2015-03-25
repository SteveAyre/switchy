# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Make single calls synchronously
"""
from contextlib import contextmanager
from test import TonePlay
from switchy import Client, get_listener, utils


@contextmanager
def sync_caller(host, port='8021', password='ClueCon',
                apps={'TonePlay': TonePlay}):
    '''Deliver a synchronous caller
    '''
    client = Client(
        host, port, password, listener=get_listener(host, port, password)
    )
    client.listener.connect()
    client.connect()
    # load app set
    app_names = []
    for value, app in apps.items():
        app_names.append(client.load_app(app, on_value=value if value else
                         utils.get_name(app)))

    client.listener.start()

    def caller(dest_url, app_name, timeout=30, waitfor=None,
               **orig_kwargs):
        '''Make a call synchronously returning control once it has entered
        a stable state.
        Deliver the active originating `Session` and a `waitfor` blocker
        method as output.
        '''
        # override the channel variable used to look up the intended
        # switchy app to be run for this call
        if caller.lookup_var:
            client.listener.id_var = caller.lookup_var

        job = client.originate(dest_url, app_id=app_name, **orig_kwargs)
        job.wait(timeout)
        if not job.successful():
            raise job.result
        call = client.listener.calls[job.sess_uuid]
        orig_sess = call.sessions[0]  # first sess is the originator
        if waitfor:
            var, time = waitfor
            client.listener.waitfor(orig_sess, var, time)

        return orig_sess, client.listener.waitfor

    # attach apps handle for easy interactive use
    caller.lookup_var = None
    caller.apps = client.apps
    caller.client = client
    caller.app_names = app_names
    yield caller
    client.listener.disconnect()
    client.disconnect()