"""show_mld.py

IOSXE parsers for the following show commands:

    * show ipv6 mld interface 
    * show ipv6 mld vrf <WORD> interface 
    * show ipv6 mld groups detail
    * show ipv6 mld vrf <WORD> groups detail
    * show ipv6 mld ssm-map
    * show ipv6 mld ssm-map <WORD>
    * show ipv6 mld vrf <WORD> ssm-map <WORD>
    * show ipv6 mld snooping querier
    * show platform software fed switch active ipv6 mld snooping groups count
"""

# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Optional


# ==============================================
# Parser for 'show ipv6 mld interface'
# Parser for 'show ipv6 mld vrf <WORD> interface'
# ==============================================

class ShowIpv6MldInterfaceSchema(MetaParser):
    """Schema for:
        show ipv6 mld interface
        show ipv6 mld vrf <vrf> interface"""
    schema = {'vrf':
                {Any(): {
                    Optional('max_groups'): int,
                    Optional('active_groups'): int,
                    'interface': {
                        Any(): {
                            'oper_status': str,
                            'interface_status': str,
                            Optional('interface_adress'): str,
                            'enable': bool,
                            Optional('version'): int,
                            Optional('query_interval'): int,
                            Optional('querier_timeout'): int,
                            Optional('query_max_response_time'): int,
                            Optional('last_member_query_interval'): int,
                            Optional('group_policy'): str,
                            Optional('max_groups'): int,
                            Optional('active_groups'): int,
                            Optional('counters'): {
                                'joins': int,
                                'leaves': int,
                            },
                            Optional('querier'): str,
                            Optional('query_this_system'): bool,
                        },
                    }
                }
            },
        }

class ShowIpv6MldInterface(ShowIpv6MldInterfaceSchema):
    """Parser for:
        show ipv6 mld interface
        show ipv6 mld vrf <vrf> interface"""

    cli_command = ['show ipv6 mld vrf {vrf} interface','show ipv6 mld interface']
    exclude = ['(LIIN.*)', '(Tunnel.*)', '(Loopback.*)', 'joins', 'leaves']


    def cli(self, vrf='',output=None):
        if output is None:
            if vrf:
                cmd = self.cli_command[0].format(vrf=vrf)
            else:
                vrf = 'default'
                cmd = self.cli_command[1]
            out = self.device.execute(cmd)
        else:
            out = output

        # initial variables
        ret_dict = {}

        for line in out.splitlines():
            line = line.strip()

            # Global State Limit : 0 active out of 64000 max
            p1 = re.compile(r'^Global +State +Limit *: +'
                             r'(?P<active>\d+) +active +out +of +(?P<global_max_groups>\d+) +max$')
            m = p1.match(line)
            if m:
                max_groups = int(m.groupdict()['global_max_groups'])
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}

                ret_dict['vrf'][vrf]['max_groups'] = max_groups
                ret_dict['vrf'][vrf]['active_groups'] = int(m.groupdict()['active'])
                continue

            # GigabitEthernet1 is up, line protocol is up
            p2 = re.compile(r'^(?P<intf>[\w\-\.\/]+) +is +(?P<intf_status>[\w\s]+), +'
                             r'line +protocol +is +(?P<oper_status>\w+)$')
            m = p2.match(line)
            if m:
                intf = m.groupdict()['intf']
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}

                if 'interface' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['interface'] = {}
                if intf not in ret_dict['vrf'][vrf]['interface']:
                    ret_dict['vrf'][vrf]['interface'][intf] = {}

                ret_dict['vrf'][vrf]['interface'][intf]['oper_status'] = \
                    m.groupdict()['oper_status'].lower()
                ret_dict['vrf'][vrf]['interface'][intf]['interface_status'] = \
                    m.groupdict()['intf_status'].lower()
                continue

            # Internet address is FE80::5054:FF:FE7C:DC70/10
            p3 = re.compile(r'^Internet +address +is +(?P<ip>[\w\/\.\:]+)$')
            m = p3.match(line)
            if m:                
                ret_dict['vrf'][vrf]['interface'][intf]['interface_adress'] = \
                    m.groupdict()['ip']
                continue

            # MLD is enabled on interface
            p4 = re.compile(r'^MLD +is +(?P<status>\w+) +on +interface$')
            m = p4.match(line)
            if m:
                status = m.groupdict()['status'].lower()
                ret_dict['vrf'][vrf]['interface'][intf]['enable'] = True if \
                    'enable' in status else False
                continue
            
            # Current MLD version is 2
            p5 = re.compile(r'^Current +MLD +version +is +(?P<ver>\d+)$')
            m = p5.match(line)
            if m:                
                ret_dict['vrf'][vrf]['interface'][intf]['version'] = int(m.groupdict()['ver'])
                continue

            # MLD query interval is 366 seconds
            p7 = re.compile(r'^MLD +query +interval +is +(?P<query_interval>\d+) +seconds$')
            m = p7.match(line)
            if m:                
                ret_dict['vrf'][vrf]['interface'][intf]['query_interval'] = \
                    int(m.groupdict()['query_interval'])
                continue

            # MLD querier timeout is 740 seconds
            p9 = re.compile(r'^MLD +querier +timeout +is +'
                             r'(?P<timeout>\d+) +seconds$')
            m = p9.match(line)
            if m:                
                ret_dict['vrf'][vrf]['interface'][intf]['querier_timeout'] = \
                    int(m.groupdict()['timeout'])
                continue

            # MLD max query response time is 16 seconds
            p11 = re.compile(r'^MLD +max +query +response +time +is +'
                             r'(?P<time>\d+) +seconds$')
            m = p11.match(line)
            if m:                
                ret_dict['vrf'][vrf]['interface'][intf]['query_max_response_time'] = \
                    int(m.groupdict()['time'])
                continue

            # Last member query response interval is 1 seconds
            p13 = re.compile(r'^Last +member +query +response +interval +is '
                              r'+(?P<time>\d+) +(seconds|ms)$')
            m = p13.match(line)
            if m:                
                ret_dict['vrf'][vrf]['interface'][intf]['last_member_query_interval'] = \
                    int(m.groupdict()['time'])
                continue

            # Inbound MLD access group is: test
            p14 = re.compile(r'^Inbound +MLD +access +group +is *: +(?P<group_policy>\S+)$')
            m = p14.match(line)
            if m:                
                ret_dict['vrf'][vrf]['interface'][intf]['group_policy'] = \
                    m.groupdict()['group_policy']
                continue

            # MLD activity: 11 joins, 2 leaves
            p15 = re.compile(r'^MLD +activity: +(?P<joins>\d+) +joins, +(?P<leaves>\d+) +leaves$')
            m = p15.match(line)
            if m:
                if 'counters' not in ret_dict['vrf'][vrf]['interface'][intf]:
                    ret_dict['vrf'][vrf]['interface'][intf]['counters'] = {}
                ret_dict['vrf'][vrf]['interface'][intf]['counters']['joins'] = \
                    int(m.groupdict()['joins'])
                ret_dict['vrf'][vrf]['interface'][intf]['counters']['leaves'] = \
                    int(m.groupdict()['leaves'])
                continue

            # Interface State Limit : 0 active out of 6400 max
            p16 = re.compile(r'^Interface +State +Limit *: +'
                              r'(?P<active>\d+) +active +out +of +(?P<max>\d+) +max$')
            m = p16.match(line)
            if m:                
                ret_dict['vrf'][vrf]['interface'][intf]['max_groups'] = int(m.groupdict()['max'])
                ret_dict['vrf'][vrf]['interface'][intf]['active_groups'] = int(m.groupdict()['active'])
                continue

            # MLD querying router is FE80::5054:FF:FE7C:DC70 (this system)
            p20 = re.compile(r'^MLD +querying +router +is +(?P<querier>[\w\.\:]+)'
                              r'(?P<dummy> *\([\w\s]+\))?$')
            m = p20.match(line)
            if m:
                ret_dict['vrf'][vrf]['interface'][intf]['querier'] = \
                    m.groupdict()['querier']
                if "this system" in str(m.groupdict()['dummy']):
                    ret_dict['vrf'][vrf]['interface'][intf]['query_this_system'] = True
                continue

        return ret_dict



# ==================================================
# Parser for 'show ipv6 mld groups detail'
# Parser for 'show ipv6 mld vrf <WORD> groups detail'
# ==================================================

class ShowIpv6MldGroupsDetailSchema(MetaParser):
    """Schema for:
        show ipv6 mld groups detail
        show ipv6 mld vrf <vrf> groups detail"""

    schema = {'vrf':
                {Any(): {
                    'interface': {
                        Any(): {
                            Optional('join_group'): {
                                Any(): {
                                    'group': str,
                                    'source': str,
                                }
                            },
                            Optional('static_group'): {
                                Any(): {
                                    'group': str,
                                    'source': str,
                                }
                            },
                            'group': {
                                Any(): {
                                    'up_time': str,
                                    'filter_mode': str,
                                    'host_mode': str,
                                    'last_reporter': str,
                                    Optional('expire'): str,
                                    Optional('source'): {
                                        Any(): {
                                            Optional('expire'): str,
                                            'forward': bool,
                                            Optional('flags'): str,
                                            'up_time': str,
                                        },
                                    },
                                }
                            },
                        }
                    }
                },
            }
        }

class ShowIpv6MldGroupsDetail(ShowIpv6MldGroupsDetailSchema):
    """Parser for:
        show ipv6 mld groups detail
        show ipv6 mld vrf <vrf> groups detail"""

    cli_command = ['show ipv6 mld vrf {vrf} groups detail', 'show ipv6 mld groups detail']
    exclude = ['expire', 'up_time']


    def cli(self, vrf='', output=None):
        if output is None:
            if vrf:
                cmd = self.cli_command[0].format(vrf=vrf)
            else:
                vrf = 'default'
                cmd = self.cli_command[1]
            out = self.device.execute(cmd)
        else:
            out = output

        # initial variables
        ret_dict = {}

        for line in out.splitlines():
            line = line.strip()

            # Interface:\tVlan211
            line = line.replace('\t', '    ')

            # Interface:        GigabitEthernet1
            p1 = re.compile(r'^Interface: +(?P<intf>[\w\.\-\/]+)$')
            m = p1.match(line)
            if m:
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}

                intf = m.groupdict()['intf']
                if 'interface' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['interface'] = {}
                if intf not in ret_dict['vrf'][vrf]['interface']:
                    ret_dict['vrf'][vrf]['interface'][intf] = {}
                continue

            # Group:                239.1.1.1
            p2 = re.compile(r'^Group: +(?P<group>[\w\.\:]+)$')
            m = p2.match(line)
            if m:
                group = m.groupdict()['group']
                if 'group' not in ret_dict['vrf'][vrf]['interface'][intf]:
                    ret_dict['vrf'][vrf]['interface'][intf]['group'] = {}
                if group not in ret_dict['vrf'][vrf]['interface'][intf]['group']:
                    ret_dict['vrf'][vrf]['interface'][intf]['group'][group] = {}
                continue

            # Host mode:        INCLUDE
            p3 = re.compile(r'^Host +mode: +(?P<host_mode>\w+)$')
            m = p3.match(line)
            if m:
                host_mode = m.groupdict()['host_mode']
                ret_dict['vrf'][vrf]['interface'][intf]['group'][group]['host_mode'] = host_mode.lower()
                continue

            # Uptime:                00:05:06
            p4 = re.compile(r'^Uptime: +(?P<up_time>[\w\:\.]+)$')
            m = p4.match(line)
            if m:
                up_time = m.groupdict()['up_time']
                ret_dict['vrf'][vrf]['interface'][intf]['group'][group]['up_time'] = up_time
                continue

            # Router mode:        INCLUDE
            # Router mode:        EXCLUDE (Expires: 00:06:06)
            p5 = re.compile(r'^Router +mode: +(?P<filter_mode>\w+)'
                             r'( *\(Expires: +(?P<expire>[\w\.\:]+)\))?$')
            m = p5.match(line)
            if m:
                filter_mode = m.groupdict()['filter_mode']
                expire = m.groupdict()['expire']
                ret_dict['vrf'][vrf]['interface'][intf]['group'][group]['filter_mode'] = filter_mode.lower()
                if expire:
                    ret_dict['vrf'][vrf]['interface'][intf]['group'][group]['expire'] = expire
                continue

            # Last reporter:        10.1.2.1
            p6 = re.compile(r'^Last +reporter: +(?P<last_reporter>[\w\.\:]+)$')
            m = p6.match(line)
            if m:
                last_reporter = m.groupdict()['last_reporter']
                ret_dict['vrf'][vrf]['interface'][intf]['group'][group]['last_reporter'] = last_reporter
                continue

            # Source Address                          Uptime    Expires   Fwd  Flags
            p7_1 = re.compile(r'^Source +Address +Uptime +Expires +Fwd +Flags$')
            m = p7_1.match(line)
            if m:
                continue

            # 2001:DB8:2:2::2                         08:13:22  00:06:42  Yes  Remote Local 2D
            p7 = re.compile(r'^(?P<source>[\w\.\:]+) +'
                             r'(?P<up_time>[\w\.\:]+) +'
                             r'(?P<expire>[\w\.\:]+) +'
                             r'(?P<forward>\w+) +'
                             r'(?P<flags>[\w\s]+)$')
            m = p7.match(line)
            if m:
                source = m.groupdict()['source']
                flags = m.groupdict()['flags']


                # group structure
                if 'source' not in ret_dict['vrf'][vrf]['interface'][intf]['group'][group]:
                    ret_dict['vrf'][vrf]['interface'][intf]['group'][group]['source'] = {}
                if source not in ret_dict['vrf'][vrf]['interface'][intf]['group'][group]['source']:
                    ret_dict['vrf'][vrf]['interface'][intf]['group'][group]['source'][source] = {}

                ret_dict['vrf'][vrf]['interface'][intf]['group'][group]\
                    ['source'][source]['up_time'] = m.groupdict()['up_time']

                ret_dict['vrf'][vrf]['interface'][intf]['group'][group]\
                    ['source'][source]['expire'] = m.groupdict()['expire']

                ret_dict['vrf'][vrf]['interface'][intf]['group'][group]\
                    ['source'][source]['forward'] = True \
                        if m.groupdict()['forward'].lower() == 'yes' else False

                ret_dict['vrf'][vrf]['interface'][intf]['group'][group]\
                    ['source'][source]['flags'] = flags

                flag_list = flags.lower().split()
                if ('4' in flag_list or '2d' in flag_list) and 'e' in flag_list:
                    keys = ['join_group', 'static_group']
                elif '4' in flag_list or '2d' in flag_list:
                    keys = ['join_group']
                elif 'e' in flag_list:
                    keys = ['static_group']
                else:
                    keys = []

                # join_group or static_group structure
                if keys:
                    static_join_group = group + ' ' + source
                    for key in keys:
                        if key not in ret_dict['vrf'][vrf]['interface'][intf]:
                            ret_dict['vrf'][vrf]['interface'][intf][key] = {}

                        if static_join_group not in ret_dict['vrf'][vrf]['interface'][intf][key]:
                            ret_dict['vrf'][vrf]['interface'][intf][key][static_join_group] = {}

                        ret_dict['vrf'][vrf]['interface'][intf][key][static_join_group]['group'] = group
                        ret_dict['vrf'][vrf]['interface'][intf][key][static_join_group]['source'] = source

        return ret_dict

# ========================================================
# Parser for 'show ipv6 mld ssm-map'
# ========================================================

class ShowIpv6MldSsmSchema(MetaParser):
    """
    Schema for 'show ipv6 mld ssm-map'
    """
    schema = {'ssm_mapping': str,
              'dns_lookup': str
        }

class ShowIpv6MldSsm(ShowIpv6MldSsmSchema):
    """
    Parser for 'show ipv6 mld ssm-map'
    """
    cli_command = 'show ipv6 mld ssm-map'
    def cli(self,output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # SSM Mapping : Enabled
        p1 = re.compile(r'^SSM Mapping *: *(?P<ssm_mapping>\w+)$')

        # DNS Lookup : Enabled
        p2 = re.compile(r'^DNS Lookup *: *(?P<dns_lookup>\w+)$')

        # initial variables
        ret_dict = {}
        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                ret_dict.update(m.groupdict())
                continue

            m = p2.match(line)
            if m:
                ret_dict.update(m.groupdict())
                continue

        return ret_dict

# ========================================================
# Parser for 'show ipv6 mld ssm-map <WROD>'
# Parser for 'show ipv6 mld vrf <WORD> ssm-map <WORD>'
# ========================================================

class ShowIpv6MldSsmMapSchema(MetaParser):
    """Schema for:
        show ipv6 mld ssm-map <group_address>
        show ipv6 mld vrf <vrf> ssm-map <group_address>"""

    schema = {'vrf':
                {Any(): {
                    'ssm_map': {
                        Any(): {
                            'source_addr': str,
                            'group_address': str,
                            'database': str,
                            'group_mode_ssm': bool
                        }
                    }
                },
            }
        }

class ShowIpv6MldSsmMap(ShowIpv6MldSsmMapSchema):
    """Parser for:
        show ipv6 mld ssm-map <group_address>
        show ipv6 mld vrf <vrf> ssm-map <group_address>"""

    cli_command = ['show ipv6 mld vrf {vrf} ssm-map {group}', 'show ipv6 mld ssm-map {group}']

    def cli(self, group, vrf='', output=None):
        if output is None:
            if vrf:
                cmd = self.cli_command[0].format(vrf=vrf, group=group)
            else:
                vrf = 'default'
                cmd = self.cli_command[1].format(group=group)
            out = self.device.execute(cmd)
        else:
            out = output

        # initial variables
        ret_dict = {}
        group_address = ''
        mode = database = None

        for line in out.splitlines():
            line = line.strip()

            # Group address: FF35:1::1
            p1 = re.compile(r'^Group +address *: +(?P<group_address>[\w\.\:]+)$')
            m = p1.match(line)
            if m:
                group_address = m.groupdict()['group_address']
                continue

            # Database     : STATIC
            p2 = re.compile(r'^Database *: +(?P<database>\w+)$')
            m = p2.match(line)
            if m:
                database = m.groupdict()['database'].lower()
                continue

            # Group mode ssm : FALSE
            p4 = re.compile(r'^Group +mode +ssm *: +(?P<mode>\w+)$')
            m = p4.match(line)
            if m:
                mode = False if 'false' in m.groupdict()['mode'].lower() else True
                continue

            # Source list  : 2001:DB8:1:1::1
            p3 = re.compile(r'^Source +list *: +(?P<source_addr>[\w\.\:]+)$')
            m = p3.match(line)
            if m:
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}
                if 'ssm_map' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['ssm_map'] = {}

                source_addr = m.groupdict()['source_addr']
                ssm = source_addr + ' ' + group_address
                if ssm not in ret_dict['vrf'][vrf]['ssm_map']:
                    ret_dict['vrf'][vrf]['ssm_map'][ssm] = {}

                ret_dict['vrf'][vrf]['ssm_map'][ssm]['source_addr'] = source_addr

                if group_address:
                    ret_dict['vrf'][vrf]['ssm_map'][ssm]['group_address'] = group_address

                if database:
                    ret_dict['vrf'][vrf]['ssm_map'][ssm]['database'] = database.lower()

                if mode != None:
                    ret_dict['vrf'][vrf]['ssm_map'][ssm]['group_mode_ssm'] = mode
                continue

            # 2001:DB8::3
            p3_1 = re.compile(r'^(?P<source_addr>[\w\.\:]+)$')
            m = p3_1.match(line)
            if m:
                source_addr = m.groupdict()['source_addr']
                ssm = source_addr + ' ' + group_address
                if ssm not in ret_dict['vrf'][vrf]['ssm_map']:
                    ret_dict['vrf'][vrf]['ssm_map'][ssm] = {}

                ret_dict['vrf'][vrf]['ssm_map'][ssm]['source_addr'] = source_addr

                if group_address:
                    ret_dict['vrf'][vrf]['ssm_map'][ssm]['group_address'] = group_address

                if database:
                    ret_dict['vrf'][vrf]['ssm_map'][ssm]['database'] = database.lower()

                if mode != None:
                    ret_dict['vrf'][vrf]['ssm_map'][ssm]['group_mode_ssm'] = mode
                continue

        return ret_dict


#====================================================
# Parser for show ipv6 mld snooping address count
#====================================================

class ShowIpv6MldSnoopingAddressCountSchema(MetaParser):
    schema = {
        'total_number_of_groups': {
            'mld_groups_count': int
        }
    }


class ShowIpv6MldSnoopingAddressCount(ShowIpv6MldSnoopingAddressCountSchema):

    cli_command = 'show ipv6 mld snooping address count'

    def cli(self, output=None):

        if not output:
            output = self.device.execute(self.cli_command)

        # Total number of groups:   551
        p1 = re.compile(r'^Total\s+number\s+of\s+groups\:\s+(?P<mld_groups_count>\d+)$')

        ret_dict = {}
        for line in output.splitlines():
            line = line.strip()

            # Total number of groups:   551
            m = p1.match(line)
            if m:
                group = m.groupdict()
                igmp_groups_count_dict = ret_dict.setdefault('total_number_of_groups', {})
                igmp_groups_count_dict['mld_groups_count'] = int(group['mld_groups_count'])

        return ret_dict


class ShowIpv6MldGroupsSummarySchema(MetaParser):
    '''Schema for show ipv6 mld groups summary'''
    schema = {
        'route': {
            Any(): {
                'routes': int
            }
        }
    }


class ShowIpv6MldGroupsSummary(ShowIpv6MldGroupsSummarySchema):
    '''Parser for show ipv6 mld groups summary'''

    cli_command = 'show ipv6 mld groups summary'

    def cli(self, output=None):

        if not output:
            output = self.device.execute(self.cli_command)

        # No. of (*,G) routes = 9
        p1 = re.compile(r'^No\. of \((?P<route>.+)\) routes =\s(?P<routes>\d+)$')

        ret_dict = dict()
        for line in output.splitlines():
            line = line.strip()

            # No. of (S,G) routes = 0
            m = p1.match(line)
            if m:
                group = m.groupdict()
                route_dict = ret_dict.setdefault('route', {}).setdefault(group['route'], {})
                route_dict.setdefault('routes', int(group['routes']))

        return ret_dict

# ============================================
# Schema for 'show ipv6 mld snooping querier'
# ============================================
class ShowIpv6MldSnoopingQuerierSchema(MetaParser):
    """ Schema for show ipv6 mld snooping querier """
    schema = {
        'vlan': {
            int: {
                'ipv6_address': {
                    str: {
                        'version': str,
                        'port': str,
                    },
                }
            },
        },
    }

# ==================================================
# Parser for 'show ipv6 mld snooping querier'
# ==================================================
class ShowIpv6MldSnoopingQuerier(ShowIpv6MldSnoopingQuerierSchema):
    """ Parser for show ipv6 mld snooping querier """

    cli_command = "show ipv6 mld snooping querier"

    def cli(self, output=None):

        if output is None:
            output = self.device.execute(self.cli_command)

        # initial return dictionary
        parsed_dict = {}

        # initial regexp pattern
        #101       FE80::A      v2         Switch
        p1 = re.compile(r'^[a-zA-Z\/\s-]*(?P<vlan_id>\d+)\s+(?P<ip_addr>[0-9a-fA-F\.:]+)\s+(?P<version>[v\d,]+)\s+(?P<port>[\w:\/\s]+)$')
        #101       FE80:0:9D36:F78B:A8BB:CCFF:FE00:400
        p2 = re.compile(r'^[a-zA-Z\/\s-]*(?P<vlan_id>\d+)\s+(?P<ip_addr>[0-9a-fA-F\.:]+)\s*\\*$')
        #v2         Switch
        p3 = re.compile(r'^(?P<version>v[\d,]+)\s+(?P<port>[\w:\/\s]+)$')

        for line in output.splitlines():
            line = line.strip()

            #101       FE80::A      v2         Switch
            m = p1.match(line)
            if m:
                group = m.groupdict()
                parsed_dict.setdefault('vlan', {})
                vlan = parsed_dict['vlan'].setdefault(int(group['vlan_id']), {})
                vlan_ip = vlan.setdefault('ipv6_address', {})
                vlan_ip.update(
                    {
                        group['ip_addr']: {
                            'version': group['version'],
                            'port': group['port']
                    }
                })
                continue

            #101       FE80:0:9D36:F78B:A8BB:CCFF:FE00:400
            m = p2.match(line)
            if m:
                group = m.groupdict()
                ip_addr = group['ip_addr']
                vlan_id = int(group['vlan_id'])
                continue

            #v2         Switch
            m = p3.match(line)
            if m:
                group = m.groupdict()
                parsed_dict.setdefault('vlan', {})
                vlan = parsed_dict['vlan'].setdefault(vlan_id, {})
                vlan_ip = vlan.setdefault('ipv6_address', {})
                vlan_ip.update(
                    {
                        ip_addr: {
                            'version': group['version'],
                            'port': group['port']
                    }
                })
                continue

        return parsed_dict

# ========================================================
# Parser for 'show ipv6 mld groups'
# ========================================================

class ShowIpv6MldGroupsSchema(MetaParser):
    """
    Schema for 'show ipv6 mld groups'
    """

    schema = {
        'mld_groups': {
            Any(): {
                'intf': str,
                'uptime': str,
                'expires': str,
            },
        }
    }

class ShowIpv6MldGroups(ShowIpv6MldGroupsSchema):
    """
    Parser for 'show ipv6 mld groups'
    """
    cli_command = 'show ipv6 mld groups'

    def cli(self, output=None):
        if output is None:
            output = self.device.execute(self.cli_command)

        # initial variables
        mld_dict = {}
        
        # FF1E::         Vlan10         00:00:27  not used
        # FF1E::1        Te1/0/3        00:01:49  00:01:46
        # FF8E::4        Vlan100        1d00h     00:03:11
        p1 = re.compile(r'(?P<group>[\w\.\:]+) +(?P<intf>[\w\.\/\-]+) +(?P<uptime>[\d\:dh]+) +(?P<expires>(?:[\d\:]+)|(?:[\w\s]+)|(?:not used))$')

        for line in output.splitlines():
            line = line.strip()

            # FF1E::         Vlan10         00:00:27  not used
            # FF1E::1        Te1/0/3        00:01:49  00:01:46
            m = p1.match(line)
            if m:
                group = m.groupdict()
                mld_dict.setdefault('mld_groups', {}).setdefault(group.pop('group'), group)
        return mld_dict

class ShowPlatformSoftwareMldSnoopingGroupsCountSchema(MetaParser):
    schema = {
        Optional('ipv6_mld_snooping_entries'): int,
        Optional('total_group_count'): int,
        Optional('total_stub_group_count'): int
        }

class ShowPlatformSoftwareMldSnoopingGroupsCount(ShowPlatformSoftwareMldSnoopingGroupsCountSchema):

    cli_command = [
                  'show platform software fed {switch} {active} ipv6 mld snooping groups count',
                  'show platform software fed {active} ipv6 mld snooping groups count'
                  ]

    def cli(self, output=None, switch='', active=''):
        if output is None:
            if switch:
                cmd = self.cli_command[0].format(switch=switch, active=active)
            else:
                cmd = self.cli_command[1].format(active=active)
            output = self.device.execute(cmd)
        dict_count = {}
        # Total number of entries:8000
        p1 = re.compile(r'^Total\s+number\s+of\s+entries\:(?P<ipv6_mld_snooping_entries>\d+)$')

        # Total Group Count       : 9789
        p2 = re.compile(r'(Total Group Count +\: +(?P<total_group_count>\d+))')

        # Total Stub Group Count  : 9787
        p3 = re.compile(r'(Total Stub Group Count +\: +(?P<total_stub_group_count>\d+))')

        for line in output.splitlines():
            line = line.strip()

            # Number of lines which match regexp = 240
            m = p1.match(line)
            if m:
                groups = m.groupdict()
                count = int(groups['ipv6_mld_snooping_entries'])
                dict_count['ipv6_mld_snooping_entries'] = count
                continue

            # Total Group Count       : 9789
            m = p2.match(line)
            if m:
                group = m.groupdict()
                dict_count['total_group_count'] = int(group['total_group_count'])
                continue

            # Total Stub Group Count  : 9787
            m = p3.match(line)
            if m:
                group = m.groupdict()
                dict_count['total_stub_group_count'] = int(group['total_stub_group_count'])
                continue

        return dict_count
