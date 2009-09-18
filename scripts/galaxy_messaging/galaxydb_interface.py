#/usr/bin/python

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import sys
import optparse
import os
import time
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger( 'GalaxyDbInterface' )

class GalaxyDbInterface(object):
    
    def __init__(self, dbstr):
        self.dbstr = dbstr
        self.db_engine = create_engine(self.dbstr)    
#        self.db_engine.echo = True  
        self.metadata = MetaData(self.db_engine)
        self.session = sessionmaker(bind=self.db_engine)
        self.event_table = Table('sample_event', self.metadata, autoload=True )
        self.sample_table = Table('sample', self.metadata, autoload=True )
        self.request_table = Table('request', self.metadata, autoload=True )
        self.state_table = Table('sample_state', self.metadata, autoload=True  )

    def get_sample_id(self, field_name='bar_code', value=None):
        if not value:
            return -1
        sample_id = -1
        if field_name =='name':
            stmt = select(columns=[self.sample_table.c.id],
                          whereclause=self.sample_table.c.name==value)
            result = stmt.execute()
            sample_id = result.fetchone()[0]
        elif field_name == 'bar_code':
            stmt = select(columns=[self.sample_table.c.id],
                          whereclause=self.sample_table.c.bar_code==value)
            result = stmt.execute()
            x = result.fetchone()
            if x:
                sample_id = x[0]
                log.debug('Sample ID: %i' % sample_id)
                return sample_id
        log.warning('This sample %s %s does not belong to any sample in the database.' % (field_name, value))
        return -1
        
    def current_state(self, sample_id):
        '''
        This method returns the current state of the sample for the given sample_id
        '''
        stmt = select(columns=[self.event_table.c.sample_state_id],
                      whereclause=self.event_table.c.sample_id==sample_id,
                      order_by=self.event_table.c.update_time.desc())
        result = stmt.execute()
        all_states = result.fetchall()
        current_state_id = all_states[0][0]
        return current_state_id
        
    def all_possible_states(self, sample_id):
        subsubquery = select(columns=[self.sample_table.c.request_id], 
                             whereclause=self.sample_table.c.id==sample_id)
        self.request_id = subsubquery.execute().fetchall()[0][0]
        log.debug('REQUESTID: %i' % self.request_id)
        subquery = select(columns=[self.request_table.c.request_type_id], 
                          whereclause=self.request_table.c.id==self.request_id)
        request_type_id = subquery.execute().fetchall()[0][0]
        log.debug('REQUESTTYPEID: %i' % request_type_id)
        query = select(columns=[self.state_table.c.id, self.state_table.c.name], 
                       whereclause=self.state_table.c.request_type_id==request_type_id,
                       order_by=self.state_table.c.id.asc())
        states = query.execute().fetchall()
        log.debug('POSSIBLESTATES: '+ str(states))
        return states
    
    def change_state(self, sample_id, new_state=None):
        '''
        This method changes the state of the sample to the the 'new_state' 
        '''
        if not new_state:
            return
        new_state_id = -1
        # find the state_id for this new state in the list of possible states
        possible_states = self.all_possible_states(sample_id)
        for state_id, state_name in possible_states:
            if new_state == state_name:
                new_state_id = state_id
        if new_state_id == -1:
            return
        log.debug('Updating sample_id %i state to %s' % (sample_id, new_state))
        d = timedelta(hours=4)
        i = self.event_table.insert()
        i.execute(update_time=datetime.now()+d, 
                  create_time=datetime.now()+d,
                  sample_id=sample_id, 
                  sample_state_id=int(new_state_id), 
                  comment='bar code scanner')
        # if all the samples for this request are in the final state
        # then change the request state to 'Complete'
        result = select(columns=[self.sample_table.c.id],
                        whereclause=self.sample_table.c.request_id==self.request_id).execute()
        sample_id_list = result.fetchall()
        request_complete = True
        for sid in sample_id_list:
            current_state_id = self.current_state(sid[0])
            if current_state_id != possible_states[-1][0]:
                request_complete = False
                break
        if request_complete:
            request_state = 'Complete'
        else:
            request_state = 'Submitted'
        log.debug('Updating request_id %i state to "%s"' % (self.request_id, request_state))
        d = timedelta(hours=4)
        i = self.request_table.update(whereclause=self.request_table.c.id==self.request_id,
                                      values={self.request_table.c.state: request_state})
        i.execute()



if __name__ == '__main__':
    print '''This file should not be run directly. To start the Galaxy AMQP Listener:
    %sh run_galaxy_listener.sh'''
#    dbstr = 'postgres://postgres:postgres@localhost/galaxy_ft'
#
#    parser = optparse.OptionParser()
#    parser.add_option('-n', '--name', help='name of the sample field', dest='name', \
#                      action='store', default='bar_code')
#    parser.add_option('-v', '--value', help='value of the sample field', dest='value', \
#                      action='store')
#    parser.add_option('-s', '--state', help='new state of the sample', dest='state', \
#                      action='store')
#    (opts, args) = parser.parse_args()
#
#    gs = GalaxyDbInterface(dbstr)
#    sample_id = gs.get_sample_id(field_name=opts.name, value=opts.value)
#    gs.change_state(sample_id, opts.state)

            

