import sys
from ConfigParser import SafeConfigParser
from optparse import OptionParser

from psychsim.pwl import *
from psychsim.action import *
from psychsim.world import World,stateKey,actionKey
from psychsim.agent import Agent

def scenarioCreationUseCase(sCost=1000,fCost=1000,sCollapse=0.1,fCollapse=0.1):
    """
    An example of how to create a scenario
    @param sCost: number of troops Sylvania loses in battle
    @param fCost: number of troops Sylvania loses in battle
    @return: the scenario created
    @rtype: L{World}
    """
    # Create scenario
    world = World()

    # Agents
    free = Agent('Freedonia')
    world.addAgent(free)
    sylv = Agent('Sylvania')
    world.addAgent(sylv)

    # User state
    world.defineState(free.name,'troops',int,lo=0,hi=500000,
                      description='Number of troops %s has left' % (free.name))
    free.setState('troops',381940)
    world.defineState(free.name,'territory',int,lo=0,hi=100,
                      description='Percentage of disputed territory currently owned by %s' % (free.name))
    free.setState('territory',13)  # Percentage of disputed territory
    world.defineState(free.name,'rejected',bool,
                      description='Has %s just rejected the last offer from %s' % (sylv.name,free.name))
    free.setState('rejected',False)

    # Agent state
    world.defineState(sylv.name,'troops',int,lo=0,hi=500000,
                      description='Number of troops %s has left' % (sylv.name))
    sylv.setState('troops',461432)
    world.defineState(sylv.name,'offered',int,lo=0,hi=100,
                      description='Percentage of disputed territory that %s last offered to %s' % (free.name,sylv.name))
    sylv.setState('offered',0)  # Percentage of disputed territory offered *to* me

    # World state
    world.defineState(None,'treaty',bool,
                      description='Have the two sides reached an agreement?')
    world.setState(None,'treaty',False)
    # Stage of negotiation, illustrating the use of an enumerated state feature
    world.defineState(None,'phase',list,['offer','respond','rejection','end','paused'],
                      description='The current stage of the negotiation game')
    world.setState(None,'phase','paused')
    # Round of negotiation
    world.defineState(None,'round',int,description='The current round of the negotiation')
    world.setState(None,'round',0)

    # Game over if there is a treaty
    world.addTermination(makeTree({'if': trueRow(stateKey(None,'treaty')),
                                   True: True, False: False}))
    # Game over if Freedonia has no territory
    world.addTermination(makeTree({'if': thresholdRow(stateKey(free.name,'territory'),1),
                                   True: False, False: True}) )
    # Game over if Freedonia has all the territory
    world.addTermination(makeTree({'if': thresholdRow(stateKey(free.name,'territory'),99),
                                   True: True, False: False})) 
    # Game over if number of rounds exceeds limit
    world.addTermination(makeTree({'if': thresholdRow(stateKey(None,'rounds'),14),
                                   True: True, False: False}))

    # Turn order: Uncomment the following if you want agents to act in parallel
#    world.setOrder([{free.name,sylv.name}])
    # Turn order: Uncomment the following if you want agents to act sequentially
    world.setOrder([free.name,sylv.name])

    # User actions
    freeNOP = free.addAction({'verb': 'continue'})
    freeBattle = free.addAction({'verb': 'attack','object': sylv.name})
    freeOffer25 = free.addAction({'verb': 'offer','object': sylv.name,'amount': 25})
    freeOffer50 = free.addAction({'verb': 'offer','object': sylv.name,'amount': 50})
    freeOffer75 = free.addAction({'verb': 'offer','object': sylv.name,'amount': 75})

    # Agent actions
    sylvNOP = sylv.addAction({'verb': 'continue'})
    sylvBattle = sylv.addAction({'verb': 'attack','object': free.name})
    sylvAccept = sylv.addAction({'verb': 'accept offer','object': free.name})
    sylvReject = sylv.addAction({'verb': 'reject offer','object': free.name})

    # Restrictions on when actions are legal, based on phase of game
    for action in filterActions({'verb': 'offer'},free.actions):
        free.setLegal(action,makeTree({'if': equalRow(stateKey(None,'phase'),'offer'),
                                       True: True,     # Offers are legal in the offer phase
                                       False: False})) # Offers are illegal in all other phases
    free.setLegal(freeNOP,makeTree({'if': equalRow(stateKey(None,'phase'),'rejection'),
                                    True: True,     # Doing nothing is legal only in rejection phase
                                    False: False})) # Doing nothing is illegal in all other phases
    free.setLegal(freeBattle,makeTree({'if': equalRow(stateKey(None,'phase'),'rejection'),
                                       True: True,     # Attacking is legal for Freedonia only in rejection phase
                                       False: False})) # Attacking is illegal for Freedonia in all other phases
    # Once offered, Sylvania can take action
    for action in [sylvBattle,sylvAccept,sylvReject]:
        sylv.setLegal(action,makeTree({'if': equalRow(stateKey(None,'phase'),'respond'),
                                       True: True,     # Sylvania must act in the response phase
                                       False: False})) # Sylvania cannot act in any other phase
    # NOP is legal in exactly opposite situations to all other actions
    sylv.setLegal(sylvNOP,makeTree({'if': equalRow(stateKey(None,'phase'),'end'),
                                    True: True,     # Sylvania does not do anything in the null phase after Freedonia responds to rejection
                                    False: False})) # Sylvania must act in its other phases

    # Goals for Freedonia
    goalFTroops = maximizeFeature(stateKey(free.name,'troops'))
    free.setReward(goalFTroops,1.)
    goalFTerritory = maximizeFeature(stateKey(free.name,'territory'))
    free.setReward(goalFTerritory,10.)

    # Goals for Sylvania
    goalSTroops = maximizeFeature(stateKey(sylv.name,'troops'))
    sylv.setReward(goalSTroops,1.)
    goalSTerritory = minimizeFeature(stateKey(free.name,'territory'))
    sylv.setReward(goalSTerritory,10.)

    # Horizons
    free.setHorizon(2)
    sylv.setHorizon(2)

    # Levels of belief
    free.setRecursiveLevel(2)
    sylv.setRecursiveLevel(2)

    # Dynamics of battle
    freeTroops = stateKey(free.name,'troops')
    freeTerr = stateKey(free.name,'territory')
    sylvTroops = stateKey(sylv.name,'troops')
    # Effect of fighting
    for action in filterActions({'verb': 'attack'},free.actions | sylv.actions):
        # Effect on troops (cost of battle)
        tree = makeTree(incrementMatrix(freeTroops,-fCost))
        world.setDynamics(free.name,'troops',action,tree)
        tree = makeTree(incrementMatrix(sylvTroops,-sCost))
        world.setDynamics(sylv.name,'troops',action,tree)
        # Effect on territory (probability of collapse)
        tree = makeTree({'distribution': [
                    ({'distribution': [(setToConstantMatrix(freeTerr,100),1.-fCollapse), # Sylvania collapses, Freedonia does not
                                       (noChangeMatrix(freeTerr),         fCollapse)]},  # Both collapse
                     sCollapse),
                    ({'distribution': [(setToConstantMatrix(freeTerr,0),fCollapse),      # Freedonia collapses, Sylvania does not
                                       (noChangeMatrix(freeTerr),       1.-fCollapse)]}, # Neither collapse
                     1.-sCollapse)]})
        world.setDynamics(free.name,'territory',action,tree)
        # If Freedonia attacks, negates offer
        tree = makeTree(setToConstantMatrix(stateKey(sylv.name,'offered'),0))
        world.setDynamics(sylv.name,'offered',freeBattle,tree)

    # Dynamics of offers
    atom =  Action({'subject': free.name,'verb': 'offer','object': sylv.name})
    offer = stateKey(atom['object'],'offered')
    amount = actionKey('amount')
    tree = makeTree({'if': trueRow(stateKey(None,'treaty')),
                     True: noChangeMatrix(offer),
                     False: setToConstantMatrix(offer,amount)})
    world.setDynamics(atom['object'],'offered',atom,tree)
    # Making an offer resets "rejected" flag
    tree = makeTree(setFalseMatrix(stateKey(free.name,'rejected')))
    world.setDynamics(free.name,'rejected',atom,tree)

    # Dynamics of treaties
    for action in filterActions({'verb': 'accept offer'},free.actions | sylv.actions):
        # Accepting an offer means that there is now a treaty
        tree = makeTree({'if': trueRow(stateKey(None,'treaty')),
                         True: noChangeMatrix(stateKey(None,'treaty')),
                         False: setTrueMatrix(stateKey(None,'treaty'))})
        world.setDynamics(None,'treaty',action,tree)
        # Accepting offer sets territory
        offer = stateKey(action['subject'],'offered')
        territory = stateKey(free.name,'territory')
        if action['subject'] == free.name:
            # Freedonia accepts sets territory to last offer
            tree = makeTree({'if': thresholdRow(offer,0.),
                             True: {'if': trueRow(stateKey(None,'treaty')),
                                    True: noChangeMatrix(territory),
                                    False: setToFeatureMatrix(territory,offer)},
                             False: noChangeMatrix(territory)})
            world.setDynamics(free.name,'territory',action,tree)
        else:
            # Sylvania accepts sets territory to 1-last offer
            tree = makeTree({'if': thresholdRow(offer,0.),
                             True: setToFeatureMatrix(territory,offer,pct=-1.,shift=100.),
                             False: noChangeMatrix(territory)})
            world.setDynamics(free.name,'territory',action,tree)

    # Dynamics of rejection
    tree = makeTree(setTrueMatrix(stateKey(free.name,'rejected')))
    world.setDynamics(free.name,'rejected',sylvReject,tree)

    # Dynamics of resetting offer
    tree = makeTree(setToConstantMatrix(stateKey(sylv.name,'offered'),0))
    world.setDynamics(sylv.name,'offered',freeNOP,tree)

    # Dynamics of phase
    # OFFER -> RESPOND
    atom =  Action({'subject': free.name,'verb': 'offer','object': sylv.name})
    tree = makeTree(setToConstantMatrix(stateKey(None,'phase'),'respond'))
    world.setDynamics(None,'phase',atom,tree)
    # RESPOND -> REJECTION
    atom =  Action({'subject': sylv.name,'verb': 'reject offer','object': free.name})
    tree = makeTree(setToConstantMatrix(stateKey(None,'phase'),'rejection'))
    world.setDynamics(None,'phase',atom,tree)
    # RESPOND -> OFFER
    for verb in ['attack','accept offer']:
        atom =  Action({'subject': sylv.name,'verb': verb,'object': free.name})
        tree = makeTree(setToConstantMatrix(stateKey(None,'phase'),'offer'))
        world.setDynamics(None,'phase',atom,tree)
        tree = makeTree(incrementMatrix(stateKey(None,'round'),1))
        world.setDynamics(None,'round',atom,tree)
    # REJECTION -> END
    for verb in ['attack','continue']:
        atom =  Action({'subject': free.name,'verb': verb,'object': sylv.name})
        tree = makeTree(setToConstantMatrix(stateKey(None,'phase'),'end'))
        world.setDynamics(None,'phase',atom,tree)
    # END -> OFFER
    atom =  Action({'subject': sylv.name,'verb': 'continue','object': free.name})
    tree = makeTree(setToConstantMatrix(stateKey(None,'phase'),'end'))
    world.setDynamics(None,'phase',atom,tree)
    tree = makeTree(incrementMatrix(stateKey(None,'round'),1))
    world.setDynamics(None,'round',atom,tree)
    
    # # Models of Freedonia
    # free.addModel('dove',R={goalFTroops: 1e-4,goalFTerritory: 0.1},level=1,rationality=0.01)
    # free.addModel('true',level=1,rationality=0.01)
    # free.addModel('hawk',R={goalFTroops: 1e-4,goalFTerritory: 0.3},level=1,rationality=0.01)
    # world.setMentalModel(sylv.name,free.name,{'true': 0.6,'dove': 0.3,'hawk': 0.1})
    return world

def scenarioSimulationUseCase(world,offer=10,rounds=1,debug=1):
    """
    @param offer: the initial offer for Freedonia to give (default is 10)
    @type offer: int
    @param rounds: the number of complete rounds, where a round is two turns each, following Powell (default is 1)
    @type rounds: int
    @param debug: the debug level to use in explanation (default is 1)
    @type debug: int
    """
    free = world.agents['Freedonia']
    sylv = world.agents['Sylvania']
    if options.debug > 0:
        world.printState()

    for t in range(rounds*2):
        assert len(world.state) == 1
        if not world.terminated(world.state.domain()[0]):
            if t == 0:
                # Force Freedonia to make low offer in first step
                world.explain(world.step({free.name: Action({'subject':free.name,'verb':'offer','object': sylv.name,'amount': offer})}),options.debug)
            else:
                # Freedonia is free to choose
                world.explain(world.step(),options.debug)
            world.state.select()
            if options.debug > 0:
                world.printState()
                # Display Sylvania's posterior beliefs
                # sylv.printBeliefs()

        assert len(world.state) == 1
        if not world.terminated(world.state.domain()[0]):
            # Sylvania free to decide in second step
            world.explain(world.step(),options.debug)
            world.state.select()
            if options.debug > 0:
                world.printState()

if __name__ == '__main__':
    # Grab command-line arguments
    parser = OptionParser()
    # Optional argument that sets the level of explanations when running the simulation
    parser.add_option('-d','--debug',action='store',
                      dest='debug',type='int',default=1,
                      help='level of explanation detail [default: %default]')
    # Optional argument that sets the initial offer that Freedonia will make
    parser.add_option('-i','--initial',action='store',
                      dest='offer',type='int',default=10,
                      help='initial offer to try [default: %default]')
    # Optional argument that sets the number of rounds to play
    parser.add_option('-r','--rounds',action='store',
                      dest='rounds',type='int',default=1,
                      help='number of rounds to play [default: %default]')
    # Optional argument that sets the filename for the output file
    parser.add_option('-o','--output',action='store',type='string',
                      dest='output',default='default',
                      help='scenario file [default: %default]')
    (options, args) = parser.parse_args()
    
    world = scenarioCreationUseCase()

    # Create configuration file
    config = SafeConfigParser()
    config.add_section('Game')
    config.set('Game','rounds','15')
    assert world.agents.has_key('Freedonia')
    config.set('Game','user','Freedonia')
    f = open('default.cfg','w')
    config.write(f)
    f.close()

    # Save scenario to compressed XML file
    world.save(options.output)

    # Test saved scenario
    world = World(options.output)
    scenarioSimulationUseCase(world,options.offer,options.rounds,options.debug)
