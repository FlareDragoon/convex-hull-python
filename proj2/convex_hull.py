from cmath import sqrt
from contextlib import nullcontext
from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)

	
# This is the method that gets called by the GUI and actually executes
# the finding of the hull

# The Master's Theorum describes the speed of this algorithm as 
# 2t(n/2) + O(n^1), giving it a speed of nlog(n)
	def partition_points(self, point_a, point_b, points):
		# In this function we partition the points into two 
		# arrays based on where they lie in relation to the two 
		# points A and B that constitute our line. From these
		# two partitions we will continue to partiton and make 
		# our miniature hulls that will be combined.
		points_above = []
		points_below = []

		# Should these points form a vertical line, then we return
		# the empty lists because any point partitioned would not 
		# be in the convex hull, nor could you divide to find m.
		if (point_a.x() - point_b.x() == 0):
			return points_above, points_below

		# Use the function y = mx + b from geometry to find where
		# each point falls in relation to the slope of the line.
		m = (point_b.y() - point_a.y()) / (point_b.x() - point_a.x())
		b = -1 * (m * point_a.x()) + point_a.y()

		for point in points:
			if (point.y() > m * point.x() + b):
				points_above.append(point)
			elif (point.y() < m * point.x() + b):
				points_below.append(point)

		# This function ultimately has a time complexity of O(n)
		# due to its simple calculations and the single for loop
		# that covers every point in the list of points.
		# Its space complexity can be summed up as O(2n) because 
		# it will store the list of points and then partition most,
		# if not all, into one of two smaller arrays, the sum of whose
		# size is either less than or equal to the size of the original.
		return points_above, points_below

	def find_distance(self, point_a, point_b, point_c):
		# Points A and B constitute the found line.
		# Point C is the point whose tangiential distance we 
		# are trying to find from the line. 

		# This algorithm ultimately has a space complexity of O(3n)
		# for each point, and a time complexity of O(n) for the 
		# simple operations that it performs.

		# For this algorithm, we use the equation ax +by +c
		# from geometry to find length of the tangent.
		a = point_a.y() - point_b.y()
		b = point_b.x() - point_a.x()
		c = point_a.x() * point_b.y() - point_b.x() * point_a.y()

		# Finally, with those values defined, we use the dot product
		# to calculate the length of the tangents drawn between
		# points A and B.
		dot_product = abs(a * point_c.x() + b * point_c.y() + c) / sqrt(a * a + b * b)
		return dot_product

	def find_farthest_point(self, points, point_a, point_b):
		# Find the point that has the longest tangent in relation 
		# to the otherpoints A and B that constitute a small hull. 
		# This is done using the slope of the tangent.
		# This loop will run through every point in the array of 
		# points passed in and as such will have a time complexity 
		# of O(n) and a space complexity of O(n).
		max_distance = 0
		farthest_point = None
		for point in points:
			distance = self.find_distance(point_a, point_b, point)
			if (distance.real > max_distance):
				max_distance = distance.real
				farthest_point = point
		return farthest_point

	def solve_above_helper(self, point_a, point_b, points, convex_hull):
		# Runs the function to find the next point in the hull 
		# with a space and time complexity of O(n) - see above.
		farthest_point = self.find_farthest_point(points, point_a, point_b)

		# Merge into the convex hull and remove from the list
		# of remaining points to avoid duplicates.
		# Because it is above the tangent, to order the list of 
		# points clockwise we place it before the rightmost point 
		# of the tangent in question.
		temp_index = convex_hull.index(point_b)
		convex_hull.insert(temp_index, farthest_point)
		points.pop(points.index(farthest_point))

		# Partition the remaining points according to whether 
		# are above or below the two tangents after merging into 
		# the new convex hull.
		# Partitioning the points runs at a speed and space complexity
		# of O(n) - see above.
		points_above_a, points_below_a = self.partition_points(point_a, farthest_point, points)
		points_above_b, points_below_b = self.partition_points(farthest_point, point_b, points)

		# Because the original points offered into this array
		# are those who would be above the original hull, then
		# we are only concerned with the two arrays that are 
		# above the two tangents formed above. If no points are in 
		# the array, we skip it since we have found the farthest
		# convex hull point.
		if (points_above_a):
			convex_hull = self.solve_above_helper(point_a, farthest_point, points_above_a, convex_hull)
		if (points_above_b):
			convex_hull = self.solve_above_helper(farthest_point, point_b, points_above_b, convex_hull)

		# The recursion of the function takes the speed of 
		# O(nlogn) because it is split into two sub problems 
		# and constantly halved, per the Master Theorum. 
		# That is, 2t(n/2) + O(n^1)
		# Also runs at a space complexity of O(n), being 
		# multiplied at a constant factor to represent the 
		# array of points and the convex_hull array. At a 
		# worst case, every point is in the convex hull, 
		# resulting in a worst case space consumption of O(2n)
		return convex_hull

	def solve_below_helper(self, point_a, point_b, points, convex_hull):
		# Runs the function to find the next point in the hull 
		# with a space and time complexity of O(n) - see above.
		farthest_point = self.find_farthest_point(points, point_a, point_b)

		# Merge into the convex hull and remove from the list
		# of remaining points to avoid duplicates.
		# Because it is below the tangent, to order the list of 
		# points clockwise we place it after the rightmost point 
		# of the tangent in question.
		temp_index = convex_hull.index(point_b)
		convex_hull.insert(temp_index + 1, farthest_point)
		points.pop(points.index(farthest_point))

		# Partition the remaining points according to whether 
		# are above or below the two tangents after merging into 
		# the new convex hull.
		# Partitioning the points runs at a speed and space complexity
		# of O(n) - see above.
		points_below_a, points_below_a = self.partition_points(point_a, farthest_point, points)
		points_below_b, points_below_b = self.partition_points(farthest_point, point_b, points)

		# Because the original points offered into this array
		# are those who would be below the original hull, then
		# we are only concerned with the two arrays that are 
		# below the two tangents formed above. If no points are in 
		# the array, we skip it since we have found the farthest
		# convex hull point.
		if (points_below_a):
			convex_hull = self.solve_below_helper(point_a, farthest_point, points_below_a, convex_hull)
		if (points_below_b):
			convex_hull = self.solve_below_helper(farthest_point, point_b, points_below_b, convex_hull)

		# The recursion of the function takes the speed of 
		# O(nlogn) because it is split into two sub problems 
		# and constantly halved, per the Master Theorum. 
		# That is, 2t(n/2) + O(n^1)
		# Also runs at a space complexity of O(n), being 
		# multiplied at a constant factor to represent the 
		# array of points and the convex_hull array. At a 
		# worst case, every point is in the convex hull, 
		# resulting in a worst case space consumption of O(2n)
		return convex_hull

	def solve_hull(self, points):
		# Store points that will form the convex hull in a new 
		# array and pop them from the array of sorted points to 
		# avoid repeats in the convex hull.
		# The following quick methods are speed O(n)
		point_a = points[0]
		point_b = points[len(points)-1]

		convex_hull = []
		convex_hull.append(point_a)
		convex_hull.append(point_b)

		points.pop(0)
		points.pop(len(points)-1)

		# Partition the remaining points into two groups: those 
		# that are above the tangent formed by the rightmost and 
		# leftmost points, and those that will fall below said tangent.
		# Any point that falls on the tangent will be in the center 
		# of the new hull and therefore not be in the convex hull.
		points_above, points_below = self.partition_points(point_a, point_b, points)

		# Call the recursive function on our two sets of points
		# to find all of the points in each that will be a part 
		# of the convex hull
		# The following two function calls constitute the bulk of 
		# the divide and conquer algorithm, recursively dividing 
		# the array of points into two subsets and merging convex 
		# hulls.
		if (points_above):
			convex_hull = self.solve_above_helper(point_a, point_b, points_above, convex_hull)
		if (points_below):
			convex_hull = self.solve_below_helper(point_a, point_b, points_below, convex_hull)

		# Create final hull between the points in convex_hull and 
		# return a list of QLineF objects to be drawn.
		# The ultimate speed is O(partition) + O(recursive), or 
		# O(n) + O(nlogn). The Master's Theorum for the overarching
		# class is described above.
		# The space complexity is O(n), where n is the size of the points
		# array, multiplies by some constant factor C that represents the 
		# size of the convex hull.
		polygon = [QLineF(convex_hull[i],convex_hull[(i+1)%len(convex_hull)]) for i in range(len(convex_hull))]
		return polygon

	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		# SORT THE POINTS BY INCREASING X-VALUE
		points.sort(key=lambda p: p.x())
		t2 = time.time()

		t3 = time.time()
		# this is a polygon of the convex hull
		polygon = self.solve_hull(points)
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))