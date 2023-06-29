import cv2
import pytesseract
from numpy import ndarray

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

# funcion para detetctar las placas
def  deteccion(image:ndarray)->tuple[str,ndarray] or tuple[None,None]: 
  placa = [] # variable para guardar la placa

  umbral = 70 # umbral para binarizar la imagen

  copy = image.copy() # copia de la imagen

  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # obtener la imagen en escala de grises

  gray = cv2.blur(gray,(3,3)) # aplicar un filtro de desenfoque

  canny = cv2.Canny(gray,50,200) # aplicar el detector de bordes de canny

  canny = cv2.dilate(canny,None,iterations=1) # dilatar la imagen


  cnts,_ = cv2.findContours(canny,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE) # encontrar los contornos

  cv2.drawContours(image,cnts,-1,(0,255,0),2) # dibujar los contornos en la imagen original


  for c in cnts: # recorrer los contornos
    area = cv2.contourArea(c) # calcular el area del contorno
    x,y,w,h = cv2.boundingRect(c) # obtener las coordenadas del contorno
    epsilon = 0.09*cv2.arcLength(c,True) # calcular el perimetro del contorno
    approx = cv2.approxPolyDP(c,epsilon,True) # aproximar el contorno a un poligono

    if len(approx)>=2 and area>6000  and area<20000: # si el area es mayor a 6000 y menor a 15000
      #print('area=',area,'approx=',len(approx))

      cv2.drawContours(image,[approx],0,(0,255,0),3) # dibujar el contorno aproximado

      aspect_ratio = float(w)/h # calcular el aspect ratio
      cv2.destroyAllWindows()
      if aspect_ratio>2 and aspect_ratio<2.7: # si el aspect ratio es mayor a 2 y menor a 2.7
        #print('aspect_ratio=',aspect_ratio) 
        placa = gray[y:y+h,x:x+w] # obtener la placa de la imagen en escala de grises
        placa = cv2.resize(placa,(200,100)) # redimensionar la placa
        #print('PLACA: ',placa.shape)

        placa = placa[20:95,:] # recortar la placa
        #binarizar la placa
        placa[placa>=umbral]=255 
        placa[placa<umbral]=0
        #cv2.imshow('PLACA',placa)
        
        text = pytesseract.image_to_string(placa,config='--psm 7') # obtener el texto de la placa
        # quitar espacios en blanco y limitar el texto a 9 caracteres
        text = text.replace(' ','')
        if len(text)>=9: text = text[:9] 
        print('PLACA: ',text)
        #cv2.waitKey(0)
        #cv2.moveWindow('PLACA',780,10)
        cv2.rectangle(copy,(x,y),(x+w,y+h),(0,255,0),3) # dibujar el rectangulo de la placa
        cv2.putText(copy,text,(x-20,y-10),1,2.2,(0,0,255),3) # escribir el texto de la placa
        

        return (text,copy) # retornar el texto de la placa y la imagen original si el texto tiene 9 caracteres

  return (None,None) # retornar None si no se detecta una placa

if __name__ == '__main__':
  cam = cv2.VideoCapture(0)
  while True:
    ret,frame = cam.read()
    if ret:
      cv2.imshow('Image',frame.copy())
      placa,frame = deteccion(frame)
      
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break
