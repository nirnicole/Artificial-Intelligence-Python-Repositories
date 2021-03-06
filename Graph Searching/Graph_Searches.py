
import util

class SearchProblem:

  def getStartState(self):
     util.raiseNotDefined()

  def isGoalState(self, state):
     util.raiseNotDefined()

  def getSuccessors(self, state):
     util.raiseNotDefined()

  def getCostOfActions(self, actions):
     util.raiseNotDefined()

def graphSearch(problem, frontierDataStructure):

  startingNode = problem.getStartState()

  if problem.isGoalState(startingNode):
      return []

  #initialize the frontier using the initial state of problem, datastructor depands on the algorithem calling
  frontier = frontierDataStructure
  frontier.push((problem.getStartState(), [], 0))

  #initialize the explored set to be empty
  exploredSet = []

  """
   #loop do
  if the frontier is empty then return failure
  choose a leaf node and remove it from the frontier
  if the node contains a goal state then return the corresponding solution
  add the node to the explored set
  expend the chosen node, adding the resulting nodes to the frontier only if not in the frontier or explored set
  """
  while not frontier.isEmpty():

      currentNode, actions, costs = frontier.pop()

      if currentNode not in exploredSet:
          exploredSet.append(currentNode)

          if problem.isGoalState(currentNode):
              return actions

          for nextNode, action, cost in problem.getSuccessors(currentNode):
              newAction = actions + [action]
              newCostToNode = costs + cost
              frontier.push((nextNode, newAction, newCostToNode))

  util.raiseNotDefined()

def biasedGraphSearch(problem, frontierDataStructure, heuristic):

    startingNode = problem.getStartState()

    if problem.isGoalState(startingNode):
        return []

    # initialize the frontier using the initial state of problem, datastructor depands on the algorithem calling
    # this time with a priorety queue by cost to path
    frontier = frontierDataStructure
    frontier.push((problem.getStartState(), [], 0), heuristic(problem.getStartState(), problem))

    # initialize the explored set to be empty
    exploredSet = []

    while not frontier.isEmpty():

        currentNode, actions, costs = frontier.pop()

        if currentNode not in exploredSet:
            exploredSet.append(currentNode)

            if problem.isGoalState(currentNode):
                return actions

            for nextNode, action, cost in problem.getSuccessors(currentNode):
                newAction = actions + [action]
                newCostToNode = costs + cost
                heuristicCost = newCostToNode + heuristic(nextNode, problem)
                frontier.push((nextNode, newAction, newCostToNode),heuristicCost)

    util.raiseNotDefined()

def depthFirstSearch(problem):
  return  graphSearch(problem, util.Stack())

def breadthFirstSearch(problem):
  return  graphSearch(problem, util.Queue())

def uniformCostSearch(problem):
  return biasedGraphSearch(problem, util.PriorityQueue(), nullHeuristic)

def nullHeuristic(state, problem=None):
  return 0

def aStarSearch(problem, heuristic=nullHeuristic):
  return biasedGraphSearch(problem, util.PriorityQueue(), heuristic)
