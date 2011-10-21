from teamwork.agent.AgentClasses import *
from teamwork.dynamics.pwlDynamics import *
from teamwork.math.Interval import *

from inspect import *
from ship import *

from teamwork.math.probability import Distribution

classHierarchy['World'] = {
    'parent': ['Entity'],
    'state': {'socialWelfare':0.2,
              },
    'dynamics':{'socialWelfare':{'pass':{'class':PWLDynamics,
                                         'args':welfareDynamics()},
                                  },
                },
    'models':{'passive':{'goals':[],
                         'policy':[{'class':'default',
                                    'action':{"type":"wait"}},
                                   ],
                         },
              },
    'model':'passive',
    'depth':0,
    }

classHierarchy['FirstResponder'] = {
    'parent': ['Entity'],
    'state': {'waitTime':0.8,
              'reputation':0.5,
##              'resources':0.5,
              },
    'goals':[{'entity':    ['World'],
              'direction': 'max',
              'type':      'state',
              'key':   'socialWelfare',
              'weight':    0.3},
             {'entity':    ['self'],
              'direction': 'min',
              'type':      'state',
              'key':       'waitTime',
              'weight':    0.4},
             {'entity':    ['self'],
              'direction': 'max',
              'type':      'state',
              'key':   'reputation',
              'weight':    0.3},
             ],
    'actions':{'type':'AND',
               'key':'object',
               'values':[{'type':'generic','value':'Shipper'}],
               'base':{'type':'XOR',
                       'key':'type',
                       'values':[{'type':'literal','value':'inspect'},
##                                 {'type':'literal','value':'hold'},
                                 {'type':'literal','value':'pass'},
                                 ],
                       },
               },
    'dynamics':{'waitTime':{'inspect':{'class':PWLDynamics,
                                             'args':waitTime(.05)},
##                                  'hold':{'class':PWLDynamics,
##                                          'args':waitTime(.05)},
                                  'bust':{'class':PWLDynamics,
                                          'args':waitTime(.05)},
                                  'pass':{'class':PWLDynamics,
                                          'args':waitTime(-.05)},
                              },
                'reputation':{'inspect':{'class':PWLDynamics,
                                         'args':bustDynamics(.01)},
                              'pass':{'class':PWLDynamics,
                                      'args':bustDynamics(-.01)},
                              },
                },
    'beliefs':{'FederalAuthority':{
##    '_trustworthiness':.1,
##    '_likeability':0.,
                      'model':'selfless',
                      },
               'Shipper':{
##    '_trustworthiness':-.3,
##    '_likeability':-.3,
                          'model':'average',
                          'containerDanger':Distribution({0.:0.99,
                                                          0.7:0.01}),
                          },
               'Customer':{
##    '_trustworthiness':-.3,
##    '_likeability':-.3,
                           'model':'good',
                           },
               'World':{'model':'passive'},
               },
    'models': {'gogetter':{'goals':[{'entity':    ['World'],
                                     'direction': 'max',
                                     'type':      'state',
                                     'key':       'socialWelfare',
                                     'weight':    0.4}, 
                                    {'entity':    ['self'],
                                     'direction': 'max',
                                     'type':      'state',
                                     'key':       'reputation',
                                     'weight':    0.4},
                                    {'entity':    ['self'],
                                     'direction': 'min',
                                     'type':      'state',
                                     'key':       'waitTime',
                                     'weight':    0.2},],
                         'policy': [],
                         },
##               'secure':{'goals':[{'entity':    ['World'],
##                                   'direction': 'max',
##                                   'type':      'state',
##                                   'key':       'socialWelfare',
##                                   'weight':    0.8},
##                                  {'entity':    ['self'],
##                                   'direction': 'min',
##                                   'type':      'state',
##                                   'key':       'waitTime',
##                                   'weight':    0.2},],
##                         'policy': [],
##                         },
               'efficient':{'goals':[{'entity':    ['World'],
                                      'direction': 'max',
                                      'type':      'state',
                                      'key':       'socialWelfare',
                                      'weight':    0.3},
                                     {'entity':    ['self'],
                                      'direction': 'max',
                                      'type':      'state',
                                      'key':       'reputation',
                                      'weight':    0.3},
                                     {'entity':    ['self'],
                                      'direction': 'min',
                                      'type':      'state',
                                      'key':       'waitTime',
                                      'weight':    0.4},],
                            'policy': [],
                       },
               },
    }

classHierarchy['FederalAuthority'] = {
    'parent': ['Entity'],
    'goals':[{'entity':    ['World'],
              'direction': 'max',
              'type':      'state',
              'key':   'socialWelfare',
              'weight':    1.},
             ],
    'beliefs':{'Shipper':{
##    '_trustworthiness':-.3,
##    '_likeability':-.3,
                          'model':'average',
                          'containerDanger':Distribution({0.:0.2,
                                                          0.7:0.8}),
                          },
               'FirstResponder':{
##    '_trustworthiness':0.,
##    '_likeability':0.2,
                                  'model':'gogetter',
                                  'waitTime':0.3,
                                  },
               'World':{'model':'passive',
                        },
               'Customer':{
##    '_trustworthiness':-.3,
##    '_likeability':-.4,
                           'model':'good',
                           },
               },
    'models':{'selfless':{'goals':[{'entity':    ['World'],
                                      'direction': 'max',
                                    'type':      'state',
                                    'key':   'socialWelfare',
                                    'weight':    1.},
                                   ],
                          'policy':[{'class':'default',
                                     'action':{"type":"wait"}},
                                    ],
                          },
              },
    }

classHierarchy['Shipper'] = {
    'parent': ['Entity'],
    'state': {'containerDanger': 0.7,
##            'routeSecurity': 0.,
##              'containerValue':  0.2,
##              'money':          0.3,
##              'fee':            0.,
              },
    'goals': [{'entity':    ['self'],
               'direction': 'max',
               'type':      'state',
               'key':   'money',
               'weight':    1.},
              ],
    'dynamics':{'containerDanger':{'shipThrough':{'class':PWLDynamics,
                                                  'args':shipThrough('containerDanger','routeSecurity')},
                                   'inspect':{'class':PWLDynamics,
                                              'args':zero('containerDanger')},
                                   },
##                'containerValue':{'shipThrough':{'class':PWLDynamics,
##                                                 'args':shipThrough('containerValue')},
##                                  'inspect':{'class':PWLDynamics,
##                                             'args':scale('containerValue',
##                                                          -.01)},
##                                  },
##                'money':{'pass':{'class':PWLDynamics,
##                                 'args':shipThrough('money','containerValue',
##                                                    'object')},
##                         },
                },
    'beliefs':{'FirstResponder':{
##    '_trustworthiness':.1,
##    '_likeability':-.4,
                                  'model':'gogetter',
                                  },
               'FederalAuthority':{
##    '_trustworthiness':-.2,
##    '_likeability':-.5,
                      'model':'selfless',
                      },
               'Customer':{
##    '_trustworthiness':.1,
##    '_likeability':.3,
                           'model':'good',
                           },
               'World':{'model':'passive'},
               },
    'models':{'average':{'goals': [{'entity':    ['self'],
                                    'direction': 'max',
                                    'type':      'state',
                                    'key':   'money',
                                    'weight':    1.},
                                   ],
                         'policy':[{'class':'default',
                                    'action':{"type":"wait"}},
                                   ],
                         },
              },
    }

classHierarchy['Customer'] = {
    'parent': ['Entity'],
    'actions': {'type':'XOR',
                'key':'object',
                'values': [{'type':'generic','value':'Shipper'}],
                'base':{'type':'action',
                        'values':[{'type':'shipThrough'}],
                        },
                },
    'state': {'money': 0.,
              },
    'beliefs':{'FirstResponder':{
##    '_trustworthiness':.1,
##    '_likeability':-.4,
                                  'model':'gogetter',
                                  },
               'FederalAuthority':{
##    '_trustworthiness':-.2,
##    '_likeability':-.5,
                      'model':'selfless',
                      },
               'Shipper':{
##    '_trustworthiness':.1,
##    '_likeability':.3,
                          'model':'average',
                          },
               'World':{'model':'passive'},
               },
    'models':{'good':{'goals':[{'entity':    ['self'],
                                'direction': 'max',
                                'type':      'state',
                                'key':   'money',
                                'weight':    1.},
                               ],
                      'policy':[{'class':'default',
                                 'action':{"type":"wait"}},
                                ],
                      },
              'bad':{'goals': [{'entity':    ['World'],
                                'direction': 'min',
                                'type':      'state',
                                'key':   'socialWelfare',
                                'weight':    1.},
                               ],
                     'policy':[{'class':'default',
                                'action':{"type":"wait"}},
                               ],
                     },
              },
    }

classHierarchy['GoodCustomer'] = {
    'parent': ['Customer'],
    'state': {'containerDanger':0.0,
##              'containerValue':0.5,
              },
    'goals': [{'entity':    ['self'],
               'direction': 'max',
               'type':      'state',
               'key':   'money',
               'weight':    1.},
              ],
    }

classHierarchy['BadCustomer'] = {
    'parent': ['Customer'],
    'state': {'containerDanger':0.7,
##              'containerValue':0.3,
              },
    'goals': [{'entity':    ['World'],
               'direction': 'min',
               'type':      'state',
               'key':   'socialWelfare',
               'weight':    1.},
              ],
    }