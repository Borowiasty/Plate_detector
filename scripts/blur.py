import cv2 

img = cv2.imread('image_path', cv2.IMREAD_GRAYSCALE)
laplacian = cv2.Laplacian(img, cv2.CV_64F)
laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
print(round(laplacian_var, 2))

cv2.imshow('Image',img)
cv2.imshow('Laplacian',laplacian)
cv2.waitKey(0)
cv2.destroyAllWindows()
