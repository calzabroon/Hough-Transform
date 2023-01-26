import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
from matplotlib import pyplot as plt
import cv2
from skimage.morphology import skeletonize

#Calum Brown - 18366096
#CS410 - Assignment 2

def Hough(E, rho_range, theta_range):
    # '''E - edge image
    # rho_range = [rho_min, rho_max, rho_delta]
    # theta_range = [theta_min, theta_max, theta_delta]
    # '''  
    
    #TASK 4 Define and initialise the Accumulator array
    #TASK 4.1 use np.arange to create an explicit list of theta values (i.e. [theta_min, theta_min + theta_delta,theta_min + 2*theta_delta, ... ])
    theta_length = int((theta_range[1] - theta_range[0])/theta_range[2])
    counter = 0
    theta_accumulator= np.array([])#creates epmty array
    for counter in range(theta_length + 1):
        theta_accumulator = np.append(theta_accumulator, theta_range[0] + counter*theta_range[2]) #implements [theta_min, theta_min + theta_delta,theta_min + 2*theta_delta, ... ]
    #print('theta_accumulator: ', theta_accumulator)


    #TASK 4.2 use np.arange to create an explicit list of rho values (i.e. [rho_min, rho_min + rho_delta, rho_min + 2*rho_delta, ... ])
    rho_length = int((rho_range[1] - rho_range[0])/rho_range[2])
    counter = 0
    rho_accumulator = np.array([])
    for counter in range(rho_length + 1):
        rho_accumulator = np.append(rho_accumulator, rho_range[0] + counter*rho_range[2])#implements [rho_min, rho_min + rho_delta, rho_min + 2*rho_delta, ... ] 
    
    #print('rho_accumulator: ', rho_accumulator)

    # Construct Accumulator
    #TASK 4.3 use np.zeros to create an accumulator array of the correct dimension
    Acc = np.zeros((rho_length + 1, theta_length + 1))# accumulator is size of rholength and thetalength
    
    '''reason for rho_length + 1 is to include the last value of 400 and the same goes for theta_length + 1'''
    
    # Raster scan image
    #TASK 5 Write a set of nested for loops to raster scan through the edge image
    Ny = E.shape[0]
    Nx = E.shape[1]
    
    for y in range(Ny):
        for x in range(Nx):
            #TASK 6 add an if statment to check if we are at an edge
            if E[y,x] > 0:
                mask = np.zeros(0)
                rho_indices = np.zeros(0)# creates 2 empty arrays
                
                #print('theta_i: ')
                for theta_i in theta_accumulator:
                    #TASK 6.1 Perform the Hough transform by calculating the rho values for each of the theta values
                    rho = np.array(round(x*np.cos(theta_i) + y*np.sin(theta_i))) #function used to caluclate rho
                                
                    
                    rho_indices = np.append(rho_indices, (.5*rho + 200)) #adds all index value to array, .5*rho + 200 is sued to calculate the points index, valid or not
                   

                 # Some of the rho_indices will be out of range due to the fact that the rhos may go outside the bounds
                # of the range covered by the accumulator array. To cater for this we next compute a mask index array which 
                # is a boolean array of the same size as rho_indices where we store a value of True where there are 
                # valid values in the rho_indices array, and False otherwise. 
                # For further information see: https://numpy.org/doc/stable/user/basics.indexing.html#boolean-or-mask-index-arrays
                #TASK 6.3 use np.logical_and to compute a mask array for valid values in rho_indices
                
                #outside of angle loop
                #creates the mask array
                mask = np.logical_and(rho_indices >= 0, rho_indices <= 400)
                
                # We now create a linear range to convert the locations where the mask index array is True into corresponding
                # index in the theta dimension of the accumulator array
                
                #creates the theta array
                theta_indices = np.arange(0,mask.shape[0])
            

                # TASK 6.4 Add code below to use the rho_indices, theta_indices, and mask array's to index into Acc
                # and thereby increment all of the points on the sinusoid for the current edge point
                
                #converts the rho.indices contents to integers
                rho_indices = rho_indices.astype(int)
                            
                for i in range(mask.size):
                    #check to see if point is valid
                    if (mask[i] == True):
                        Acc[rho_indices[i], theta_indices[i]] = Acc[rho_indices[i], theta_indices[i]] + 1 #increments all the points in Acc
  
    #print('Acc after: ', Acc)
    
    return Acc

def nonmax(A, size = 1):
    M = np.zeros(A.shape)
    #print(A.shape[0]-size)
    for col in range(size, A.shape[1]-size):
        for row in range(size, A.shape[0]-size):
            #TASK 8: Add code to copy the value of A[row,col] through to M[row,col] iff it is greater than all of the the *other* values
            # in the neighbour from [row-size, col-size] to [row+size, col+size]

            check_bit = True
            #nested loop cycles through all values surrounding current point
            for col_inner in range(col - size, col + size):
                for row_inner in range(row - size, row + size):
                    if ((row != row_inner) and (col != col_inner)): #stops comparing it with itself
                        if (A[row, col] == A[row_inner, col_inner]): #if two points have the same value, this prioritises the first one found and the redues the other to 0
                            A[row_inner, col_inner] = 0; 
                        if (A[row, col] < A[row_inner, col_inner]):#if this point is smaller than any other surrounding point it will not be added
                            check_bit = False
            if(check_bit): #check to see if point is the highest in its surrounding area
                M[row,col] = A[row,col]
        
    return M

def extract_peaks(A, thresh, r_range, theta_range):
    ind = np.where(A>thresh)
    theta_list = np.arange(theta_range[0], theta_range[1], theta_range[2])
    r_list = np.arange(r_range[0], r_range[1], r_range[2])
    
    return (r_list[ind[0]], theta_list[ind[1]])


def drawline(img, r, theta):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*r
    y0 = b*r
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))

    cv2.line(img,(x1,y1),(x2,y2),(255,0,255),2)
    

def intersection(line1, line2):
    """Finds the intersection of two lines given in Hesse normal form.

    Returns closest integer pixel locations.
    See https://stackoverflow.com/a/383527/5087436
    """
    rho1, theta1 = line1
    rho2, theta2 = line2
    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])
    b = np.array([[rho1], [rho2]])
    try:
        x0, y0 = np.linalg.solve(A, b)
    except:
        print("Singular matrix -- You should check that the lines are not close to parallel"
              "e.g. check that lines are not within 10 degrees of each other")
        raise
    x0, y0 = int(np.round(x0)), int(np.round(y0))
    return [[x0, y0]]

    


#Task 1

Ic = cv2.imread('checkerboard.jpg')
print("Color image dimensions:", Ic.shape)


I = 0

I = cv2.imread('checkerboard.jpg', cv2.IMREAD_GRAYSCALE)
print("Grayscale image dimensions: ", I.shape)

#Task 2

plt.imshow(I)
plt.set_cmap('gray')
plt.show()




#Task 3

#Define a set of Sobel kernels to compute the gradient in the X-direction and Y-direction
xSobel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
ySobel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])

#TASK 3.1 use cv2.filter2D to estimate the gradients in the X and Y-directions
gradients_x = cv2.filter2D(I, cv2.CV_64F, xSobel)

gradients_y = cv2.filter2D(I, cv2.CV_64F, ySobel)

G = np.sqrt(np.add(np.square(gradients_x), np.square(gradients_y)))# G = sqrt((gradients_x)^2 + (gradients_y)^2)

plt.imshow(G)
plt.set_cmap('gray')
plt.show()




# Here we create an image of equivalent size to G of type uint8 intialised to 0

E = np.zeros(G.shape, dtype='uint8')

#TASK 3.3 Compute an edge-map from G: for each pixel in G above a threshold of 20 set the corresponding pixel in E to 1

G = G.astype(int)

counter_x = 0
counter_y = 0

#cycles through all the points in the image G

        
for x in G:
    for y in x:
        if (y > 20): #if the curent point is greater than 20 we set the same coordinate in E to 1, else it remains as 0
            E[counter_x][counter_y] = 1
        counter_y = counter_y + 1
    counter_x = counter_x + 1
    counter_y = 0


E = skeletonize(E)
plt.imshow(E)
plt.show()



rho_range = [-400, 400, 2]
theta_range = [0, np.pi, (np.pi)/180]

A = Hough(E, rho_range, theta_range)

plt.imshow(A)
plt.set_cmap('hot')
plt.gca().set_aspect(A.shape[1]/A.shape[0])
plt.show()



#this calculates all the max points by comparing them to the surrounding points
A = nonmax(A,5)
plt.imshow(A)
plt.gca().set_aspect(A.shape[1]/A.shape[0])
plt.show()



thresh = 100 #threshold had to be lowered to detect one line

#TASK 9: Use the extract_peaks function to find all peaks greater than a value of 170
rs, ps = extract_peaks(A, thresh, rho_range, theta_range)

#print('rs: ', rs)
#print('ps: ', ps)

D = Ic.copy()

#TASK 10: Add code to use drawline to visualise each detected line on the image D
# print(rs.shape[0])

for i in range(rs.shape[0]):
    drawline(D, rs[i], ps[i]) #draws lines for every peak point


# show the resultant lines
plt.imshow(D)
plt.show()

#TASK 11: Add code here that uses the intersection function to compute the intersection
#between each pair of detected lines, where the angle between the lines is greater than
#10 degree (i.e. np.pi/18 radians). Each intersection should be appended to the 
#intersections list

#print('rs.shape[0]/2: ', rs.shape[0]/2)

intersections = np.empty((0,2), int) #creates and empty array with 2 columns to store intersections

#this nested loop cycles through all lines and all the lines that they come in contact with
for vertical_lines in range(int(rs.shape[0]/2)):
        for horizontal_lines in range(int(rs.shape[0]/2), int(rs.shape[0])):
            intersections = np.vstack([intersections, intersection([rs[vertical_lines], ps[vertical_lines]], [rs[horizontal_lines], ps[horizontal_lines]])]) #staks result in intersections array

D = Ic.copy()
i = 0
for i in intersections:
    cv2.circle(D,(i[0],i[1]),4,(255,0,0),thickness=3) #i[0][0] changed to i[0] because of how i designed intersections np.array

plt.imshow(D)
plt.show()
